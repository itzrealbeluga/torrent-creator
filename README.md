# Torrent Creator Version 1.1.7

Torrent Creator is a Python-based CLI tool that allows users to easily create torrent files. It supports both single-file and multi-file torrents, customizable torrent piece sizes, and platform detection (Windows/Linux). This tool also generates magnet URIs based on user preferences and allows users to customize the tracker type for private or public trackers.

## Features

- **Create Single-File or Multi-File Torrents**: Supports creating torrents from individual files or entire directories.
- **Platform Detection**: Automatically detects the operating system (Windows or Linux) and saves configuration (`.env`) in the appropriate location.
  - **Windows**: `.env` is saved in `C:/torrent-creator/.env`
  - **Linux**: `.env` is saved in `/home/<username>/torrent-creator/.env`
- **Customizable Piece Size**: Allows selecting a piece size from 256 KB to 16 MB.
- **Magnet URL Generation**: Optionally generates and displays a magnet URL after the torrent is created.
- **Override Configuration via CLI**: Allows overriding the default `.env` values (such as output path, announce URL, piece size, etc.) directly from the command line.
- **Private or Public Tracker Types**: Customizable tracker type with an option to enable/disable DHT, PeX, and LSD based on the tracker type.
- **Reconfigure `.env` File**: Supports resetting and reconfiguring the `.env` file with the `--reset-env` option.


## Installation

To install the tool, run the following command:

```
pip install torrent-creator
```

# Alternatively, you can clone the repository and install it locally:

```
git clone https://github.com/yourusername/torrent-creator.git
cd torrent-creator
python setup.py install
```

## Setup / Configuration

Upon the first run, ``torrent-creator`` will prompt you to configure the following settings:

- **TORRENT_OUTPUT_PATH:** Path where the .torrent files will be saved.

- **ANNOUNCE_URL:** The announce URL for the torrent tracker.

- **PRINT_MAGNET_URL:** Whether to print the magnet URI after creation (true or false).

- **PLATFORM:** The platform (1 for Windows, 2 for Linux).

- **PIECE_SIZE:** The size of each piece in bytes (must be one of the predefined sizes).

- **TRACKER_TYPE:** The type of tracker (1 for public, 2 for private).

## Usage


```    usage: torrent-creator [-h] [-p] [-a ANNOUNCE] [-o OUTPUT] [--ps PS]
                           [--platform PLATFORM] [--magnet] [--reset-env]
                           [-set] [-t] [-l] [--tracker-type {1,2}]
                           [-current-conf] [filename]


positional arguments:
  <filename>/directory              The file or directory to create a torrent from.

optional arguments:
  -h, --help            Show this help message and exit.
  -p                    Show current path for .torrent file output.
  -a ANNOUNCE, --announce ANNOUNCE
                        Override announce URL.
  -o OUTPUT, --output OUTPUT
                        Override output directory.
  --ps PS, --piece-size PS
                        Override piece size (bytes).
  --platform PLATFORM   Override platform (1=Windows, 2=Linux).
  --magnet              Print magnet URI after creation.
  --reset-env           Reconfigure the .env file.
  -set                  Set environment variables interactively.
  -t, --trackers        Show trackers from an existing torrent file.
  -l, --list            List files in the torrent directory.
  --tracker-type {1,2}  Set tracker type: 1=Public, 2=Private.

```



## Last Changes

**Torrent-Creator Version 1.2.0**
- Added progress bar for real-time file and piece processing
- Improved CLI interface with detailed help and usage examples
- Added better error handling and argument validation
- Replaced `.env` management for platform-specific configurations (Windows/Linux)
- Introduced new option to interactively configure environment variables
- Support for multiple tracker URLs in torrent creation
- Enhanced logging functionality for better debugging and user feedback
- Added functionality to show current configuration via `-current-conf`
- Ability to override torrent piece size and output directory via command line
- Fixed env conflict
- other bugs fixed
