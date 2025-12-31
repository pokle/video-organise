"""Tests for video_organise.py"""

from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from video_organise import app, get_file_date, get_date_from_filename, should_copy, format_size, is_insta360_file

runner = CliRunner()


class TestGetDateFromFilename:
    """Tests for get_date_from_filename function."""

    def test_vid_filename(self, tmp_path: Path) -> None:
        """Should extract date from VID_ prefixed filename."""
        test_file = tmp_path / "VID_20241011_185020_00_003.insv"
        result = get_date_from_filename(test_file)
        assert result == date(2024, 10, 11)

    def test_lrv_filename(self, tmp_path: Path) -> None:
        """Should extract date from LRV_ prefixed filename."""
        test_file = tmp_path / "LRV_20240926_150746_01_003.lrv"
        result = get_date_from_filename(test_file)
        assert result == date(2024, 9, 26)

    def test_img_filename(self, tmp_path: Path) -> None:
        """Should extract date from IMG_ prefixed filename."""
        test_file = tmp_path / "IMG_20240915_133402_00_027.insp"
        result = get_date_from_filename(test_file)
        assert result == date(2024, 9, 15)

    def test_no_date_in_filename(self, tmp_path: Path) -> None:
        """Should return None for files without date pattern."""
        test_file = tmp_path / "random_file.insv"
        result = get_date_from_filename(test_file)
        assert result is None

    def test_fileinfo_list(self, tmp_path: Path) -> None:
        """Should return None for fileinfo_list.list."""
        test_file = tmp_path / "fileinfo_list.list"
        result = get_date_from_filename(test_file)
        assert result is None


class TestGetFileDate:
    """Tests for get_file_date function."""

    def test_returns_date_object(self, tmp_path: Path) -> None:
        """Should return a date object."""
        test_file = tmp_path / "test.insv"
        test_file.write_text("content")

        result = get_file_date(test_file)

        assert isinstance(result, date)

    def test_returns_filesystem_date_for_generic_filename(self, tmp_path: Path) -> None:
        """Should return today's date for file without date in filename."""
        test_file = tmp_path / "test.insv"
        test_file.write_text("content")

        result = get_file_date(test_file)

        assert result == date.today()

    def test_prefers_filename_date_over_filesystem(self, tmp_path: Path) -> None:
        """Should use date from filename even if filesystem date differs."""
        test_file = tmp_path / "VID_20230505_120000_00_001.insv"
        test_file.write_text("content")

        result = get_file_date(test_file)

        # Should use filename date, not today's filesystem date
        assert result == date(2023, 5, 5)


class TestShouldCopy:
    """Tests for should_copy function."""

    def test_returns_true_when_dest_not_exists(self, tmp_path: Path) -> None:
        """Should return True when destination doesn't exist."""
        src = tmp_path / "src.insv"
        src.write_text("content")
        dest = tmp_path / "dest.insv"

        assert should_copy(src, dest) is True

    def test_returns_false_when_same_size(self, tmp_path: Path) -> None:
        """Should return False when destination exists with same size."""
        src = tmp_path / "src.insv"
        src.write_text("content")
        dest = tmp_path / "dest.insv"
        dest.write_text("content")

        assert should_copy(src, dest) is False

    def test_returns_true_when_different_size(self, tmp_path: Path) -> None:
        """Should return True when destination exists with different size."""
        src = tmp_path / "src.insv"
        src.write_text("longer content here")
        dest = tmp_path / "dest.insv"
        dest.write_text("short")

        assert should_copy(src, dest) is True

    def test_returns_false_when_same_file(self, tmp_path: Path) -> None:
        """Should return False when source and destination are the same file."""
        src = tmp_path / "video.insv"
        src.write_text("content")

        # Same path should not be copied
        assert should_copy(src, src) is False

    def test_returns_false_when_same_file_via_symlink(self, tmp_path: Path) -> None:
        """Should return False when paths resolve to the same file."""
        src = tmp_path / "video.insv"
        src.write_text("content")
        link = tmp_path / "link.insv"
        link.symlink_to(src)

        # Link resolves to same file, should not be copied
        assert should_copy(src, link) is False



class TestFormatSize:
    """Tests for format_size function."""

    def test_bytes(self) -> None:
        assert format_size(500) == "500.0 B"

    def test_kilobytes(self) -> None:
        assert format_size(1024) == "1.0 KB"

    def test_megabytes(self) -> None:
        assert format_size(1024 * 1024) == "1.0 MB"

    def test_gigabytes(self) -> None:
        assert format_size(1024 * 1024 * 1024) == "1.0 GB"


