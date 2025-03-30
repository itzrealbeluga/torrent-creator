import sys
import os
import hashlib
import bencodepy as bencode
import argparse
import logging
import time
from dotenv import load_dotenv, set_key
from pathlib import Path
import urllib.parse
import getpass
from tqdm import tqdm

PIECE_SIZES = {
    "1": 2**18,  # 256 KB
    "2": 2**19,  # 512 KB
    "3": 2**20,  # 1 MB
    "4": 2**21,  # 2 MB
    "5": 2**22,  # 4 MB
    "6": 2**23,  # 8 MB
    "7": 2**24,  # 16 MB
}

def get_env_file_path():
    if sys.platform.startswith("win"):
        env_dir = Path("C:/torrent-creator")
        env_dir.mkdir(parents=True, exist_ok=True)
        return env_dir / '.env'
    elif sys.platform.startswith("linux"):
        env_dir = Path(f"/home/{getpass.getuser()}/torrent-creator")
        env_dir.mkdir(parents=True, exist_ok=True)
        return env_dir / '.env'
    return None

ENV_FILE = get_env_file_path()

def validate_env():
    required_keys = {
        "TORRENT_OUTPUT_PATH": str,
        "ANNOUNCE_URL": str,
        "PRINT_MAGNET_URL": lambda x: x.lower() in ("true", "false"),
        "PLATFORM": lambda x: x in ("1", "2"),
        "PIECE_SIZE": lambda x: x.isdigit() and int(x) in PIECE_SIZES.values(),
        "TRACKER_TYPE": lambda x: x in ("1", "2")
    }
    updated = False
    for key, check in required_keys.items():
        value = os.getenv(key)
        if not value or (callable(check) and not check(value)):
            if key == "TORRENT_OUTPUT_PATH":
                val = input("Enter path to save .torrent files: ").strip()
            elif key == "ANNOUNCE_URL":
                val = input("Enter announce URL: ").strip()
            elif key == "PRINT_MAGNET_URL":
                val = input("Print magnet URI after creation? (true/false): ").strip().lower()
            elif key == "PLATFORM":
                val = input("Select platform [1=Windows, 2=Linux]: ").strip()
            elif key == "PIECE_SIZE":
                print("Select torrent piece size:")
                for k, size in PIECE_SIZES.items():
                    print(f"{k}. {size // 1024} KB")
                choice = input("Enter choice [1-7]: ").strip()
                val = str(PIECE_SIZES.get(choice, 2**20))
            elif key == "TRACKER_TYPE":
                val = input("Enter tracker type [1=Public, 2=Private]: ").strip()
            set_key(str(ENV_FILE), key, val)
            updated = True
    if updated:
        load_dotenv(dotenv_path=ENV_FILE, override=True)

def prompt_env_setup():
    output_path = input("Enter the path where .torrent files should be saved: ").strip()
    announce_url = input("Enter the announce URL for the torrent tracker: ").strip()
    print_magnet = input("Print magnet URI after creation? (true/false): ").strip().lower()
    platform = input("Select platform [1=Windows, 2=Linux]: ").strip()

    print("\nPublic Tracker vs Private Tracker:")
    print("1. Public Tracker:")
    print("   - DHT, PeX, and LSD are enabled.")
    print("   - Anyone can join and download torrents.")
    print("2. Private Tracker:")
    print("   - DHT, PeX, and LSD are disabled.")
    print("   - Access is restricted to invited users.")
    
    tracker_type = input("Enter tracker type [1=Public, 2=Private]: ").strip()
    
    print("Select torrent piece size:")
    for key, size in PIECE_SIZES.items():
        print(f"{key}. {size // 1024} KB")
    piece_size_choice = input("Enter choice [1-7]: ").strip()
    piece_size = PIECE_SIZES.get(piece_size_choice, 2**20)
    
    with open(ENV_FILE, "w") as f:
        f.write(f"TORRENT_OUTPUT_PATH={output_path or './torrents'}\n")
        f.write(f"ANNOUNCE_URL={announce_url or 'http://tracker.opentrackr.org:1337/announce'}\n")
        f.write(f"PRINT_MAGNET_URL={print_magnet or 'false'}\n")
        f.write(f"PLATFORM={platform or '2'}\n")
        f.write(f"TRACKER_TYPE={tracker_type or '2'}\n")
        f.write(f"PIECE_SIZE={piece_size}\n")

