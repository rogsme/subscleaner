"""Unit tests for the subscleaner module."""

from io import StringIO
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


def create_sample_srt_file(tmpdir, content):
    """Create a sample SRT file with the given content."""
    file_path = tmpdir.join("sample.srt")
    file_path.write(content)
    return str(file_path)


@pytest.mark.parametrize(
    "subtitle_line, expected_result",
    [
        ("This is a normal line", False),
        ("This line contains OpenSubtitles", True),
        ("Subtitles by XYZ", True),
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
    with patch("src.subscleaner.subscleaner.os.path.getctime", return_value=0):
        assert is_processed_before(subtitle_file) is True

    with patch("src.subscleaner.subscleaner.os.path.getctime", return_value=9999999999):
        assert is_processed_before(subtitle_file) is False


def test_get_encoding(tmpdir, sample_srt_content):
    """
    Test the get_encoding function.

    Args:
        tmpdir (pytest.fixture): A temporary directory for creating the sample SRT file.
        sample_srt_content (str): The sample SRT content.
    """
    subtitle_file = create_sample_srt_file(tmpdir, sample_srt_content)
    assert get_encoding(subtitle_file) == "ascii"


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


def test_process_subtitle_file_no_modification(tmpdir, sample_srt_content):
    """
    Test the process_subtitle_file function when the file does not require modification.

    Args:
        tmpdir (pytest.fixture): A temporary directory for creating the sample SRT file.
        sample_srt_content (str): The sample SRT content.
    """
    subtitle_file = create_sample_srt_file(tmpdir, sample_srt_content)
    with patch("src.subscleaner.subscleaner.is_processed_before", return_value=True):
        assert process_subtitle_file(subtitle_file) is False


def test_process_subtitle_file_with_modification(tmpdir, sample_srt_content):
    """
    Test the process_subtitle_file function when the file requires modification.

    Args:
        tmpdir (pytest.fixture): A temporary directory for creating the sample SRT file.
        sample_srt_content (str): The sample SRT content.
    """
    subtitle_file = create_sample_srt_file(tmpdir, sample_srt_content)
    with patch("src.subscleaner.subscleaner.is_processed_before", return_value=False):
        assert process_subtitle_file(subtitle_file) is True


def test_process_subtitle_file_error(tmpdir):
    """
    Test the process_subtitle_file function when an error occurs (e.g., file not found).

    Args:
        tmpdir (pytest.fixture): A temporary directory.
    """
    subtitle_file = tmpdir.join("nonexistent.srt")
    assert process_subtitle_file(str(subtitle_file)) is False


def test_process_subtitle_files(tmpdir, sample_srt_content):
    """
    Test the process_subtitle_files function.

    Args:
        tmpdir (pytest.fixture): A temporary directory for creating the sample SRT files.
        sample_srt_content (str): The sample SRT content.
    """
    subtitle_file1 = create_sample_srt_file(tmpdir, sample_srt_content)
    subtitle_file2 = create_sample_srt_file(tmpdir, "1\n00:00:01,000 --> 00:00:03,000\nThis is a sample subtitle.")
    with patch("src.subscleaner.subscleaner.process_subtitle_file", side_effect=[True, False]):
        modified_subtitle_files = process_subtitle_files([subtitle_file1, subtitle_file2])
        assert modified_subtitle_files == [subtitle_file1]


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
        patch("src.subscleaner.subscleaner.process_subtitle_files", return_value=[]) as mock_process_subtitle_files,
    ):
        main()
        mock_process_subtitle_files.assert_called_once_with([subtitle_file])


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
        patch(
            "src.subscleaner.subscleaner.process_subtitle_files",
            return_value=[subtitle_file],
        ) as mock_process_subtitle_files,
    ):
        main()
        mock_process_subtitle_files.assert_called_once_with([subtitle_file])
