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

    Returns True if destination doesn't exist or has different size.
    """
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
    # Collect all Insta360 files recursively
    files = [f for f in source_directory.rglob("*") if f.is_file() and is_insta360_file(f)]

    if not files:
        typer.echo("No Insta360 files found in source directory.")
        raise typer.Exit()

    to_copy: list[tuple[Path, Path]] = []
    skipped: list[Path] = []
    total_size = 0

    for src_file in files:
        file_date = get_file_date(src_file)
        date_folder = file_date.strftime("%Y-%m-%d")
        dest_path = destination_directory / date_folder / "insta360" / src_file.name

        if should_copy(src_file, dest_path):
            to_copy.append((src_file, dest_path))
            total_size += src_file.stat().st_size
        else:
            skipped.append(src_file)

    # Print summary
    action = "Moving" if move else "Copying"
    if approve:
        typer.echo(f"{action} {len(to_copy)} files ({format_size(total_size)})")
    else:
        typer.echo(f"[DRY RUN] Would {'move' if move else 'copy'} {len(to_copy)} files ({format_size(total_size)})")

    if skipped:
        typer.echo(f"Skipping {len(skipped)} files (already exist with same size)")

    typer.echo("")

    # Process files
    for src_file, dest_path in to_copy:
        if approve:
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            if move:
                shutil.move(src_file, dest_path)
                typer.echo(f"Moved: {src_file} -> {dest_path}")
            else:
                shutil.copy2(src_file, dest_path)
                typer.echo(f"Copied: {src_file} -> {dest_path}")
        else:
            typer.echo(f"Would {'move' if move else 'copy'}: {src_file} -> {dest_path}")

    if not approve and to_copy:
        typer.echo("")
        typer.echo(f"Run with --approve to {'move' if move else 'copy'} files.")


if __name__ == "__main__":
    app()
