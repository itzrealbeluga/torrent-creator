# Torrent Creator

Torrent Creator is a Python CLI tool that allows users to create torrent files easily. It supports both single-file and multi-file torrents, platform detection (Windows/Linux), piece size selection, and more. It also generates magnet URIs based on user preferences.

## Features

- **Create single-file or multi-file torrents**: Supports generating torrents from directories and individual files.
- **Platform Detection**: Automatically detects whether the script is running on Windows or Linux and stores configuration (`.env`) in the appropriate location.
  - **Windows**: `.env` file created in `C:/torrent-creator/.env`
  - **Linux**: `.env` file created in `/home/<username>/.env`
- **Configurable Piece Size**: Supports customizable piece size from 256 KB to 16 MB.
- **Magnet URI Generation**: Optionally prints a magnet URI after the torrent is created.
- **Override Configuration via CLI**: Allows overriding `.env` values like output path, announce URL, piece size, and more via command-line arguments.
- **Interactive Setup**: On the first run, the script will prompt the user for necessary configurations and store them in the `.env` file.
- **Reset Configuration**: Reset the `.env` file and reconfigure all options using `--reset-env`.

## Installation

### Requirements

- Python 3.x
- `bencodepy`: For creating torrent files.
- `python-dotenv`: For reading and writing the `.env` configuration file.

To install the required dependencies, run:

```bash
pip install bencodepy python-dotenv


Usage
Initial Setup
The first time you run the script, it will detect the platform (Windows/Linux) and ask for the following configurations:

Path to save .torrent files

Announce URL for the torrent tracker

Whether to print the magnet URI after creation

Select platform: 1 for Windows, 2 for Linux

Select piece size: Options from 256 KB to 16 MB

Commands
Show Current Path:

bash
Copy
python torrent-creator.py -p
Displays the current path where the .torrent files will be saved.

Show Current Announce URL:

bash
Copy
python torrent-creator.py -a
Displays the current announce URL.

Override Output Path:

bash
Copy
python torrent-creator.py -o [path]
Override the output path for where the .torrent file will be saved.

Override Announce URL:

bash
Copy
python torrent-creator.py -a [url]
Override the announce URL for the torrent tracker.

Override Piece Size:

bash
Copy
python torrent-creator.py --ps [size]
Override the piece size in bytes. Valid values are powers of 2 ranging from 256 KB to 16 MB.

Generate a Torrent:

bash
Copy
python torrent-creator.py [path_to_file_or_directory]
Generate a torrent for the specified file or directory.

Show Trackers from an Existing Torrent File:

bash
Copy
python torrent-creator.py -t [torrent_file]
Displays the trackers from an existing .torrent file.

List Files in the Directory:

bash
Copy
python torrent-creator.py -l
Lists all files in the current directory.

Reset and Reconfigure .env:

bash
Copy
python torrent-creator.py --reset-env
Reset and reconfigure the .env file with new values.

Set Configuration Values Individually:

bash
Copy
python torrent-creator.py -set -p [new_output_path]
Set individual values like output path, announce URL, piece size, and more. The script will prompt for missing or invalid values.