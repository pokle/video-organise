# Video Organise CLI Specification

## Overview
A Python CLI tool that organizes Insta360 files from a source directory into date-based folders.

## Requirements
- **File types**: Only Insta360 files (`*.insv`, `*.insp`, `*.lrv`, `fileinfo_list.list`) are organized; all other files are ignored.
- **Recursion**: Scan source directory recursively for files.
- **Date source**: File creation/modification date from filesystem (no metadata parsing)
- **File action**: Copy files (or move with `--move`), skip if already exists AND same size
- **Default mode**: Dry-run (preview only)
- **Output structure**: `{dest}/YYYY-MM-DD/insta360/{original-filename}`

## CLI Interface

```
video-organise <source-directory> <destination-directory> [--approve] [--move]
```

### Arguments
- `source_directory`: Path (must exist, must be directory)
- `destination_directory`: Path (must exist, must be directory)

### Options
- `--approve`: Actually perform the copy/move (default is dry-run/preview mode)
- `--move`: Move files instead of copying them

## Core Functions

### `get_file_date(file_path: Path) -> date`
Get creation date from filesystem using `st_birthtime` on macOS, fall back to `st_mtime`.

### `should_copy(src: Path, dest: Path) -> bool`
Returns True if destination doesn't exist OR exists but has different size.

## Main Logic Flow

1. Scan source directory for ALL files (recursive)
2. For each file:
   - Get file creation date from filesystem
   - Determine destination: `{dest}/{YYYY-MM-DD}/insta360/{original-filename}`
   - Check if file exists at destination with same size -> skip
   - If dry-run: print what would be copied
   - If --approve: create directories and copy file
3. Print summary (files to copy, files skipped, total size)

## Usage

```bash
# Preview what will be copied (default - dry run)
video-organise /Volumes/SDCARD /archive/videos

# Actually copy files
video-organise --approve /Volumes/SDCARD /archive/videos

# Move files instead of copying
video-organise --approve --move /Volumes/SDCARD /archive/videos

# Or run via uv
uv run video-organise /Volumes/SDCARD /archive/videos
```

---

## Fix Structure Script

A separate script to fix existing archives where Insta360 files are not in the correct `insta360/` subfolder.

### CLI Interface

```
fix-structure <source-directory>
```

### Output
Generates a shell script (to stdout) with `mkdir` and `mv` commands to move non-compliant files.

Output includes:
- `#!/usr/bin/env bash` shebang
- `set -x` for verbose execution
- `mkdir -p` commands for creating `insta360/` subfolders
- `mv` commands for moving files

### Warnings
- Warns (to stderr) about non-compliant folders in root that don't match the date pattern `YYYY-MM-DD` or `YYYY-MM-DD[-/ ]project-name`

### Date Folder Pattern
Matches folders named:
- `YYYY-MM-DD` (e.g., `2024-01-15`)
- `YYYY-MM-DD-suffix` (e.g., `2024-01-15-vacation`)
- `YYYY-MM-DD suffix` (e.g., `2024-01-15 Trip to Paris`)

### Usage

```bash
# Preview commands (outputs to stdout)
uv run python fix_structure.py /archive/videos

# Execute the generated commands
uv run python fix_structure.py /archive/videos | bash
```
