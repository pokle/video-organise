# Video Organise

A CLI tool to organize Insta360 files into date-based folders.

See [SPEC.md](SPEC.md) for full details.

## Installation

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/pokle/video-organise
cd video-organise
uv sync
```

## Usage

```bash
# Preview what will be copied (default - dry run)
uv run video-organise /Volumes/SDCARD /archive/videos

# Actually copy files
uv run video-organise --approve /Volumes/SDCARD /archive/videos
```

## Development

```bash
uv run pytest
```
