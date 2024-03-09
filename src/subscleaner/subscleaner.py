"""Main Subscleaner module."""

"""
Subscleaner.
Copyright (C) 2023 Roger Gonzalez

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import os
import re
import sys
import time

import chardet
import pysrt

ADS = [
    r".*nordvpn.*",
    r".*a Card Shark AMERICASCARDROOM.*",
    r".*OpenSubtitles.*",
    r".*Advertise your product or brand here.*",
    r".*Apóyanos y conviértete en miembro VIP Para.*",
    r".*Addic7ed.*",
    r".*argenteam.*",
    r".*AllSubs.*",
    r"Created and Encoded by.*",
    r".*corrected.*by.*",
    r".*Entre a AmericasCardroom. com Hoy.*",
    r".*Everyone is intimidated by a shark. Become.*",
    r".*Juegue Poker en Línea por Dinero Real.*",
    r".*OpenSubtitles.*",
    r".*Open Subtitles.*",
    r".*MKV Player.*",
    r".*MKV player.*",
    r".*Resync.*for.*",
    r".*Resync.*improved.*",
    r".*Ripped?By.*",
    r'.*Sigue "Community" en.*',
    r".*Subtitles.*by.*",
    r".*Subt?tulos.*por.*",
    r".*Support us and become VIP member.*",
    r".*Subs.*Team.*",
    r".*subscene.*",
    r".*Subtitulado por.*",
    r".*subtitulamos.*",
    r".*Synchronized.*by.*",
    r".*Sincronizado y corregido por.*",
    r".*subdivx.*",
    r".*Sync.*Corrected.*",
    r".*Sync.*corrections.*by.*",
    r".*sync and corrections by.*" r".*Sync.*by.*",
    r".*Una.*traducci?n.*de.*",
    r".*tvsubtitles.*",
    r".*Una.*traducci?n.*de.*",
    "Tacho8",
    r".*www. com.*",
    r".*www. es.*",
]


def ads_in_line(line: str) -> bool:
    """
    Check if the given line contains an ad.

    Args:
        line (str): The line of text to be checked.

    Returns:
        bool: True if the line contains an ad, False otherwise.
    """
    return any(re.match(ad, line, re.DOTALL) for ad in ADS)


def is_already_processed(filename: str) -> bool:
    """
    Check if the file has already been processed.

    Args:
        filename (str): The path to the subtitle file.

    Returns:
        bool: True if the file has already been processed, False otherwise.
    """
    created = os.path.getctime(filename)
    already_processed = time.mktime(
        time.strptime("2021-05-13 00:00:00", "%Y-%m-%d %H:%M:%S"),
    )
    return created < already_processed


def detect_encoding(filename: str) -> str:
    """
    Detect the encoding of the subtitle file.

    Args:
        filename (str): The path to the subtitle file.

    Returns:
        str: The detected encoding of the file.
    """
    with open(filename, "rb") as f:
        return chardet.detect(f.read())["encoding"]


def remove_ads(subs: pysrt.SubRipFile) -> bool:
    """
    Remove ads from the subtitle file.

    Args:
        subs (pysrt.SubRipFile): The subtitle file object.

    Returns:
        bool: True if the file was modified, False otherwise.
    """
    modified = False
    for i, line in enumerate(subs):
        if ads_in_line(line.text):
            print(f"Removing: {line}\n")
            del subs[i]
            modified = True
    return modified


def process_file(filename: str) -> bool:
    """
    Process a subtitle file to remove ads.

    Args:
        filename (str): The path to the subtitle file.

    Returns:
        bool: True if the file was modified, False otherwise.
    """
    try:
        if is_already_processed(filename):
            print(f"Already processed {filename}")
            return False

        print(f"Analyzing: {filename}")

        encoding = detect_encoding(filename)
        subs = pysrt.open(filename, encoding=encoding)

        if remove_ads(subs):
            print(f"Saving {filename}")
            subs.save(filename)
            return True
        return False
    except Exception as e:
        print(f"Error processing {filename}: {e}")
        return False


def process_files(filenames: list[str]) -> list[str]:
    """
    Process multiple subtitle files to remove ads.

    Args:
        filenames (list[str]): A list of subtitle file paths.

    Returns:
        list[str]: A list of modified file paths.
    """
    modified_files = []
    for filename in filenames:
        if process_file(filename):
            modified_files.append(filename)
    return modified_files


def main():
    """
    Process subtitle files to remove ads.

    Read filenames from standard input, process each file to remove ads,
    and print the result. Keep track of the modified files and print
    a summary at the end.
    """
    filenames = [filename.strip() for filename in sys.stdin]
    print("Starting script")
    modified_files = process_files(filenames)
    if modified_files:
        print(f"Modified {len(modified_files)} files")
    print("Done")


if __name__ == "__main__":
    main()
