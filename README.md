# Subscleaner

<p align="center">
  <img src="https://gitlab.com/uploads/-/system/project/avatar/55502917/logo.jpg" alt="subscleaner"/>
</p>

[![PyPI version](https://badge.fury.io/py/subscleaner.svg)](https://badge.fury.io/py/subscleaner)
[![codecov](https://codecov.io/gl/rogs/subscleaner/graph/badge.svg?token=JDAY18ZIFZ)](https://codecov.io/gl/rogs/subscleaner)
[![docker](https://img.shields.io/badge/Docker-subscleaner-blue)](https://hub.docker.com/r/rogsme/subscleaner)

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
docker run -e CRON="0 0 * * *" -v /your/media/location:/files rogsme/subscleaner
```

- Replace `0 0 * * *` with your desired cron schedule for running the script.
- Replace `/your/media/location` with the path to your media directory containing the subtitle files.

The Docker container will run the Subscleaner script according to the specified cron schedule and process the subtitle files in the mounted media directory.

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
```

To get more information on how to add your own containers in YAMS: https://yams.media/advanced/add-your-own-containers/

## Contributing

Contributions are welcome! If you have any suggestions or improvements, feel free to fork the repository and submit a pull request.

## License

Subscleaner is licensed under the GNU General Public License v3.0 or later. See the [LICENSE](https://gitlab.com/rogs/subscleaner/-/blob/master/LICENSE) file for more details.

## Acknowledgments

This repository is a rewrite of this Github repository: https://github.com/FraMecca/subscleaner.

Thanks to [FraMecca](https://github.com/FraMecca/) in Github!
