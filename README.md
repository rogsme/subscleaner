# Subscleaner

<p align="center">
  <img src="https://gitlab.com/uploads/-/system/project/avatar/55502917/logo.jpg" alt="subscleaner"/>
</p>

[![PyPI version](https://badge.fury.io/py/subscleaner.svg)](https://badge.fury.io/py/subscleaner)
[![codecov](https://codecov.io/gl/rogs/subscleaner/graph/badge.svg?token=JDAY18ZIFZ)](https://codecov.io/gl/rogs/subscleaner)
[![docker](https://img.shields.io/badge/Docker-subscleaner-blue)](https://hub.docker.com/r/rogsme/subscleaner)
[![CI](https://git.rogs.me/rogs/subscleaner/actions/workflows/ci.yml/badge.svg)](https://git.rogs.me/rogs/subscleaner/actions)

Subscleaner is a Python script that removes advertisements from subtitle files. It's designed to help you enjoy your favorite shows and movies without the distraction of unwanted ads in the subtitles.

## Features

- Removes a predefined list of advertisement patterns from subtitle files.
- Supports various subtitle formats through the pysrt library.
- Automatically detects the encoding of subtitle files using chardet.
- Available as a Docker image for easy deployment and usage.

## Installation

### Automatic installation

To install with `pip`:

``` sh
sudo pip install subscleaner
```

### Manual installation

To install Subscleaner, you'll need Python 3.9 or higher. It's recommended to use Poetry for managing the project dependencies.

1. Clone the repository:

``` sh
git clone https://gitlab.com/rogs/subscleaner.git
```

2. Navigate to the project directory:

``` sh
cd subscleaner
```

3. Install the dependencies with Poetry:

``` sh
poetry install
```

### Docker

Subscleaner is also available as a Docker image. You can pull the image from Docker Hub:

``` sh
docker pull rogsme/subscleaner
```

## Usage

If you installed the package automatically, you can pipe a list of subtitle filenames into the script:

``` sh
find /your/media/location -name "*.srt" | subscleaner
```

If you installed the package manually:

``` sh
find /your/media/location -name "*.srt" | poetry run subscleaner
```

Alternatively, you can use the script directly if you've installed the dependencies globally:

``` sh
find /your/media/location -name "*.srt" | python3 subscleaner.py
```

### Docker

To use the Docker image, you can run the container with the following command:

``` sh
docker run -e CRON="0 0 * * *" -v /your/media/location:/files -v /etc/localtime:/etc/localtime:ro rogsme/subscleaner
```

- Replace `0 0 * * *` with your desired cron schedule for running the script.
- Replace `/your/media/location` with the path to your media directory containing the subtitle files.

The Docker container will run the Subscleaner script according to the specified cron schedule and process the subtitle files in the mounted media directory.

#### Database Persistence in Docker

By default, the Docker container uses an internal database that will be lost when the container is removed. To maintain a persistent database across container restarts, you should mount a volume for the database:

``` sh
docker run -e CRON="0 0 * * *" \
  -v /your/media/location:/files \
  -v /path/for/database:/data \
  -v /etc/localtime:/etc/localtime:ro \
  rogsme/subscleaner
```

#### If you are using YAMS

YAMS is a highly opinionated media server. You can know more about it here: https://yams.media/

Add this container to your `docker-compose.custom.yaml`:

``` sh
  subscleaner:
    image: rogsme/subscleaner
    environment:
      - CRON=0 0 * * *
    volumes:
      - ${MEDIA_DIRECTORY}:/files
      - ./subscleaner-data:/data
      - /etc/localtime:/etc/localtime:ro
```

This ensures that the database is preserved between container restarts, preventing unnecessary reprocessing of subtitle files.

To get more information on how to add your own containers in YAMS: https://yams.media/advanced/add-your-own-containers/

## Contributing

Contributions are welcome! If you have any suggestions or improvements, feel free to fork the repository and submit a pull request.

## License

Subscleaner is licensed under the GNU General Public License v3.0 or later. See the [LICENSE](https://gitlab.com/rogs/subscleaner/-/blob/master/LICENSE) file for more details.

## Acknowledgments

This repository is a rewrite of this Github repository: https://github.com/FraMecca/subscleaner.

Thanks to [FraMecca](https://github.com/FraMecca/) in Github!

## Database and Caching

Subscleaner now uses a SQLite database to track processed files, which significantly improves performance by avoiding redundant processing of unchanged subtitle files.

### How it works

1. When Subscleaner processes a subtitle file, it generates an MD5 hash of the file content.
2. This hash is stored in a SQLite database along with the file path.
3. On subsequent runs, Subscleaner checks if the file has already been processed by comparing the current hash with the stored hash.
4. If the file hasn't changed, it's skipped, saving processing time.

### Database Location

The SQLite database is stored in the following locations, depending on your operating system:

- **Linux**: `~/.local/share/subscleaner/subscleaner.db`
- **macOS**: `~/Library/Application Support/subscleaner/subscleaner.db`
- **Windows**: `C:\Users\<username>\AppData\Local\subscleaner\subscleaner\subscleaner.db`

### Command Line Options

Several command line options are available:

- `--db-location`: Specify a custom location for the database file
- `--force`: Processes all files regardless of whether they've been processed before
- `--reset-db`: Reset the database (remove all stored file hashes)
- `--list-patterns`: List all advertisement patterns being used
- `--version`: Show version information and exit
- `-v`, `--verbose`: Increase output verbosity (show analyzing/skipping messages)

Example usage:
```sh
find /your/media/location -name "*.srt" | subscleaner --force
find /your/media/location -name "*.srt" | subscleaner --db-location /path/to/custom/database.db
find /your/media/location -name "*.srt" | subscleaner --verbose
```

This feature makes Subscleaner more efficient, especially when running regularly via cron jobs or other scheduled tasks, as it will only process new or modified subtitle files.
