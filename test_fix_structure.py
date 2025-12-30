"""Tests for fix_structure.py"""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from fix_structure import (
    app,
    is_insta360_file,
    is_date_folder,
    get_date_folder,
    is_compliant,
)

runner = CliRunner()


class TestIsInsta360File:
    """Tests for is_insta360_file function."""

    def test_insv_is_insta360(self, tmp_path: Path) -> None:
        assert is_insta360_file(tmp_path / "video.insv") is True

    def test_insp_is_insta360(self, tmp_path: Path) -> None:
        assert is_insta360_file(tmp_path / "photo.insp") is True

    def test_lrv_is_insta360(self, tmp_path: Path) -> None:
        assert is_insta360_file(tmp_path / "preview.lrv") is True

    def test_uppercase_insta360_extensions(self, tmp_path: Path) -> None:
        assert is_insta360_file(tmp_path / "video.INSV") is True
        assert is_insta360_file(tmp_path / "photo.INSP") is True
        assert is_insta360_file(tmp_path / "preview.LRV") is True

    def test_mp4_is_not_insta360(self, tmp_path: Path) -> None:
        assert is_insta360_file(tmp_path / "video.mp4") is False

    def test_mov_is_not_insta360(self, tmp_path: Path) -> None:
        assert is_insta360_file(tmp_path / "video.mov") is False

    def test_json_is_not_insta360(self, tmp_path: Path) -> None:
        assert is_insta360_file(tmp_path / "metadata.json") is False

    def test_fileinfo_list_is_insta360(self, tmp_path: Path) -> None:
        assert is_insta360_file(tmp_path / "fileinfo_list.list") is True

    def test_other_list_file_is_not_insta360(self, tmp_path: Path) -> None:
        assert is_insta360_file(tmp_path / "other.list") is False


class TestIsDateFolder:
    """Tests for is_date_folder function."""

    def test_simple_date(self, tmp_path: Path) -> None:
        folder = tmp_path / "2024-01-15"
        assert is_date_folder(folder) is True

    def test_date_with_project_name(self, tmp_path: Path) -> None:
        folder = tmp_path / "2024-01-15-my-project"
        assert is_date_folder(folder) is True

    def test_date_with_complex_suffix(self, tmp_path: Path) -> None:
        folder = tmp_path / "2024-01-15-trip-to-paris-2024"
        assert is_date_folder(folder) is True

    def test_date_with_space_suffix(self, tmp_path: Path) -> None:
        folder = tmp_path / "2023-03-03 Moggs in the dark"
        assert is_date_folder(folder) is True

    def test_non_date_folder(self, tmp_path: Path) -> None:
        folder = tmp_path / "some-folder"
        assert is_date_folder(folder) is False

    def test_insta360_folder(self, tmp_path: Path) -> None:
        folder = tmp_path / "insta360"
        assert is_date_folder(folder) is False


class TestGetDateFolder:
    """Tests for get_date_folder function."""

    def test_file_in_date_folder(self, tmp_path: Path) -> None:
        date_folder = tmp_path / "2024-01-15"
        file_path = date_folder / "video.insv"

        result = get_date_folder(file_path, tmp_path)
        assert result == date_folder

    def test_file_in_subfolder_of_date_folder(self, tmp_path: Path) -> None:
        date_folder = tmp_path / "2024-01-15"
        file_path = date_folder / "insta360" / "video.insv"

        result = get_date_folder(file_path, tmp_path)
        assert result == date_folder

    def test_file_in_nested_subfolder(self, tmp_path: Path) -> None:
        date_folder = tmp_path / "2024-01-15"
        file_path = date_folder / "Camera01" / "video.insv"

        result = get_date_folder(file_path, tmp_path)
        assert result == date_folder

    def test_file_not_in_date_folder(self, tmp_path: Path) -> None:
        file_path = tmp_path / "random-folder" / "video.insv"

        result = get_date_folder(file_path, tmp_path)
        assert result is None


class TestIsCompliant:
    """Tests for is_compliant function."""

    def test_insv_in_insta360_is_compliant(self, tmp_path: Path) -> None:
        date_folder = tmp_path / "2024-01-15"
        file_path = date_folder / "insta360" / "video.insv"

        assert is_compliant(file_path, date_folder) is True

    def test_insv_in_date_folder_root_is_not_compliant(self, tmp_path: Path) -> None:
        date_folder = tmp_path / "2024-01-15"
        file_path = date_folder / "video.insv"

        assert is_compliant(file_path, date_folder) is False

    def test_insv_in_camera_folder_is_not_compliant(self, tmp_path: Path) -> None:
        date_folder = tmp_path / "2024-01-15"
        file_path = date_folder / "Camera01" / "video.insv"

        assert is_compliant(file_path, date_folder) is False