if not ENV_FILE.exists():
    prompt_env_setup()

load_dotenv(dotenv_path=ENV_FILE)
validate_env()

def update_env_var(key: str, value: str):
    set_key(str(ENV_FILE), key, value)
    logging.info(f"{key} updated to: {value}")

def detect_platform(path):
    if path:
        if '\\' in path:
            logging.info("Windows Platform Detected")
            return "Windows"
        elif '/' in path:
            logging.info("Linux Platform Detected")
            return "Linux"
    return "Unknown"

def show_current_path():
    path = os.getenv("TORRENT_OUTPUT_PATH")
    logging.info(f'Current path for .torrent file output: {path}' if path else 'TORRENT_OUTPUT_PATH not found in .env')

def show_current_url():
    url = os.getenv("ANNOUNCE_URL")
    logging.info(f'Current announce URL: {url}' if url else 'ANNOUNCE_URL not found in .env')

def print_help():
    logging.info("""Usage:
    - torrent-creator.py -p : Show current path for .torrent file output.
    - torrent-creator.py -a : Show current announce URL.
    - torrent-creator.py -t : Show trackers from an existing torrent file.
    - torrent-creator.py -l : List files in the torrent directory.
    - torrent-creator.py -o [path] : Override output directory.
    - torrent-creator.py -a [url] : Override announce URL.
    - torrent-creator.py --ps [size] : Override piece size (bytes).
    - torrent-creator.py --reset-env : Reconfigure the .env file.
    - torrent-creator.py -set [-p | -a | --ps | --platform | --magnet | --tracker-type]
    - torrent-creator.py <file_or_folder> : Create a torrent using .env or overrides.

Example:
    python torrent-creator.py --output "/path/to/output" --announce "http://tracker.example.com/announce" --ps 1048576 /path/to/video
    """)

def generate_magnet(info_dict, announce_url):
    info_encoded = bencode.encode(info_dict)
    info_hash = hashlib.sha1(info_encoded).hexdigest()
    name = urllib.parse.quote(info_dict['name'])
    tracker = urllib.parse.quote(announce_url)
    return f"magnet:?xt=urn:btih:{info_hash}&dn={name}&tr={tracker}"

