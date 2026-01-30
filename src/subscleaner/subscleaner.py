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

import argparse
import hashlib
import pathlib
import re
import sqlite3
import sys

import chardet
import pysrt
from appdirs import user_data_dir

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
    re.compile(r"\bYTS.MX\b", re.IGNORECASE),
    re.compile(r"\bYTS.LT\b", re.IGNORECASE),
    re.compile(r"\bYTS.BZ\b", re.IGNORECASE),
]


def get_db_path(db_location=None):
    """
    Get the path to the SQLite database.

    Args:
        db_location (str, optional): Custom path for the database file.

    Returns:
        pathlib.Path: The path to the database file.
    """
    if db_location:
        db_path = pathlib.Path(db_location)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return db_path

    app_data_dir = pathlib.Path(user_data_dir("subscleaner", "subscleaner"))
    app_data_dir.mkdir(parents=True, exist_ok=True)
    return app_data_dir / "subscleaner.db"


def init_db(db_path):
    """
    Initialize the database if it doesn't exist.

    Args:
        db_path (pathlib.Path): The path to the database file.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS processed_files (
        file_path TEXT PRIMARY KEY,
        file_hash TEXT NOT NULL,
        processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


def get_file_hash(file_path):
    """
    Generate an MD5 hash of the file content.

    Args:
        file_path (pathlib.Path): The path to the file.

    Returns:
        str: The MD5 hash of the file content.
    """
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        print(f"Error generating hash for {file_path}: {e}")
        return None


def is_file_processed(db_path, file_path, file_hash):
    """
    Check if the file has been processed before.

    Args:
        db_path (pathlib.Path): The path to the database file.
        file_path (str): The path to the file.
        file_hash (str): The MD5 hash of the file content.

    Returns:
        bool: True if the file has been processed before, False otherwise.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT file_hash FROM processed_files WHERE file_path = ?",
        (str(file_path),),
    )
    result = cursor.fetchone()

    conn.close()

    if result is None:
        return False

    # If the hash has changed, the file has been modified
    return result[0] == file_hash