class TestCLI:
    """Tests for CLI interface."""

    def test_empty_directory(self, tmp_path: Path) -> None:
        result = runner.invoke(app, [str(tmp_path)])

        assert result.exit_code == 0
        assert "No Insta360 files found" in result.output

    def test_no_insta360_files(self, tmp_path: Path) -> None:
        """Should report no files when only non-Insta360 files exist."""
        date_folder = tmp_path / "2024-01-15"
        date_folder.mkdir()
        (date_folder / "video.mp4").write_text("content")
        (date_folder / "metadata.json").write_text("{}")

        result = runner.invoke(app, [str(tmp_path)])

        assert result.exit_code == 0
        assert "No Insta360 files found" in result.output

    def test_all_compliant(self, tmp_path: Path) -> None:
        date_folder = tmp_path / "2024-01-15"
        insta360_folder = date_folder / "insta360"
        insta360_folder.mkdir(parents=True)
        (insta360_folder / "video.insv").write_text("content")

        result = runner.invoke(app, [str(tmp_path)])

        assert result.exit_code == 0
        assert "All Insta360 files are already compliant" in result.output

    def test_file_in_date_folder_root(self, tmp_path: Path) -> None:
        date_folder = tmp_path / "2024-01-15"
        date_folder.mkdir()
        (date_folder / "video.insv").write_text("content")

        result = runner.invoke(app, [str(tmp_path)])

        assert result.exit_code == 0
        assert "#!/usr/bin/env bash" in result.output
        assert "set -x" in result.output
        assert "mkdir -p" in result.output
        assert "/insta360" in result.output
        assert "mv" in result.output
        assert "video.insv" in result.output

    def test_file_in_camera_subfolder(self, tmp_path: Path) -> None:
        date_folder = tmp_path / "2024-01-15"
        camera_folder = date_folder / "Camera01"
        camera_folder.mkdir(parents=True)
        (camera_folder / "video.insv").write_text("content")

        result = runner.invoke(app, [str(tmp_path)])

        assert result.exit_code == 0
        assert "mkdir -p" in result.output
        assert "/insta360" in result.output
        assert "mv" in result.output
        assert "video.insv" in result.output

    def test_multiple_files(self, tmp_path: Path) -> None:
        date_folder = tmp_path / "2024-01-15"
        date_folder.mkdir()
        (date_folder / "video.insv").write_text("content1")
        (date_folder / "photo.insp").write_text("content2")
        (date_folder / "preview.lrv").write_text("content3")

        result = runner.invoke(app, [str(tmp_path)])

        assert result.exit_code == 0
        assert "/insta360" in result.output
        assert "3 files to move" in result.output

    def test_ignores_non_insta360_files(self, tmp_path: Path) -> None:
        """Should only process Insta360 files, ignoring others."""
        date_folder = tmp_path / "2024-01-15"
        date_folder.mkdir()
        (date_folder / "video.insv").write_text("content1")
        (date_folder / "video.mp4").write_text("content2")
        (date_folder / "metadata.json").write_text("{}")

        result = runner.invoke(app, [str(tmp_path)])

        assert result.exit_code == 0
        assert "video.insv" in result.output
        assert "video.mp4" not in result.output
        assert "metadata.json" not in result.output
        assert "1 files to move" in result.output

    def test_date_folder_with_project_name(self, tmp_path: Path) -> None:
        date_folder = tmp_path / "2024-01-15-vacation"
        date_folder.mkdir()
        (date_folder / "video.insv").write_text("content")

        result = runner.invoke(app, [str(tmp_path)])

        assert result.exit_code == 0
        assert "2024-01-15-vacation/insta360" in result.output

    def test_files_outside_date_folders_ignored(self, tmp_path: Path) -> None:
        random_folder = tmp_path / "not-a-date"
        random_folder.mkdir()
        (random_folder / "video.insv").write_text("content")

        result = runner.invoke(app, [str(tmp_path)])

        assert result.exit_code == 0
        # Should not generate any mv commands for files outside date folders
        assert "mv" not in result.output

    def test_warns_about_non_compliant_folders(self, tmp_path: Path) -> None:
        """Should warn about folders that don't match date pattern."""
        # Create a compliant date folder with files to move
        date_folder = tmp_path / "2024-01-15"
        date_folder.mkdir()
        (date_folder / "video.insv").write_text("content")

        # Create non-compliant folders
        (tmp_path / "random-folder").mkdir()
        (tmp_path / "Camera01").mkdir()

        result = runner.invoke(app, [str(tmp_path)])

        assert result.exit_code == 0
        assert "Warning: Non-compliant folders found in root" in result.output
        assert "random-folder" in result.output
        assert "Camera01" in result.output

    def test_date_folder_with_space_suffix(self, tmp_path: Path) -> None:
        """Test folder names like '2023-03-03 Moggs in the dark'."""
        date_folder = tmp_path / "2023-03-03 Moggs in the dark"
        camera_folder = date_folder / "Camera01"
        camera_folder.mkdir(parents=True)
        (camera_folder / "VID_20230303_193624_00_001.insv").write_text("content")

        result = runner.invoke(app, [str(tmp_path)])

        assert result.exit_code == 0
        assert "mkdir -p" in result.output
        assert "/insta360" in result.output
        assert "VID_20230303_193624_00_001.insv" in result.output
        assert "1 files to move" in result.output
