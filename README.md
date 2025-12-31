# Video Organise

A CLI tool to organize Insta360 files into date-based folders.

See [SPEC.md](SPEC.md) for full details.

## Installation

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

Run latest stable version directly:

```bash
uvx video-organise <source> <dest>
```

Or clone the repo and install latest development version:
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

## Publishing a new version to PyPI

```bash
uv version --bump patch  # or 'minor' or 'major'
git commit -am "Bump version"
git tag X.Y.Z         # replace X.Y.Z with the new version
git push --tags
```

Then create a [new release with the same version tag on GitHub](https://github.com/pokle/video-organise/releases/new) to trigger the PyPI publish workflow.


