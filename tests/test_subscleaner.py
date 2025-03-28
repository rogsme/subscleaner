"""Unit tests for the subscleaner module."""

import os
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pysrt
import pytest

from src.subscleaner.subscleaner import (
    contains_ad,
    get_encoding,
    is_processed_before,
    main,
    process_subtitle_file,
    process_subtitle_files,
    remove_ad_lines,
)


@pytest.fixture
def sample_srt_content():
    """Return a sample SRT content."""
    return """1
00:00:01,000 --> 00:00:03,000
This is a sample subtitle.

2
00:00:04,000 --> 00:00:06,000
OpenSubtitles

3
00:00:07,000 --> 00:00:09,000
Another sample subtitle.
"""


@pytest.fixture
def mock_db_path():
    """Return a mock database path."""
    return Path("/tmp/test_subscleaner.db")


@pytest.fixture
def special_chars_temp_dir(tmpdir):
    """Create a temporary directory with special character filenames."""
    special_chars_dir = Path(tmpdir) / "special_chars"
    special_chars_dir.mkdir(exist_ok=True)
    return special_chars_dir


def create_sample_srt_file(tmpdir, content):
    """Create a sample SRT file with the given content."""
    file_path = tmpdir.join("sample.srt")
    file_path.write(content)
    return str(file_path)


def create_special_char_files(dir_path, content):
    """Create sample SRT files with special characters in their names."""
    special_filenames = [
        "file,with,commas.srt",
        "file with spaces.srt",
        "file_with_ümlaut.srt",
        "file_with_ß_char.srt",
        "file_with_áccent.srt",
        "file_with_$ymbol.srt",
        "file_with_パーセント.srt",  # Japanese characters
    ]

    created_files = []
    for filename in special_filenames:
        file_path = dir_path / filename
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        created_files.append(str(file_path))

    return created_files


@pytest.mark.parametrize(
    "subtitle_line, expected_result",
    [
        ("This is a normal line", False),
        ("This line contains OpenSubtitles", True),
        ("Subtitles by XYZ", True),
        ("YTS.MX presents", True),
    ],
)
def test_contains_ad(subtitle_line, expected_result):
    """
    Test the contains_ad function with different subtitle lines and expected results.

    Args:
        subtitle_line (str): The subtitle line to be tested.
        expected_result (bool): The expected result (True if the line contains an ad, False otherwise).
    """
    assert contains_ad(subtitle_line) is expected_result


def test_is_processed_before(tmpdir):
    """
    Test the is_processed_before function.

    Args:
        tmpdir (pytest.fixture): A temporary directory for creating the sample SRT file.
    """
    subtitle_file = create_sample_srt_file(tmpdir, "")
    subtitle_path = Path(subtitle_file)

    with patch("os.path.getctime", return_value=0):
        assert is_processed_before(subtitle_path) is True

    with patch("os.path.getctime", return_value=9999999999):
        assert is_processed_before(subtitle_path) is False


def test_get_encoding(tmpdir, sample_srt_content):
    """
    Test the get_encoding function.

    Args:
        tmpdir (pytest.fixture): A temporary directory for creating the sample SRT file.
        sample_srt_content (str): The sample SRT content.
    """
    subtitle_file = create_sample_srt_file(tmpdir, sample_srt_content)
    encoding = get_encoding(Path(subtitle_file))
    assert encoding in ("ascii", "utf-8"), f"Expected ascii or utf-8, got {encoding}"


def test_remove_ad_lines(sample_srt_content):
    """
    Test the remove_ad_lines function.

    Args:
        sample_srt_content (str): The sample SRT content.
    """
    subtitle_data = pysrt.from_string(sample_srt_content)
    expected_subtitle_count = 2
    assert remove_ad_lines(subtitle_data) is True
    assert len(subtitle_data) == expected_subtitle_count

    subtitle_data = pysrt.from_string("1\n00:00:01,000 --> 00:00:03,000\nThis is a sample subtitle.")
    assert remove_ad_lines(subtitle_data) is False
    assert len(subtitle_data) == 1


def test_process_subtitle_file_no_modification(tmpdir, sample_srt_content, mock_db_path):
    """
    Test the process_subtitle_file function when the file does not require modification.

    Args:
        tmpdir (pytest.fixture): A temporary directory for creating the sample SRT file.
        sample_srt_content (str): The sample SRT content.
        mock_db_path (Path): A mock database path.
    """
    subtitle_file = create_sample_srt_file(tmpdir, sample_srt_content)
    with (
        patch("src.subscleaner.subscleaner.is_processed_before", return_value=True),
        patch("src.subscleaner.subscleaner.is_file_processed", return_value=True),
    ):
        assert process_subtitle_file(subtitle_file, mock_db_path) is False


