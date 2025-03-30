# Torrent Creator Version 1.1.7

Torrent Creator is a Python-based CLI tool that allows users to easily create torrent files. It supports both single-file and multi-file torrents, customizable torrent piece sizes, and platform detection (Windows/Linux). This tool also generates magnet URIs based on user preferences and allows users to customize the tracker type for private or public trackers.

## Features

- **Create Single-File or Multi-File Torrents**: Supports creating torrents from individual files or entire directories.
- **Platform Detection**: Automatically detects the operating system (Windows or Linux) and saves configuration (`.env`) in the appropriate location.
  - **Windows**: `.env` is saved in `C:/torrent-creator/.env`
  - **Linux**: `.env` is saved in `/home/<username>/torrent-creator/.env`
- **Customizable Piece Size**: Allows selecting a piece size from 256 KB to 16 MB.
- **Magnet URI Generation**: Optionally generates and displays a magnet URI after the torrent is created.
- **Override Configuration via CLI**: Allows overriding the default `.env` values (such as output path, announce URL, piece size, etc.) directly from the command line.
- **Private or Public Tracker Types**: Customizable tracker type with an option to enable/disable DHT, PeX, and LSD based on the tracker type.
- **Reconfigure `.env` File**: Supports resetting and reconfiguring the `.env` file with the `--reset-env` option.
- **Debugging**: A `-current-conf` command to print the current configuration.

## Installation

To install the tool, run the following command:

```
pip install torrent-creator
```

