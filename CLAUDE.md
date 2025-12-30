# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Video Organise is a CLI tool that organizes video files into folders based on their metadata (creation date).

## Output Structure

Files are organized into:
```
/YYYY-MM-DD[-project-name]/raw/
```

Where `YYYY-MM-DD` is extracted from video metadata and `project-name` is an optional suffix for manual editing after organization.

## CLI Interface

```
video-organise [options] <source-directory> <destination-directory>
```

- `source-directory`: Input location (typically SD card or external drive)
- `destination-directory`: Archive location where organized folders are created

## Tooling
- Python 3.x
- Always read the documentation with context7 to understand dependencies and tools before using them.
- uv for dependencies (Executable Script with Shebang and Inline Dependency Declaration).
- pytest for testing. Every feature must be tested.
- typer for CLI interface.