class TestIsInsta360File:
    """Tests for is_insta360_file function."""

    def test_insv_is_insta360(self, tmp_path: Path) -> None:
        assert is_insta360_file(tmp_path / "video.insv") is True

    def test_insp_is_insta360(self, tmp_path: Path) -> None:
        assert is_insta360_file(tmp_path / "photo.insp") is True

    def test_lrv_is_insta360(self, tmp_path: Path) -> None:
        assert is_insta360_file(tmp_path / "preview.lrv") is True

    def test_uppercase_extensions(self, tmp_path: Path) -> None:
        assert is_insta360_file(tmp_path / "video.INSV") is True
        assert is_insta360_file(tmp_path / "photo.INSP") is True
        assert is_insta360_file(tmp_path / "preview.LRV") is True

    def test_mp4_is_not_insta360(self, tmp_path: Path) -> None:
        assert is_insta360_file(tmp_path / "video.mp4") is False

    def test_json_is_not_insta360(self, tmp_path: Path) -> None:
        assert is_insta360_file(tmp_path / "metadata.json") is False

    def test_mov_is_not_insta360(self, tmp_path: Path) -> None:
        assert is_insta360_file(tmp_path / "video.mov") is False

    def test_fileinfo_list_is_insta360(self, tmp_path: Path) -> None:
        assert is_insta360_file(tmp_path / "fileinfo_list.list") is True

    def test_other_list_file_is_not_insta360(self, tmp_path: Path) -> None:
        assert is_insta360_file(tmp_path / "other.list") is False


