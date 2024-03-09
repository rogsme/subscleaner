"""Unit tests for the subscleaner module."""

from io import StringIO
from unittest.mock import patch

import pysrt
import pytest

from src.subscleaner.subscleaner import (
    ads_in_line,
    detect_encoding,
    is_already_processed,
    main,
    process_file,
    process_files,
    remove_ads,
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
    "line, expected",
    [
        ("This is a normal line", False),
        ("This line contains OpenSubtitles", True),
        ("Subtitles by XYZ", True),
    ],
)
def test_ads_in_line(line, expected):
    """
    Test the ads_in_line function with different input lines and expected results.

    Args:
        line (str): The input line to be tested.
        expected (bool): The expected result (True if the line contains an ad, False otherwise).
    """
    assert ads_in_line(line) is expected


def test_is_already_processed(tmpdir):
    """
    Test the is_already_processed function.

    Args:
        tmpdir (pytest.fixture): A temporary directory for creating the sample SRT file.
    """
    file_path = create_sample_srt_file(tmpdir, "")
    with patch("src.subscleaner.subscleaner.os.path.getctime", return_value=0):
        assert is_already_processed(file_path) is True

    with patch("src.subscleaner.subscleaner.os.path.getctime", return_value=9999999999):
        assert is_already_processed(file_path) is False


def test_detect_encoding(tmpdir, sample_srt_content):
    """
    Test the detect_encoding function.

    Args:
        tmpdir (pytest.fixture): A temporary directory for creating the sample SRT file.
        sample_srt_content (str): The sample SRT content.
    """
    file_path = create_sample_srt_file(tmpdir, sample_srt_content)
    assert detect_encoding(file_path) == "ascii"


def test_remove_ads(sample_srt_content):
    """
    Test the remove_ads function.

    Args:
        sample_srt_content (str): The sample SRT content.
    """
    subs = pysrt.from_string(sample_srt_content)
    subs_expected_ammount = 2
    assert remove_ads(subs) is True
    assert len(subs) == subs_expected_ammount

    subs = pysrt.from_string("1\n00:00:01,000 --> 00:00:03,000\nThis is a sample subtitle.")
    assert remove_ads(subs) is False
    assert len(subs) == 1


def test_process_file_no_modification(tmpdir, sample_srt_content):
    """
    Test the process_file function when the file does not require modification.

    Args:
        tmpdir (pytest.fixture): A temporary directory for creating the sample SRT file.
        sample_srt_content (str): The sample SRT content.
    """
    file_path = create_sample_srt_file(tmpdir, sample_srt_content)
    with patch("src.subscleaner.subscleaner.is_already_processed", return_value=True):
        assert process_file(file_path) is False


def test_process_file_with_modification(tmpdir, sample_srt_content):
    """
    Test the process_file function when the file requires modification.

    Args:
        tmpdir (pytest.fixture): A temporary directory for creating the sample SRT file.
        sample_srt_content (str): The sample SRT content.
    """
    file_path = create_sample_srt_file(tmpdir, sample_srt_content)
    with patch("src.subscleaner.subscleaner.is_already_processed", return_value=False):
        assert process_file(file_path) is True


def test_process_file_error(tmpdir):
    """
    Test the process_file function when an error occurs (e.g., file not found).

    Args:
        tmpdir (pytest.fixture): A temporary directory.
    """
    file_path = tmpdir.join("nonexistent.srt")
    assert process_file(str(file_path)) is False


def test_process_files(tmpdir, sample_srt_content):
    """
    Test the process_files function.

    Args:
        tmpdir (pytest.fixture): A temporary directory for creating the sample SRT files.
        sample_srt_content (str): The sample SRT content.
    """
    file_path1 = create_sample_srt_file(tmpdir, sample_srt_content)
    file_path2 = create_sample_srt_file(tmpdir, "1\n00:00:01,000 --> 00:00:03,000\nThis is a sample subtitle.")
    with patch("src.subscleaner.subscleaner.process_file", side_effect=[True, False]):
        modified_files = process_files([file_path1, file_path2])
        assert modified_files == [file_path1]


def test_main_no_modification(tmpdir, sample_srt_content):
    """
    Test the main function when no files require modification.

    Args:
        tmpdir (pytest.fixture): A temporary directory for creating the sample SRT file.
        sample_srt_content (str): The sample SRT content.
    """
    file_path = create_sample_srt_file(tmpdir, sample_srt_content)
    with (
        patch("sys.stdin", StringIO(file_path)),
        patch("src.subscleaner.subscleaner.process_files", return_value=[]) as mock_process_files,
    ):
        main()
        mock_process_files.assert_called_once_with([file_path])


def test_main_with_modification(tmpdir, sample_srt_content):
    """
    Test the main function when files require modification.

    Args:
        tmpdir (pytest.fixture): A temporary directory for creating the sample SRT file.
        sample_srt_content (str): The sample SRT content.
    """
    file_path = create_sample_srt_file(tmpdir, sample_srt_content)
    with (
        patch("sys.stdin", StringIO(file_path)),
        patch("src.subscleaner.subscleaner.process_files", return_value=[file_path]) as mock_process_files,
    ):
        main()
        mock_process_files.assert_called_once_with([file_path])