def create_torrent(path, announce_url, torrent_output_path, piece_size, print_magnet=False):
    pieces = []
    file_entries = []
    
    def collect_files(directory):
        for root, _, files in os.walk(directory):
            for name in files:
                full_path = os.path.join(root, name)
                relative_path = os.path.relpath(full_path, start=path)
                file_entries.append((full_path, relative_path.replace("\\", "/").split("/")))

    if os.path.isdir(path):
        collect_files(path)
        total_files = len(file_entries)
        buffer = b''

        with tqdm(total=total_files, desc="Processing files", unit="file", miniters=1) as pbar:
            for full_path, _ in file_entries:
                with open(full_path, 'rb') as f:
                    while True:
                        remaining = piece_size - len(buffer)
                        chunk = f.read(remaining)
                        if not chunk:
                            break
                        buffer += chunk
                        if len(buffer) == piece_size:
                            pieces.append(hashlib.sha1(buffer).digest())
                            buffer = b''
                if len(buffer) > 0:
                    pieces.append(hashlib.sha1(buffer).digest())
                pbar.update(1)

        info_dict = {
            'name': os.path.basename(os.path.abspath(path)),
            'piece length': piece_size,
            'private': 1,
            'pieces': b''.join(pieces),
            'files': []
        }
        for full_path, rel_path_parts in file_entries:
            length = os.path.getsize(full_path)
            info_dict['files'].append({'length': length, 'path': rel_path_parts})

    else:
        file_size = os.path.getsize(path)
        num_pieces = (file_size + piece_size - 1) // piece_size
        pieces = []
        with open(path, 'rb') as f:
            with tqdm(total=num_pieces, desc="Processing file", unit="piece", miniters=1) as pbar:
                for _ in range(num_pieces):
                    piece = f.read(piece_size)
                    pieces.append(hashlib.sha1(piece).digest())
                    pbar.update(1)

        info_dict = {
            'name': os.path.basename(path),
            'piece length': piece_size,
            'pieces': b''.join(pieces),
            'length': file_size,
            'private': 1,
        }

    tracker_type = os.getenv("TRACKER_TYPE", "2")
    if tracker_type == "1":
        info_dict['private'] = 0
        logging.info("Public tracker detected. DHT, PeX, and LSD are enabled.")
    else:
        info_dict['private'] = 1
        logging.info("Private tracker detected. DHT, PeX, and LSD are disabled.")

    torrent = {
        'announce': announce_url,
        'info': info_dict,
        'created by': 'Torrent-Creator/1.1',
        'creation date': int(time.time())
    }
    torrent_bencoded = bencode.encode(torrent)
    base_name = os.path.basename(os.path.abspath(path))
    output_file = os.path.join(torrent_output_path, base_name + '.torrent')
    os.makedirs(torrent_output_path, exist_ok=True)
    with open(output_file, 'wb') as f:
        f.write(torrent_bencoded)
    logging.info(f'Torrent created at: {output_file}')
    if print_magnet:
        magnet_uri = generate_magnet(info_dict, announce_url)
        logging.info(f'Magnet URI: {magnet_uri}')

def list_files():
    files = os.listdir(".")
    logging.info("Files in the current directory:")
    for file in files:
        logging.info(f"- {file}")
    sys.exit(0)

def show_current_conf():
    logging.info("Current Configuration (.env):")
    for key in ["TORRENT_OUTPUT_PATH", "ANNOUNCE_URL", "PRINT_MAGNET_URL", "PLATFORM", "PIECE_SIZE", "TRACKER_TYPE"]:
        value = os.getenv(key)
        logging.info(f"{key}: {value}")

