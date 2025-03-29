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


