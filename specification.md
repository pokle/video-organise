# Video Organise CLI Specification

## Overview
A Python CLI tool that organizes ALL files from a source directory into date-based folders.

## Requirements
- **File types**: ALL files (not just videos - supports Insta360 and other proprietary formats)
- **Date source**: File creation/modification date from filesystem (no metadata parsing)
- **File action**: Copy files, skip if already exists AND same size
- **Default mode**: Dry-run (preview only)
- **Output structure**: `{dest}/YYYY-MM-DD/raw/{original-filename}`

## CLI Interface

```
video-organise <source-directory> <destination-directory> [--approve]
```

### Arguments
- `source_directory`: Path (must exist, must be directory)
- `destination_directory`: Path (must exist, must be directory)

### Options
- `--approve`: Actually perform the copy (default is dry-run/preview mode)

## Core Functions

### `get_file_date(file_path: Path) -> date`
Get creation date from filesystem using `st_birthtime` on macOS, fall back to `st_mtime`.

### `should_copy(src: Path, dest: Path) -> bool`
Returns True if destination doesn't exist OR exists but has different size.

## Main Logic Flow

1. Scan source directory for ALL files (recursive)
2. For each file:
   - Get file creation date from filesystem
   - Determine destination: `{dest}/{YYYY-MM-DD}/raw/{original-filename}`
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

# Or run via uv
uv run video-organise /Volumes/SDCARD /archive/videos
```
