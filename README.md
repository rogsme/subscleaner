# Subscleaner

<p align="center">
  <img src="https://gitlab.com/uploads/-/system/project/avatar/55502917/logo.jpg" alt="subscleaner"/>
</p>

Subscleaner is a Python script that removes advertisements from subtitle files. It's designed to help you enjoy your favorite shows and movies without the distraction of unwanted ads in the subtitles.

## Features

- Removes a predefined list of advertisement patterns from subtitle files.
- Supports various subtitle formats through the pysrt library.
- Automatically detects the encoding of subtitle files using chardet.

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

## Contributing

Contributions are welcome! If you have any suggestions or improvements, feel free to fork the repository and submit a pull request.

## License

Subscleaner is licensed under the GNU General Public License v3.0 or later. See the [LICENSE](https://gitlab.com/rogs/subscleaner/-/blob/master/LICENSE) file for more details.

## Acknowledgments

This repository is a rewrite of this Github repository: https://github.com/FraMecca/subscleaner.

Thanks to [FraMecca](https://github.com/FraMecca/) in Github!
