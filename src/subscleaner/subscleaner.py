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

AD_PATTERNS = [
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
    re.compile(r"\bfrom 3.49 USD/month ---->\b", re.IGNORECASE),
    re.compile(r"\bimplement REST API from", re.IGNORECASE),
    re.compile(r"\bSignup Here ->", re.IGNORECASE),
    re.compile(r"\bwww\.flixify\.app\b", re.IGNORECASE),
    re.compile(r"\bwww\.ADMITME\.APP\b", re.IGNORECASE),
    re.compile(r"\bwww\.ADMIT1\.APP\b", re.IGNORECASE),
    re.compile(r"\bsaveanilluminati\.com\b", re.IGNORECASE),
    re.compile(r"\bosdb\.link/\w+\b", re.IGNORECASE),
    re.compile(r"\bFilthyRichFutures\.com\b", re.IGNORECASE),
    re.compile(r"\bServerPartDeals\.com\b", re.IGNORECASE),
    re.compile(r"\bStreamingSites\.com\b", re.IGNORECASE),
    re.compile(r"\bSubtitles search by drag & drop\b", re.IGNORECASE),
    re.compile(r"\bSubtitles conformed by\b", re.IGNORECASE),
    re.compile(r"\bSubtitled [Bb]y\b", re.IGNORECASE),
    re.compile(r"\bResync by\b", re.IGNORECASE),
    re.compile(r"\bTRANSCRIPTED BY:\b", re.IGNORECASE),
    re.compile(r"\bVisiontext subtitles:\b", re.IGNORECASE),
    re.compile(r"\bSignup Here\b", re.IGNORECASE),
    re.compile(r"\bFind out @\b", re.IGNORECASE),
    re.compile(r"\bPublic shouldn't leave reviews for lawyers\.\b", re.IGNORECASE),
    re.compile(r"\bTrading can\.\b", re.IGNORECASE),
    re.compile(r"\bFree Browser extension:\b", re.IGNORECASE),
    re.compile(r"\bto get subtitles ->\b", re.IGNORECASE),
    re.compile(r"\bHelp other users to choose the best subtitles\b", re.IGNORECASE),
    re.compile(r"\bwith Subtitles for Free\b", re.IGNORECASE),
    re.compile(r"\bRARBG\b", re.IGNORECASE),
    re.compile(r"\bSerieCanal\.com\b", re.IGNORECASE),
    re.compile(r"\bNest0r\b", re.IGNORECASE),
    re.compile(r"\bikerslot\b", re.IGNORECASE),
    re.compile(r"\bmenoyos\b", re.IGNORECASE),
]


def contains_ad(subtitle_line: str) -> bool:
    """
    Check if the given subtitle line contains an ad.

    Args:
        subtitle_line (str): The subtitle line to be checked.

    Returns:
        bool: True if the subtitle line contains an ad, False otherwise.
    """
    return any(pattern.search(subtitle_line) for pattern in AD_PATTERNS)


def is_processed_before(subtitle_file: str) -> bool:
    """
    Check if the subtitle file has already been processed.

    Args:
        subtitle_file (str): The path to the subtitle file.

    Returns:
        bool: True if the subtitle file has already been processed, False otherwise.
    """
    file_creation_time = os.path.getctime(subtitle_file)
    processed_timestamp = time.mktime(
        time.strptime("2021-05-13 00:00:00", "%Y-%m-%d %H:%M:%S"),
    )
    return file_creation_time < processed_timestamp


def get_encoding(subtitle_file: str) -> str:
    """
    Detect the encoding of the subtitle file.

    Args:
        subtitle_file (str): The path to the subtitle file.

    Returns:
        str: The detected encoding of the subtitle file.
    """
    with open(subtitle_file, "rb") as file:
        return chardet.detect(file.read())["encoding"]


def remove_ad_lines(subtitle_data: pysrt.SubRipFile) -> bool:
    """
    Remove ad lines from the subtitle data.

    Args:
        subtitle_data (pysrt.SubRipFile): The subtitle data object.

    Returns:
        bool: True if the subtitle data was modified, False otherwise.
    """
    modified = False
    for index, subtitle in enumerate(subtitle_data):
        if contains_ad(subtitle.text):
            print(f"Removing: {subtitle}\n")
            del subtitle_data[index]
            modified = True
    return modified


def process_subtitle_file(subtitle_file: str) -> bool:
    """
    Process a subtitle file to remove ad lines.

    Args:
        subtitle_file (str): The path to the subtitle file.

    Returns:
        bool: True if the subtitle file was modified, False otherwise.
    """
    try:
        if is_processed_before(subtitle_file):
            print(f"Already processed {subtitle_file}")
            return False

        print(f"Analyzing: {subtitle_file}")

        encoding = get_encoding(subtitle_file)
        subtitle_data = pysrt.open(subtitle_file, encoding=encoding)

        if remove_ad_lines(subtitle_data):
            print(f"Saving {subtitle_file}")
            subtitle_data.save(subtitle_file)
            return True
        return False
    except Exception as e:
        print(f"Error processing {subtitle_file}: {e}")
        return False


def process_subtitle_files(subtitle_files: list[str]) -> list[str]:
    """
    Process multiple subtitle files to remove ad lines.

    Args:
        subtitle_files (list[str]): A list of subtitle file paths.

    Returns:
        list[str]: A list of modified subtitle file paths.
    """
    modified_files = []
    for subtitle_file in subtitle_files:
        if process_subtitle_file(subtitle_file):
            modified_files.append(subtitle_file)
    return modified_files


def main():
    """
    Process subtitle files to remove ad lines.

    Read subtitle file paths from standard input, process each file to remove ad lines,
    and print the result. Keep track of the modified files and print
    a summary at the end.
    """
    subtitle_files = [file_path.strip() for file_path in sys.stdin]
    print("Starting script")
    modified_files = process_subtitle_files(subtitle_files)
    if modified_files:
        print(f"Modified {len(modified_files)} files")
    print("Done")


if __name__ == "__main__":
    main()
