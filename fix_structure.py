"""
Fix Structure - Generate shell commands to fix non-compliant Insta360 file organization.

Finds Insta360 files (.insv, .insp, .lrv) that are not in the insta360/ subfolder
within date folders and outputs shell commands to move them.

Non-Insta360 files are ignored.
"""

from pathlib import Path
import re

import typer

app = typer.Typer(help="Generate shell commands to fix Insta360 file organization structure.")

# Date folder pattern: YYYY-MM-DD optionally followed by anything (space, hyphen, etc.)
DATE_FOLDER_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}([ -].*)?$")

# Insta360 file extensions
INSTA360_EXTENSIONS = {".insv", ".insp", ".lrv"}


def is_insta360_file(file_path: Path) -> bool:
    """Check if file is an Insta360 file based on extension."""
    return file_path.suffix.lower() in INSTA360_EXTENSIONS


def is_date_folder(folder: Path) -> bool:
    """Check if a folder name matches the date pattern."""
    return bool(DATE_FOLDER_PATTERN.match(folder.name))


def get_date_folder(file_path: Path, base_dir: Path) -> Path | None:
    """Find the date folder that contains this file."""
    rel_path = file_path.relative_to(base_dir)
    parts = rel_path.parts

    if parts:
        first_part = base_dir / parts[0]
        if is_date_folder(first_part):
            return first_part
    return None


def is_compliant(file_path: Path, date_folder: Path) -> bool:
    """Check if a file is in the correct location (insta360/ subfolder)."""
    expected_parent = date_folder / "insta360"
    return file_path.parent == expected_parent


def shell_quote(path: Path) -> str:
    """Quote a path for shell usage."""
    return f'"{path}"'


@app.command()
def main(
    source_directory: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        help="Source directory containing date folders to fix.",
    ),
) -> None:
    """Generate shell commands to fix non-compliant Insta360 file organization.

    Scans date folders (YYYY-MM-DD or YYYY-MM-DD-project-name) and outputs
    mkdir and mv commands to move Insta360 files into the insta360/ subfolder.

    Only Insta360 files (.insv, .insp, .lrv) are processed. All other files are ignored.
    """
    # Find all Insta360 files in date folders
    files = [f for f in source_directory.rglob("*") if f.is_file() and is_insta360_file(f)]

    if not files:
        typer.echo("# No Insta360 files found in source directory.", err=True)
        raise typer.Exit()

    # Track which directories need to be created
    dirs_to_create: set[Path] = set()
    moves: list[tuple[Path, Path]] = []

    for file_path in files:
        date_folder = get_date_folder(file_path, source_directory)

        if date_folder is None:
            # File is not in a date folder, skip
            continue

        if is_compliant(file_path, date_folder):
            # File is already in the right place
            continue

        # File needs to be moved
        target_dir = date_folder / "insta360"
        target_path = target_dir / file_path.name

        dirs_to_create.add(target_dir)
        moves.append((file_path, target_path))

    if not moves:
        typer.echo("# All Insta360 files are already compliant.", err=True)
        raise typer.Exit()

    # Output mkdir commands
    for dir_path in sorted(dirs_to_create):
        typer.echo(f"mkdir -p {shell_quote(dir_path)}")

    typer.echo("")

    # Output mv commands
    for src, dest in sorted(moves):
        typer.echo(f"mv {shell_quote(src)} {shell_quote(dest)}")

    typer.echo("")
    typer.echo(f"# {len(moves)} files to move", err=True)


if __name__ == "__main__":
    app()
