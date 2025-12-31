"""
Video Organise - Organize Insta360 files into date-based folders.

Copies Insta360 files (.insv, .insp, .lrv, fileinfo_list.list) from a source
directory into destination folders organized by date extracted from filename:
{dest}/YYYY-MM-DD/insta360/{filename}

All other file types are ignored.
"""

import re
import shutil
from datetime import date
from pathlib import Path

import typer

app = typer.Typer(help="Organize Insta360 files into date-based folders.")

# Insta360 file extensions
INSTA360_EXTENSIONS = {".insv", ".insp", ".lrv"}

# Insta360 specific filenames
INSTA360_FILENAMES = {"fileinfo_list.list"}


def is_insta360_file(file_path: Path) -> bool:
    """Check if file is an Insta360 file based on extension or filename."""
    return file_path.suffix.lower() in INSTA360_EXTENSIONS or file_path.name in INSTA360_FILENAMES


def is_in_excluded_folder(file_path: Path) -> bool:
    """Check if file is in an excluded folder (e.g., MISC)."""
    return "MISC" in file_path.parts


# Pattern to extract date from Insta360 filenames like:
# VID_20241011_185020_00_003.insv
# LRV_20240926_150746_01_003.lrv
# IMG_20240915_133402_00_027.insp
FILENAME_DATE_PATTERN = re.compile(r"^(?:VID|LRV|IMG)_(\d{4})(\d{2})(\d{2})_")


def get_date_from_filename(file_path: Path) -> date | None:
    """Extract date from Insta360 filename pattern.

    Returns None if filename doesn't match expected pattern.
    """
    match = FILENAME_DATE_PATTERN.match(file_path.name)
    if match:
        year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
        try:
            return date(year, month, day)
        except ValueError:
            return None
    return None


def get_file_date_from_filesystem(file_path: Path) -> date:
    """Get creation date from filesystem.

    Uses st_birthtime on macOS, falls back to st_mtime.
    """
    stat = file_path.stat()
    # st_birthtime is available on macOS
    timestamp = getattr(stat, "st_birthtime", None) or stat.st_mtime
    return date.fromtimestamp(timestamp)


def get_file_date(file_path: Path) -> date:
    """Get date for file, preferring filename over filesystem.

    First tries to extract date from filename pattern (e.g., VID_20241011_...).
    Falls back to filesystem creation date if no date in filename.
    """
    filename_date = get_date_from_filename(file_path)
    if filename_date:
        return filename_date
    return get_file_date_from_filesystem(file_path)


def should_copy(src: Path, dest: Path) -> bool:
    """Check if file should be copied.

    Returns False if source and destination are the same file.
    Returns True if destination doesn't exist or has different size.
    """
    # Skip if source and destination are the same file
    if src.resolve() == dest.resolve():
        return False
    if not dest.exists():
        return True
    return src.stat().st_size != dest.stat().st_size