def test_process_subtitle_file_with_modification(tmpdir, sample_srt_content, mock_db_path):
    """
    Test the process_subtitle_file function when the file requires modification.

    Args:
        tmpdir (pytest.fixture): A temporary directory for creating the sample SRT file.
        sample_srt_content (str): The sample SRT content.
        mock_db_path (Path): A mock database path.
    """
    subtitle_file = create_sample_srt_file(tmpdir, sample_srt_content)
    with (
        patch("src.subscleaner.subscleaner.is_processed_before", return_value=False),
        patch("src.subscleaner.subscleaner.is_file_processed", return_value=False),
        patch("src.subscleaner.subscleaner.get_file_hash", return_value="mockhash"),
        patch("src.subscleaner.subscleaner.mark_file_processed"),
    ):
        assert process_subtitle_file(subtitle_file, mock_db_path) is True


def test_process_subtitle_file_error(tmpdir, mock_db_path):
    """
    Test the process_subtitle_file function when an error occurs (e.g., file not found).

    Args:
        tmpdir (pytest.fixture): A temporary directory.
        mock_db_path (Path): A mock database path.
    """
    subtitle_file = tmpdir.join("nonexistent.srt")
    assert process_subtitle_file(str(subtitle_file), mock_db_path) is False


def test_process_subtitle_files(tmpdir, sample_srt_content, mock_db_path):
    """
    Test the process_subtitle_files function.

    Args:
        tmpdir (pytest.fixture): A temporary directory for creating the sample SRT files.
        sample_srt_content (str): The sample SRT content.
        mock_db_path (Path): A mock database path.
    """
    subtitle_file1 = create_sample_srt_file(tmpdir, sample_srt_content)
    subtitle_file2 = create_sample_srt_file(tmpdir, "1\n00:00:01,000 --> 00:00:03,000\nThis is a sample subtitle.")

    with patch("src.subscleaner.subscleaner.process_subtitle_file", side_effect=[True, False]) as mock_process:
        modified_subtitle_files = process_subtitle_files([subtitle_file1, subtitle_file2], mock_db_path)
        assert modified_subtitle_files == [subtitle_file1]
        assert mock_process.call_count == 2  # noqa PLR2004
        # Check that db_path was passed to process_subtitle_file
        mock_process.assert_any_call(subtitle_file1, mock_db_path, False)
        mock_process.assert_any_call(subtitle_file2, mock_db_path, False)


def test_main_no_modification(tmpdir, sample_srt_content):
    """
    Test the main function when no files require modification.

    Args:
        tmpdir (pytest.fixture): A temporary directory for creating the sample SRT file.
        sample_srt_content (str): The sample SRT content.
    """
    subtitle_file = create_sample_srt_file(tmpdir, sample_srt_content)

    with (
        patch("sys.stdin", StringIO(subtitle_file)),
        patch("sys.argv", ["subscleaner"]),
        patch("src.subscleaner.subscleaner.get_db_path", return_value=Path("/tmp/test_db.db")),
        patch("src.subscleaner.subscleaner.init_db"),
        patch("src.subscleaner.subscleaner.process_subtitle_files", return_value=[]) as mock_process_subtitle_files,
    ):
        main()
        mock_process_subtitle_files.assert_called_once_with([subtitle_file], Path("/tmp/test_db.db"), False)


def test_main_with_modification(tmpdir, sample_srt_content):
    """
    Test the main function when files require modification.

    Args:
        tmpdir (pytest.fixture): A temporary directory for creating the sample SRT file.
        sample_srt_content (str): The sample SRT content.
    """
    subtitle_file = create_sample_srt_file(tmpdir, sample_srt_content)

    with (
        patch("sys.stdin", StringIO(subtitle_file)),
        patch("sys.argv", ["subscleaner"]),
        patch("src.subscleaner.subscleaner.get_db_path", return_value=Path("/tmp/test_db.db")),
        patch("src.subscleaner.subscleaner.init_db"),
        patch(
            "src.subscleaner.subscleaner.process_subtitle_files",
            return_value=[subtitle_file],
        ) as mock_process_subtitle_files,
    ):
        main()
        mock_process_subtitle_files.assert_called_once_with([subtitle_file], Path("/tmp/test_db.db"), False)


def test_process_files_with_special_chars(special_chars_temp_dir, sample_srt_content, mock_db_path):
    """
    Test processing subtitle files with special characters in their names.

    Args:
        special_chars_temp_dir: Temporary directory for special character files
        sample_srt_content: Sample SRT content
        mock_db_path (Path): A mock database path.
    """
    special_files = create_special_char_files(special_chars_temp_dir, sample_srt_content)

    with (
        patch("src.subscleaner.subscleaner.is_processed_before", return_value=False),
        patch("src.subscleaner.subscleaner.is_file_processed", return_value=False),
        patch("src.subscleaner.subscleaner.get_file_hash", return_value="mockhash"),
        patch("src.subscleaner.subscleaner.mark_file_processed"),
    ):
        modified_files = process_subtitle_files(special_files, mock_db_path)

    assert len(modified_files) == len(special_files), "Not all files with special characters were processed"


