# Video Organise CLI Specification

## Overview
A Python CLI tool that organizes Insta360 files from a source directory into date-based folders.

## Requirements
- **File types**: Only Insta360 files (`*.insv`, `*.insp`, `*.lrv`, `fileinfo_list.list`) are organized; all other files are ignored.
- **Recursion**: Scan source directory recursively for files.
- **Excluded folders**: Files in `MISC` folders are ignored (these contain Insta360 metadata, not video data).
- **Duplicate detection**: Errors if the same filename exists in multiple source folders (to prevent data loss).
- **Date source**: Extract from filename pattern (e.g., `VID_20241011_...`), fall back to filesystem creation date
- **File action**: Copy files (or move with `--move`), skip if already exists AND same size
- **Default mode**: Dry-run (preview only)
- **Output structure**: `{dest}/YYYY-MM-DD/insta360/{original-filename}`
- **Date folder matching**: Uses existing folder if one starting with `YYYY-MM-DD` exists (e.g., `2024-01-15 Project Name`). Errors if multiple folders match the same date prefix.

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

### `get_date_from_filename(file_path: Path) -> date | None`
Extract date from Insta360 filename patterns:
- `VID_YYYYMMDD_HHMMSS_...` (video)
- `LRV_YYYYMMDD_HHMMSS_...` (low-res video)
- `IMG_YYYYMMDD_HHMMSS_...` (image)

Returns `None` if filename doesn't match pattern.

### `get_file_date(file_path: Path) -> date`
Get date for file, preferring filename over filesystem. Falls back to `st_birthtime` on macOS or `st_mtime`.

### `should_copy(src: Path, dest: Path) -> bool`
Returns True if destination doesn't exist OR exists but has different size.

## Main Logic Flow

1. Scan source directory for ALL files (recursive)
2. For each file:
   - Extract date from filename pattern, or fall back to filesystem date
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