def mark_file_processed(db_path, file_path, file_hash):
    """
    Mark the file as processed in the database.

    Args:
        db_path (pathlib.Path): The path to the database file.
        file_path (str): The path to the file.
        file_hash (str): The MD5 hash of the file content.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT OR REPLACE INTO processed_files (file_path, file_hash) VALUES (?, ?)",
        (str(file_path), file_hash),
    )

    conn.commit()
    conn.close()


def contains_ad(subtitle_line: str) -> bool:
    """
    Check if the given subtitle line contains an ad.

    Args:
        subtitle_line (str): The subtitle line to be checked.

    Returns:
        bool: True if the subtitle line contains an ad, False otherwise.
    """
    return any(pattern.search(subtitle_line) for pattern in AD_PATTERNS)


def get_encoding(subtitle_file: pathlib.Path) -> str:
    """
    Detect the encoding of the subtitle file.

    Args:
        subtitle_file (pathlib.Path): The path to the subtitle file.

    Returns:
        str: The detected encoding of the subtitle file.
    """
    try:
        with open(subtitle_file, "rb") as file:
            return chardet.detect(file.read())["encoding"] or "utf-8"
    except Exception as e:
        print(f"Error detecting encoding: {e}")
        return "utf-8"


def remove_ad_lines(subtitle_data: pysrt.SubRipFile) -> bool:
    """
    Remove ad lines from the subtitle data.

    Args:
        subtitle_data (pysrt.SubRipFile): The subtitle data object.

    Returns:
        bool: True if the subtitle data was modified, False otherwise.
    """
    modified = False
    indices_to_remove = []

    for index, subtitle in enumerate(subtitle_data):
        if contains_ad(subtitle.text):
            print(f"Removing: {subtitle}\n")
            indices_to_remove.append(index)
            modified = True

    for index in sorted(indices_to_remove, reverse=True):
        del subtitle_data[index]

    return modified


def is_already_processed(subtitle_file, db_path, file_hash, force=False, verbose=False):
    """
    Check if the subtitle file has already been processed.

    This function checks the database to determine if a file has already been processed.

    Args:
        subtitle_file (pathlib.Path): The path to the subtitle file.
        db_path (pathlib.Path): The path to the database file.
        file_hash (str): The MD5 hash of the file content.
        force (bool): If True, ignore previous processing status.

    Returns:
        bool: True if the file has already been processed, False otherwise.
    """
    if force:
        return False

    # Check if the file is in the database with the same hash
    if is_file_processed(db_path, str(subtitle_file), file_hash):
        if verbose:
            print(f"Already processed {subtitle_file} (hash match)")
        return True

    return False


def process_subtitle_file(subtitle_file_path: str, db_path, force=False, verbose=False) -> bool:
    """
    Process a subtitle file to remove ad lines.

    Args:
        subtitle_file_path (str): The path to the subtitle file.
        db_path (pathlib.Path): The path to the database file.
        force (bool): If True, process the file even if it has been processed before.
        verbose (bool): If True, print detailed processing information.

    Returns:
        bool: True if the subtitle file was modified, False otherwise.
    """
    try:
        subtitle_file = pathlib.Path(subtitle_file_path)
        if verbose:
            print(f"Analyzing: {subtitle_file}")

        # Early validation checks
        if not subtitle_file.exists():
            print(f"File not found: {subtitle_file}")
            return False

        # Get file hash and check if already processed
        file_hash = get_file_hash(subtitle_file)
        if file_hash is None or is_already_processed(subtitle_file, db_path, file_hash, force):
            return False

        # Process the subtitle file
        modified = False
        encoding = get_encoding(subtitle_file)

        # Try to open the subtitle file
        subtitle_data = None
        try:
            subtitle_data = pysrt.open(subtitle_file, encoding=encoding)
        except UnicodeDecodeError:
            print(f"Failed to open with detected encoding {encoding}, trying utf-8")
            try:
                subtitle_data = pysrt.open(subtitle_file, encoding="utf-8")
            except Exception as e:
                print(f"Error opening subtitle file with pysrt: {e}")
                return False
        except Exception as e:
            print(f"Error opening subtitle file with pysrt: {e}")
            return False

        # Remove ad lines and save if modified
        if subtitle_data and remove_ad_lines(subtitle_data):
            print(f"Saving {subtitle_file}")
            subtitle_data.save(subtitle_file)
            # Update the hash after modification
            new_hash = get_file_hash(subtitle_file)
            mark_file_processed(db_path, str(subtitle_file), new_hash)
            modified = True
        else:
            # Mark as processed even if no changes were made
            mark_file_processed(db_path, str(subtitle_file), file_hash)

        return modified
    except Exception as e:
        print(f"Error processing {subtitle_file_path}: {e}")
        return False


def process_subtitle_files(subtitle_files: list[str], db_path, force=False, verbose=False) -> list[str]:
    """
    Process multiple subtitle files to remove ad lines.

    Args:
        subtitle_files (list[str]): A list of subtitle file paths.
        db_path (pathlib.Path): The path to the database file.
        force (bool): If True, process files even if they have been processed before.
        verbose (bool): If True, print detailed processing information.

    Returns:
        list[str]: A list of modified subtitle file paths.
    """
    modified_files = []
    for subtitle_file in subtitle_files:
        if process_subtitle_file(subtitle_file, db_path, force, verbose):
            modified_files.append(subtitle_file)
    return modified_files


def _parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Remove advertisements from subtitle files.")
    parser.add_argument(
        "--db-location",
        type=str,
        help="Specify a custom location for the database file",
    )
    parser.add_argument("--force", action="store_true", help="Process files even if they have been processed before")
    parser.add_argument("--version", action="store_true", help="Show version information and exit")
    parser.add_argument("--reset-db", action="store_true", help="Reset the database (remove all stored file hashes)")
    parser.add_argument("--list-patterns", action="store_true", help="List all advertisement patterns being used")
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Increase output verbosity (show analyzing/skipping messages)",
    )
    return parser.parse_args()


def _print_version():
    """Print the application version."""
    try:
        from subscleaner import __version__

        print(f"Subscleaner version {__version__}")
    except ImportError:
        import importlib.metadata

        version = importlib.metadata.version("subscleaner")
        print(f"Subscleaner version {version}")


def _reset_database(db_path):
    """Reset the database file."""
    if db_path.exists():
        try:
            db_path.unlink()
            print(f"Database reset successfully: {db_path}")
        except Exception as e:
            print(f"Error resetting database: {e}")
    else:
        print(f"No database found at {db_path}")


def _list_patterns():
    """List the configured ad patterns."""
    print("Advertisement patterns being used:")
    for i, pattern in enumerate(AD_PATTERNS, 1):
        print(f"{i}. {pattern.pattern}")


def main():
    """
    Run the main entry point for the Subscleaner script.

    Parse arguments, handle special commands like version or reset-db,
    and processes subtitle files provided via stdin.
    """
    args = _parse_args()

    # Handle version request
    if args.version:
        _print_version()
        return

    # Get database path
    db_path = get_db_path(args.db_location)

    # Handle reset database request
    if args.reset_db:
        _reset_database(db_path)
        return

    # Handle list patterns request
    if args.list_patterns:
        _list_patterns()
        return

    # Initialize database if not resetting
    init_db(db_path)

    # Process subtitle files
    subtitle_files = [file_path.strip() for file_path in sys.stdin]
    if not subtitle_files:
        print("No subtitle files provided. Pipe filenames to subscleaner or use --help for more information.")
        return

    if args.verbose:
        print("Starting script")
    modified_files = process_subtitle_files(subtitle_files, db_path, args.force, args.verbose)
    if modified_files:
        print(f"Modified {len(modified_files)} files")
    print("Done")


if __name__ == "__main__":
    main()