def test_get_encoding_with_special_chars(special_chars_temp_dir, sample_srt_content):
    """
    Test encoding detection for files with special characters in their names.

    Args:
        special_chars_temp_dir: Temporary directory for special character files
        sample_srt_content: Sample SRT content
    """
    file_path = special_chars_temp_dir / "test_ümlaut_ß_áccent.srt"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(sample_srt_content)

    encoding = get_encoding(file_path)
    assert encoding is not None, "Encoding detection failed for file with special characters"

    non_existent_file = special_chars_temp_dir / "non_existent_ümlaut.srt"
    try:
        encoding = get_encoding(non_existent_file)
        assert encoding == "utf-8", "Fallback encoding is not utf-8"
    except Exception as e:
        pytest.fail(f"get_encoding raised {e} with non-existent file")


def test_is_processed_before_with_special_chars(special_chars_temp_dir):
    """
    Test is_processed_before function with special character filenames.

    Args:
        special_chars_temp_dir: Temporary directory for special character files
    """
    file_path = special_chars_temp_dir / "check_processed_ümlaut.srt"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("Test content")

    with patch("os.path.getctime", return_value=0):
        assert is_processed_before(file_path) is True

    with patch("os.path.getctime", return_value=9999999999):
        assert is_processed_before(file_path) is False

    non_existent_file = special_chars_temp_dir / "non_existent_ümlaut.srt"
    assert is_processed_before(non_existent_file) is False


def test_process_subtitle_file_with_special_chars(special_chars_temp_dir, sample_srt_content, mock_db_path):
    """
    Test process_subtitle_file function with special character filenames.

    Args:
        special_chars_temp_dir: Temporary directory for special character files
        sample_srt_content: Sample SRT content
        mock_db_path (Path): A mock database path.
    """
    file_path = special_chars_temp_dir / "process_this_ümlaut,file.srt"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(sample_srt_content)

    with (
        patch("src.subscleaner.subscleaner.is_processed_before", return_value=False),
        patch("src.subscleaner.subscleaner.is_file_processed", return_value=False),
        patch("src.subscleaner.subscleaner.get_file_hash", return_value="mockhash"),
        patch("src.subscleaner.subscleaner.mark_file_processed"),
    ):
        assert process_subtitle_file(str(file_path), mock_db_path) is True

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "OpenSubtitles" not in content

    non_existent_file = str(special_chars_temp_dir / "non_existent_ümlaut,file.srt")
    assert process_subtitle_file(non_existent_file, mock_db_path) is False


def test_file_saving_with_special_chars(special_chars_temp_dir, sample_srt_content, mock_db_path):
    """
    Test that files with special characters can be saved correctly after modification.

    Args:
        special_chars_temp_dir: Temporary directory for special character files
        sample_srt_content: Sample SRT content
        mock_db_path (Path): A mock database path.
    """
    special_files = create_special_char_files(special_chars_temp_dir, sample_srt_content)

    with (
        patch("src.subscleaner.subscleaner.is_processed_before", return_value=False),
        patch("src.subscleaner.subscleaner.is_file_processed", return_value=False),
        patch("src.subscleaner.subscleaner.get_file_hash", return_value="mockhash"),
        patch("src.subscleaner.subscleaner.mark_file_processed"),
    ):
        modified_files = process_subtitle_files(special_files, mock_db_path)

    for file_path in modified_files:
        assert os.path.exists(file_path), f"File {file_path} does not exist after saving"

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            assert "OpenSubtitles" not in content, f"Content was not properly saved in {file_path}"
        except Exception as e:
            pytest.fail(f"Failed to reopen file {file_path} after saving: {e}")


def test_main_with_special_chars(special_chars_temp_dir, sample_srt_content):
    """
    Test the main function with filenames containing special characters.

    Args:
        special_chars_temp_dir: Temporary directory for special character files
        sample_srt_content: Sample SRT content
    """
    file_path = special_chars_temp_dir / "main_test_ümlaut,file.srt"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(sample_srt_content)

    stdin_content = str(file_path)

    with (
        patch("sys.stdin", StringIO(stdin_content)),
        patch("sys.argv", ["subscleaner"]),
        patch("src.subscleaner.subscleaner.get_db_path", return_value=Path("/tmp/test_db.db")),
        patch("src.subscleaner.subscleaner.init_db"),
        patch(
            "src.subscleaner.subscleaner.process_subtitle_files",
            return_value=[str(file_path)],
        ) as mock_process_subtitle_files,
    ):
        main()
        mock_process_subtitle_files.assert_called_once_with([str(file_path)], Path("/tmp/test_db.db"), False)