def format_size(size_bytes: int) -> str:
    """Format bytes as human-readable string."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} PB"


def find_date_folder(dest_dir: Path, date_str: str) -> Path | list[Path]:
    """Find existing date folder or return default path.

    Looks for folders starting with YYYY-MM-DD (with optional suffix like ' Project Name').
    Returns:
    - The matching folder if exactly one exists
    - The default YYYY-MM-DD path if none exists
    - A list of matching folders if multiple exist (error case)
    """
    matches: list[Path] = []
    if dest_dir.exists():
        for folder in dest_dir.iterdir():
            if folder.is_dir() and folder.name.startswith(date_str):
                matches.append(folder)

    if len(matches) == 0:
        return dest_dir / date_str
    elif len(matches) == 1:
        return matches[0]
    else:
        return matches


@app.command()
def main(
    source_directory: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        help="Source directory containing Insta360 files to organize.",
    ),
    destination_directory: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        writable=True,
        resolve_path=True,
        help="Destination directory for organized files.",
    ),
    approve: bool = typer.Option(
        False,
        "--approve",
        help="Actually copy/move files. Without this flag, only shows what would be done.",
    ),
    move: bool = typer.Option(
        False,
        "--move",
        help="Move files instead of copying them.",
    ),
) -> None:
    """Organize Insta360 files from source into date-based folders in destination.

    Only Insta360 files (.insv, .insp, .lrv, fileinfo_list.list) are processed.
    All other files are ignored.

    Files are copied to: {destination}/YYYY-MM-DD/insta360/{original-filename}

    By default, runs in dry-run mode showing what would be copied.
    Use --approve to actually copy files.
    """
    # Collect all Insta360 files recursively (excluding MISC folder)
    files = [
        f for f in source_directory.rglob("*")
        if f.is_file() and is_insta360_file(f) and not is_in_excluded_folder(f)
    ]

    if not files:
        typer.echo("No Insta360 files found in source directory.")
        raise typer.Exit()

    # Check for duplicate filenames
    filenames: dict[str, list[Path]] = {}
    for f in files:
        filenames.setdefault(f.name, []).append(f)

    duplicates = {name: paths for name, paths in filenames.items() if len(paths) > 1}
    if duplicates:
        typer.echo("Error: Duplicate filenames found:", err=True)
        for name, paths in sorted(duplicates.items()):
            typer.echo(f"  {name}:", err=True)
            for p in paths:
                typer.echo(f"    - {p}", err=True)
        raise typer.Exit(1)

    # reason is: "new" (dest missing) or "size_mismatch" (with src_size, dest_size)
    to_copy: list[tuple[Path, Path, str]] = []
    skipped_same_file: list[Path] = []
    skipped_exists: list[Path] = []
    total_size = 0

    # Track dates with multiple matching folders (error case)
    ambiguous_dates: dict[str, list[Path]] = {}

    for src_file in files:
        file_date = get_file_date(src_file)
        date_str = file_date.strftime("%Y-%m-%d")
        date_folder_result = find_date_folder(destination_directory, date_str)

        # Check for ambiguous date folders
        if isinstance(date_folder_result, list):
            if date_str not in ambiguous_dates:
                ambiguous_dates[date_str] = date_folder_result
            continue

        date_folder = date_folder_result
        dest_path = date_folder / "insta360" / src_file.name

        # Check if source and destination are the same file
        if src_file.resolve() == dest_path.resolve():
            skipped_same_file.append(src_file)
        elif not dest_path.exists():
            to_copy.append((src_file, dest_path, "new"))
            total_size += src_file.stat().st_size
        elif src_file.stat().st_size != dest_path.stat().st_size:
            src_size = src_file.stat().st_size
            dest_size = dest_path.stat().st_size
            reason = f"size_mismatch:{src_size}:{dest_size}"
            to_copy.append((src_file, dest_path, reason))
            total_size += src_size
        else:
            skipped_exists.append(src_file)

    # Error if any dates have multiple matching destination folders
    if ambiguous_dates:
        typer.echo("Error: Multiple destination folders found for same date:", err=True)
        for date_str, folders in sorted(ambiguous_dates.items()):
            typer.echo(f"  {date_str}:", err=True)
            for folder in sorted(folders):
                typer.echo(f"    - {folder.name}", err=True)
        raise typer.Exit(1)

    # Print summary
    action = "Moving" if move else "Copying"
    if approve:
        typer.echo(f"{action} {len(to_copy)} files ({format_size(total_size)})")
    else:
        typer.echo(f"[DRY RUN] Would {'move' if move else 'copy'} {len(to_copy)} files ({format_size(total_size)})")

    if skipped_same_file:
        typer.echo(f"Skipping {len(skipped_same_file)} files (already in correct location)")
    if skipped_exists:
        typer.echo(f"Skipping {len(skipped_exists)} files (already exist with same size)")

    typer.echo("")

    # Process files
    for src_file, dest_path, reason in to_copy:
        if approve:
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            if move:
                shutil.move(src_file, dest_path)
                typer.echo(f"Moved: {src_file} -> {dest_path}")
            else:
                shutil.copy2(src_file, dest_path)
                typer.echo(f"Copied: {src_file} -> {dest_path}")
        else:
            # Explain why the file would be copied
            if reason == "new":
                reason_text = "(dest missing)"
            else:
                # reason is "size_mismatch:src_size:dest_size"
                _, src_size, dest_size = reason.split(":")
                reason_text = f"(size mismatch: src {format_size(int(src_size))} vs dest {format_size(int(dest_size))})"
            typer.echo(f"Would {'move' if move else 'copy'}: {src_file} -> {dest_path} {reason_text}")

    if not approve and to_copy:
        typer.echo("")
        typer.echo(f"Run with --approve to {'move' if move else 'copy'} files.")


if __name__ == "__main__":
    app()