def main():
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        description='Torrent-Creator/1.1 - A tool to create torrents from files and directories.',
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument('-p', action='store_true', help='Show current path for .torrent file output.')
    parser.add_argument('-a', '--announce', help='Override announce URL.')
    parser.add_argument('-o', '--output', help='Override output directory.')
    parser.add_argument('--ps', '--piece-size', type=int, help='Override piece size (bytes).')
    parser.add_argument('--platform', choices=["1", "2"], help='Override platform [1=Windows, 2=Linux].')
    parser.add_argument('--magnet', action='store_true', help='Print magnet URI after creation.')
    parser.add_argument('--reset-env', action='store_true', help='Reconfigure the .env file.')
    parser.add_argument('-set', action='store_true', help='Set environment variables interactively.')
    parser.add_argument('-t', '--trackers', action='store_true', help='Show trackers from an existing torrent file.')
    parser.add_argument('-l', '--list', action='store_true', help='List files in the torrent directory.')
    parser.add_argument('--tracker-type', choices=["1", "2"], help="Set tracker type: 1=Public, 2=Private.")
    parser.add_argument('-current-conf', action='store_true', help="Show current configuration from .env")
    parser.add_argument('filename', nargs='?', help='File or folder to create a torrent from.')

    args = parser.parse_args()

    if args.reset_env:
        prompt_env_setup()
        load_dotenv(dotenv_path=ENV_FILE, override=True)
        validate_env()
        logging.info("Reconfigured .env file.")
        sys.exit(0)

    if args.set:
        if args.output:
            update_env_var("TORRENT_OUTPUT_PATH", args.output)
        elif args.announce:
            update_env_var("ANNOUNCE_URL", args.announce)
        elif args.ps:
            update_env_var("PIECE_SIZE", str(args.ps))
        elif args.platform:
            update_env_var("PLATFORM", str(args.platform))
        elif args.magnet:
            update_env_var("PRINT_MAGNET_URL", args.magnet.lower())
        elif args.tracker_type:
            update_env_var("TRACKER_TYPE", args.tracker_type)
        else:
            print("Choose what to set:\n1. Output Path\n2. Announce URL\n3. Piece Size\n4. Platform\n5. Magnet Output\n6. Tracker Type")
            choice = input("Enter choice number: ").strip()
            if choice == '1':
                val = input("Enter new output path: ").strip()
                update_env_var("TORRENT_OUTPUT_PATH", val)
            elif choice == '2':
                val = input("Enter new announce URL: ").strip()
                update_env_var("ANNOUNCE_URL", val)
            elif choice == '3':
                print("Choose piece size:")
                for k, v in PIECE_SIZES.items():
                    print(f"{k}. {v // 1024} KB")
                pick = input("Enter choice: ").strip()
                update_env_var("PIECE_SIZE", str(PIECE_SIZES.get(pick, 1048576)))
            elif choice == '4':
                val = input("Enter platform [1=Windows, 2=Linux]: ").strip()
                update_env_var("PLATFORM", val)
            elif choice == '5':
                val = input("Print magnet URI? (true/false): ").strip()
                update_env_var("PRINT_MAGNET_URL", val.lower())
            elif choice == '6':
                val = input("Enter tracker type [1=Public, 2=Private]: ").strip()
                update_env_var("TRACKER_TYPE", val)
        sys.exit(0)

    if args.current_conf:
        show_current_conf()
        sys.exit(0)

    if not sys.argv[1:]:
        print_help()
        sys.exit(0)

    if args.p:
        show_current_path()
        sys.exit(0)

    if args.list:
        list_files()

    if args.trackers:
        if not args.filename:
            logging.error('Please provide the path to an existing torrent file using: torrent-creator.py -t <file.torrent>')
            sys.exit(1)
        try:
            with open(args.filename, 'rb') as torrent_file:
                torrent_data = bencode.decode(torrent_file.read())
                if b'announce-list' in torrent_data:
                    logging.info("Trackers in the existing torrent file:")
                    for tracker_list in torrent_data[b'announce-list']:
                        logging.info(f"- {tracker_list[0].decode()}")
                elif b'announce' in torrent_data:
                    logging.info(f"- {torrent_data[b'announce'].decode()}")
                else:
                    logging.info('No trackers found in the existing torrent file.')
        except Exception as e:
            logging.error(f'Failed to read torrent file: {e}')
        sys.exit(0)

    if args.filename:
        announce_url = args.announce or os.getenv("ANNOUNCE_URL")
        output_path = args.output or os.getenv("TORRENT_OUTPUT_PATH")
        print_magnet = os.getenv("PRINT_MAGNET_URL", "false").lower() == "true"
        piece_size = args.ps or int(os.getenv("PIECE_SIZE", 1048576))

        if not announce_url or not output_path:
            logging.error("Both ANNOUNCE_URL and TORRENT_OUTPUT_PATH must be set via .env or command line.")
            sys.exit(1)

        if not os.path.exists(args.filename):
            logging.error("The specified file or directory does not exist.")
            sys.exit(1)

        detect_platform(output_path)
        create_torrent(args.filename, announce_url, output_path, piece_size, print_magnet)
        sys.exit(0)

    logging.error('Invalid arguments. Use -h for help.')
    sys.exit(1)

if __name__ == "__main__":
    main()