class TestCLI:
    """Tests for CLI interface."""

    def test_dry_run_default(self, tmp_path: Path) -> None:
        """Default mode should be dry-run (no files copied)."""
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        dest_dir = tmp_path / "dest"
        dest_dir.mkdir()

        test_file = src_dir / "video.insv"
        test_file.write_text("video content")

        result = runner.invoke(app, [str(src_dir), str(dest_dir)])

        assert result.exit_code == 0
        assert "[DRY RUN]" in result.output
        assert "Would copy" in result.output
        # File should NOT be copied
        assert not (dest_dir / date.today().strftime("%Y-%m-%d") / "insta360" / "video.insv").exists()

    def test_approve_copies_files(self, tmp_path: Path) -> None:
        """With --approve, files should be copied."""
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        dest_dir = tmp_path / "dest"
        dest_dir.mkdir()

        test_file = src_dir / "video.insv"
        test_file.write_text("video content")

        result = runner.invoke(app, [str(src_dir), str(dest_dir), "--approve"])

        assert result.exit_code == 0
        assert "Copied:" in result.output

        # File should be copied (source still exists)
        expected_dest = dest_dir / date.today().strftime("%Y-%m-%d") / "insta360" / "video.insv"
        assert expected_dest.exists()
        assert expected_dest.read_text() == "video content"
        assert test_file.exists()  # Source file still exists after copy

    def test_move_flag_moves_files(self, tmp_path: Path) -> None:
        """With --approve --move, files should be moved."""
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        dest_dir = tmp_path / "dest"
        dest_dir.mkdir()

        test_file = src_dir / "video.insv"
        test_file.write_text("video content")

        result = runner.invoke(app, [str(src_dir), str(dest_dir), "--approve", "--move"])

        assert result.exit_code == 0
        assert "Moved:" in result.output

        # File should be moved (source no longer exists)
        expected_dest = dest_dir / date.today().strftime("%Y-%m-%d") / "insta360" / "video.insv"
        assert expected_dest.exists()
        assert expected_dest.read_text() == "video content"
        assert not test_file.exists()  # Source file removed after move

    def test_move_dry_run(self, tmp_path: Path) -> None:
        """Dry run with --move should show 'Would move'."""
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        dest_dir = tmp_path / "dest"
        dest_dir.mkdir()

        test_file = src_dir / "video.insv"
        test_file.write_text("video content")

        result = runner.invoke(app, [str(src_dir), str(dest_dir), "--move"])

        assert result.exit_code == 0
        assert "[DRY RUN]" in result.output
        assert "Would move" in result.output
        assert "Run with --approve to move files" in result.output
        # File should NOT be moved in dry run
        assert test_file.exists()

    def test_dry_run_shows_full_paths(self, tmp_path: Path) -> None:
        """Dry run should show full source and destination paths."""
        src_dir = tmp_path / "src"
        nested = src_dir / "Camera01"
        nested.mkdir(parents=True)
        dest_dir = tmp_path / "dest"
        dest_dir.mkdir()

        test_file = nested / "video.insv"
        test_file.write_text("video content")

        result = runner.invoke(app, [str(src_dir), str(dest_dir)])

        assert result.exit_code == 0
        # Should show full source path
        assert str(test_file) in result.output
        # Should show full destination path
        assert str(dest_dir) in result.output

    def test_skips_existing_same_size(self, tmp_path: Path) -> None:
        """Should skip files that already exist with same size."""
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        dest_dir = tmp_path / "dest"
        dest_dir.mkdir()

        test_file = src_dir / "video.insv"
        test_file.write_text("video content")

        # Pre-create destination file with same content
        date_folder = dest_dir / date.today().strftime("%Y-%m-%d") / "insta360"
        date_folder.mkdir(parents=True)
        existing = date_folder / "video.insv"
        existing.write_text("video content")

        result = runner.invoke(app, [str(src_dir), str(dest_dir)])

        assert result.exit_code == 0
        assert "Skipping 1 files" in result.output

    def test_copies_when_different_size(self, tmp_path: Path) -> None:
        """Should copy files that exist but have different size."""
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        dest_dir = tmp_path / "dest"
        dest_dir.mkdir()

        test_file = src_dir / "video.insv"
        test_file.write_text("new longer video content")

        # Pre-create destination file with different content
        date_folder = dest_dir / date.today().strftime("%Y-%m-%d") / "insta360"
        date_folder.mkdir(parents=True)
        existing = date_folder / "video.insv"
        existing.write_text("old")

        result = runner.invoke(app, [str(src_dir), str(dest_dir), "--approve"])

        assert result.exit_code == 0
        assert "Copied:" in result.output
        assert existing.read_text() == "new longer video content"

    def test_creates_date_folders(self, tmp_path: Path) -> None:
        """Should create date-based folder structure."""
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        dest_dir = tmp_path / "dest"
        dest_dir.mkdir()

        test_file = src_dir / "video.insv"
        test_file.write_text("content")

        result = runner.invoke(app, [str(src_dir), str(dest_dir), "--approve"])

        assert result.exit_code == 0

        # Check folder structure
        date_folder = dest_dir / date.today().strftime("%Y-%m-%d")
        assert date_folder.exists()
        assert (date_folder / "insta360").exists()

    def test_preserves_filename(self, tmp_path: Path) -> None:
        """Should preserve original filename and use date from filename."""
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        dest_dir = tmp_path / "dest"
        dest_dir.mkdir()

        test_file = src_dir / "VID_20230303_193624_00_001.insv"
        test_file.write_text("content")

        result = runner.invoke(app, [str(src_dir), str(dest_dir), "--approve"])

        assert result.exit_code == 0
        # Date extracted from filename (2023-03-03), not filesystem
        expected_dest = dest_dir / "2023-03-03" / "insta360" / "VID_20230303_193624_00_001.insv"
        assert expected_dest.exists()

    def test_handles_multiple_insta360_files(self, tmp_path: Path) -> None:
        """Should handle multiple Insta360 files."""
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        dest_dir = tmp_path / "dest"
        dest_dir.mkdir()

        (src_dir / "video.insv").write_text("content1")
        (src_dir / "photo.insp").write_text("content2")
        (src_dir / "preview.lrv").write_text("content3")

        result = runner.invoke(app, [str(src_dir), str(dest_dir), "--approve"])

        assert result.exit_code == 0
        assert "Copying 3 files" in result.output

    def test_handles_nested_directories(self, tmp_path: Path) -> None:
        """Should handle nested source directories."""
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        nested = src_dir / "Camera01"
        nested.mkdir()
        dest_dir = tmp_path / "dest"
        dest_dir.mkdir()

        (src_dir / "video1.insv").write_text("content1")
        (nested / "video2.insv").write_text("content2")

        result = runner.invoke(app, [str(src_dir), str(dest_dir), "--approve"])

        assert result.exit_code == 0
        assert "Copying 2 files" in result.output

    def test_ignores_non_insta360_files(self, tmp_path: Path) -> None:
        """Should ignore non-Insta360 files."""
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        dest_dir = tmp_path / "dest"
        dest_dir.mkdir()

        (src_dir / "video.insv").write_text("insta360 content")
        (src_dir / "video.mp4").write_text("mp4 content")
        (src_dir / "metadata.json").write_text("{}")

        result = runner.invoke(app, [str(src_dir), str(dest_dir), "--approve"])

        assert result.exit_code == 0
        assert "Copying 1 files" in result.output

        # Only insv file should be copied
        date_folder = dest_dir / date.today().strftime("%Y-%m-%d") / "insta360"
        assert (date_folder / "video.insv").exists()
        assert not (date_folder / "video.mp4").exists()
        assert not (date_folder / "metadata.json").exists()

    def test_empty_source_directory(self, tmp_path: Path) -> None:
        """Should handle empty source directory."""
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        dest_dir = tmp_path / "dest"
        dest_dir.mkdir()

        result = runner.invoke(app, [str(src_dir), str(dest_dir)])

        assert result.exit_code == 0
        assert "No Insta360 files found" in result.output

    def test_no_insta360_files(self, tmp_path: Path) -> None:
        """Should report no files when only non-Insta360 files exist."""
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        dest_dir = tmp_path / "dest"
        dest_dir.mkdir()

        (src_dir / "video.mp4").write_text("mp4 content")
        (src_dir / "metadata.json").write_text("{}")

        result = runner.invoke(app, [str(src_dir), str(dest_dir)])

        assert result.exit_code == 0
        assert "No Insta360 files found" in result.output

    def test_nonexistent_source(self, tmp_path: Path) -> None:
        """Should error on nonexistent source directory."""
        dest_dir = tmp_path / "dest"
        dest_dir.mkdir()

        result = runner.invoke(app, ["/nonexistent/path", str(dest_dir)])

        assert result.exit_code != 0

    def test_nonexistent_destination(self, tmp_path: Path) -> None:
        """Should error on nonexistent destination directory."""
        src_dir = tmp_path / "src"
        src_dir.mkdir()

        result = runner.invoke(app, [str(src_dir), "/nonexistent/path"])

        assert result.exit_code != 0
