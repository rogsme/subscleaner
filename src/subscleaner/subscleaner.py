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
    re.compile(r"\bnordvpn\b", re.IGNORECASE),
    re.compile(r"\ba Card Shark AMERICASCARDROOM\b", re.IGNORECASE),
    re.compile(r"\bOpenSubtitles\b", re.IGNORECASE),
    re.compile(r"\bAdvertise your product or brand here\b", re.IGNORECASE),
    re.compile(r"\bApóyanos y conviértete en miembro VIP Para\b", re.IGNORECASE),
    re.compile(r"\bAddic7ed\b", re.IGNORECASE),
    re.compile(r"\bargenteam\b", re.IGNORECASE),
    re.compile(r"\bAllSubs\b", re.IGNORECASE),
    re.compile(r"\bCreated and Encoded by\b", re.IGNORECASE),
    re.compile(r"\bcorrected\s+by\b", re.IGNORECASE),
    re.compile(r"\bEntre a AmericasCardroom\.com Hoy\b", re.IGNORECASE),
    re.compile(r"\bEveryone is intimidated by a shark\. Become\b", re.IGNORECASE),
    re.compile(r"\bJuegue Poker en Línea por Dinero Real\b", re.IGNORECASE),
    re.compile(r"\bOpen Subtitles\b", re.IGNORECASE),
    re.compile(r"\bMKV Player\b", re.IGNORECASE),
    re.compile(r"\bResync\s+for\b", re.IGNORECASE),
    re.compile(r"\bResync\s+improved\b", re.IGNORECASE),
    re.compile(r"\bRipped\s+By\b", re.IGNORECASE),
    re.compile(r'\bSigue "Community" en\b', re.IGNORECASE),
    re.compile(r"\bSubtitles\s+by\b", re.IGNORECASE),
    re.compile(r"\bSubt[íi]tulos\s+por\b", re.IGNORECASE),
    re.compile(r"\bSupport us and become VIP member\b", re.IGNORECASE),
    re.compile(r"\bSubs\s+Team\b", re.IGNORECASE),
    re.compile(r"\bsubscene\b", re.IGNORECASE),
    re.compile(r"\bSubtitulado por\b", re.IGNORECASE),
    re.compile(r"\bsubtitulamos\b", re.IGNORECASE),
    re.compile(r"\bSynchronized\s+by\b", re.IGNORECASE),
    re.compile(r"\bSincronizado y corregido por\b", re.IGNORECASE),
    re.compile(r"\bsubdivx\b", re.IGNORECASE),
    re.compile(r"\bSync\s+Corrected\b", re.IGNORECASE),
    re.compile(r"\bSync\s+corrections\s+by\b", re.IGNORECASE),
    re.compile(r"\bsync and corrections by\b", re.IGNORECASE),
    re.compile(r"\bSync\s+by\b", re.IGNORECASE),
    re.compile(r"\bUna\s+traducci[óo]n\s+de\b", re.IGNORECASE),
    re.compile(r"\btvsubtitles\b", re.IGNORECASE),
    re.compile(r"\bTacho8\b", re.IGNORECASE),
    re.compile(r"\bwww\.\S+\.com\b", re.IGNORECASE),
    re.compile(r"\bwww\.\S+\.es\b", re.IGNORECASE),
]


def ads_in_line(line: str) -> bool:
    """
    Check if the given line contains an ad.

    Args:
        line (str): The line of text to be checked.

    Returns:
        bool: True if the line contains an ad, False otherwise.
    """
    return any(ad.search(line) for ad in ADS)


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
