# Video Organise

A simple tool to organise your files into folders based on their creation date.

## Organisation Structure

The tool organises files into a directory structure based on the following hierarchy:

```
/YYYY-MM-DD[-project-name]/insta360/
```

- `YYYY-MM-DD`: The date the file was created.
- `project-name`: An optional project name that can be included in the folder name. Manually edit this part after the date if desired.
- `insta360`: A subfolder where the original files are stored.

## Features
- Automatically creates folders based on file creation date.
- Copies ALL files (videos, metadata, proprietary formats like Insta360).
- Allows for manual addition of project names to the folder structure.
- Dry-run mode by default - preview before copying.
- Skips files that already exist with the same size.

## Installation

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
# Clone the repository
git clone <repo-url>
cd video-organise

# Install dependencies
uv sync
```

## Usage

```bash
# Preview what will be copied (default - dry run)
uv run video-organise /Volumes/SDCARD /archive/videos

# Actually copy files
uv run video-organise --approve /Volumes/SDCARD /archive/videos
```

- `source-directory`: The directory containing the files to be organised. This is usually an SD card or external drive.
- `destination-directory`: The directory where the organised folders will be created. This is usually the archive location.
- `--approve`: Actually perform the copy. Without this flag, only shows what would be done.

## Development

```bash
# Run tests
uv run pytest

# Run tests with verbose output
uv run pytest -v
```
