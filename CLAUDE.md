# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Video Organise is a CLI tool that organizes files into folders based on their filesystem creation date.

It looks for files with the following extensions:
- `insv`
- `insp`
- `lrv`

It ignores all other file types.

## Output Structure

Files are organized into:
```
/YYYY-MM-DD[-project-name]/insta360/
```

Where `YYYY-MM-DD` is extracted from the file's creation date and `project-name` is an optional suffix for manual editing after organization.

## CLI Interface

```
video-organise [options] <source-directory> <destination-directory>
```

- `source-directory`: Input location (typically SD card or external drive)
- `destination-directory`: Archive location where organized folders are created
- `--approve`: Actually copy files (default is dry-run mode)

## Tooling
- Python 3.12+
- uv for project and dependency management
- pytest for testing (dev dependency)
- typer for CLI interface

## Commands

```bash
# Run the CLI
uv run video-organise <source> <dest>

# Run tests
uv run pytest

# Install as editable for development
uv pip install -e .
```
