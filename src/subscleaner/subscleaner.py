#!/usr/bin/python3
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


def process_file(filename):
    """
    Process a subtitle file to remove ads.

    Args:
        filename (str): The path to the subtitle file.

    Returns:
        bool: True if the file was modified, False otherwise.
    """
    try:
        created = os.path.getctime(filename)
        already_processed = time.mktime(
            time.strptime("2021-05-13 00:00:00", "%Y-%m-%d %H:%M:%S"),
        )
        if created < already_processed:
            print(f"Already processed {filename}")
            return False

        print(f"Analyzing: {filename}")

        with open(filename, "rb") as f:
            encoding = chardet.detect(f.read())["encoding"]

        subs = pysrt.open(filename, encoding=encoding)
        modified = False
        for i, line in enumerate(subs):
            if ads_in_line(line.text):
                print(f"Removing: {line}\n")
                del subs[i]
                modified = True

        if modified:
            print(f"Saving {filename}")
            subs.save(filename)
            return True
        return False
    except Exception as e:
        print(f"Error processing {filename}: {e}")
        return False


def main():
    """
    Process subtitle files to remove ads.

    Read filenames from standard input, process each file to remove ads,
    and print the result. Keep track of the modified files and print
    a summary at the end.
    """
    modified_files = []
    print("Starting script")
    for filename in sys.stdin:
        filename = filename.strip()
        if process_file(filename):
            modified_files.append(filename)

    if modified_files:
        print(f"Modified {len(modified_files)} files")
    print("Done")


if __name__ == "__main__":
    main()
