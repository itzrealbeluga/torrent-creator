#!/usr/bin/env python3
"""
Torrent-Creator v1.3.0
====================
- Fixed corruption: replaced bencodepy with torf for 100% spec-compliant torrents
- torf handles all bencoding, piece hashing, and multi-file layout correctly
- All original CLI flags preserved
"""

import sys
import os
import argparse
import logging
import time
import getpass
from pathlib import Path
from dotenv import load_dotenv, set_key

try:
    import torf
except ImportError:
    print("[X] torf not installed. Run:  pip install torf")
    sys.exit(1)

PIECE_SIZES = {
    "1": 2**18,   # 256 KB
    "2": 2**19,   # 512 KB
    "3": 2**20,   # 1 MB
    "4": 2**21,   # 2 MB
    "5": 2**22,   # 4 MB
    "6": 2**23,   # 8 MB
    "7": 2**24,   # 16 MB
}


# ─── .env location ───────────────────────────────────────────────────────────
def get_env_file_path() -> Path:
    if sys.platform.startswith("win"):
        d = Path("C:/torrent-creator")
    else:
        d = Path(f"/home/{getpass.getuser()}/torrent-creator")
    d.mkdir(parents=True, exist_ok=True)
    return d / ".env"

ENV_FILE = get_env_file_path()


# ─── env helpers ─────────────────────────────────────────────────────────────
def load_and_parse_env() -> dict:
    env = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if line and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def prompt_env_setup():
    output_path   = input("Enter the path where .torrent files should be saved: ").strip()
    announce_url  = input("Enter the announce URL for the tracker: ").strip()
    print_magnet  = input("Print magnet URI after creation? (true/false): ").strip().lower()
    platform      = input("Select platform [1=Windows, 2=Linux]: ").strip()

    print("\nTracker type:")
    print("1. Public  — DHT, PeX, LSD enabled")
    print("2. Private — DHT, PeX, LSD disabled")
    tracker_type = input("Enter tracker type [1=Public, 2=Private]: ").strip()

    print("\nSelect torrent piece size:")
    for k, size in PIECE_SIZES.items():
        print(f"  {k}. {size // 1024} KB")
    choice     = input("Enter choice [1-7]: ").strip()
    piece_size = PIECE_SIZES.get(choice, 2**20)

    with open(ENV_FILE, "w") as f:
        f.write(f"TORRENT_OUTPUT_PATH={output_path or './torrents'}\n")
        f.write(f"ANNOUNCE_URL={announce_url or 'http://tracker.opentrackr.org:1337/announce'}\n")
        f.write(f"PRINT_MAGNET_URL={print_magnet or 'false'}\n")
        f.write(f"PLATFORM={platform or '1'}\n")
        f.write(f"TRACKER_TYPE={tracker_type or '2'}\n")
        f.write(f"PIECE_SIZE={piece_size}\n")
    load_dotenv(dotenv_path=ENV_FILE, override=True)


def validate_env():
    required = {
        "TORRENT_OUTPUT_PATH": lambda x: bool(x),
        "ANNOUNCE_URL":        lambda x: x.startswith("http"),
        "PRINT_MAGNET_URL":    lambda x: x.lower() in ("true", "false"),
        "PLATFORM":            lambda x: x in ("1", "2"),
        "PIECE_SIZE":          lambda x: x.isdigit(),
        "TRACKER_TYPE":        lambda x: x in ("1", "2"),
    }
    updated = False
    for key, check in required.items():
        value = os.getenv(key, "")
        if not value or not check(value):
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
                    print(f"  {k}. {size // 1024} KB")
                choice = input("Enter choice [1-7]: ").strip()
                val = str(PIECE_SIZES.get(choice, 2**20))
            elif key == "TRACKER_TYPE":
                val = input("Enter tracker type [1=Public, 2=Private]: ").strip()
            else:
                val = ""
            set_key(str(ENV_FILE), key, val)
            updated = True
    if updated:
        load_dotenv(dotenv_path=ENV_FILE, override=True)


def reset_env_file():
    logging.info("Reconfiguring .env…")
    prompt_env_setup()
    logging.info("Done.")


def update_env_var(key: str, value: str):
    set_key(str(ENV_FILE), key, value)
    load_dotenv(dotenv_path=ENV_FILE, override=True)
    logging.info(f"{key} updated to: {value}")


def show_current_conf():
    for key in ["TORRENT_OUTPUT_PATH","ANNOUNCE_URL","PRINT_MAGNET_URL",
                "PLATFORM","PIECE_SIZE","TRACKER_TYPE"]:
        logging.info(f"{key}: {os.getenv(key,'(not set)')}")


# ─── core: create torrent via torf ───────────────────────────────────────────
def create_torrent(path: str, announce_url: str, torrent_output_path: str,
                   piece_size: int, print_magnet: bool = False) -> str:
    """
    Create a valid .torrent file for *path* (file or folder).
    Uses torf for spec-compliant bencoding — no corruption.
    Returns the path to the written .torrent file.
    """
    tracker_type = os.getenv("TRACKER_TYPE", "2")
    is_private   = (tracker_type != "1")

    if is_private:
        logging.info("Private tracker — DHT/PeX/LSD disabled (private=1)")
    else:
        logging.info("Public tracker — DHT/PeX/LSD enabled (private=0)")

    t = torf.Torrent(
        path=path,
        trackers=[announce_url],
        private=is_private,
        piece_size=piece_size,
        created_by="Torrent-Creator/1.3.0",
        creation_date=time.time(),
    )

    logging.info("Hashing pieces…")
    def _cb(torrent, filepath, pieces_done, pieces_total):
        pct = int(pieces_done / pieces_total * 100) if pieces_total else 0
        sys.stdout.write(f"\r  Hashing: {pct:3d}%  ({pieces_done}/{pieces_total} pieces)  ")
        sys.stdout.flush()
    t.generate(callback=_cb, interval=0.5)
    sys.stdout.write("\n")

    os.makedirs(torrent_output_path, exist_ok=True)
    base_name   = os.path.basename(os.path.abspath(path))
    output_file = os.path.join(torrent_output_path, base_name + ".torrent")
    t.write(output_file, overwrite=True)
    logging.info(f"Torrent written: {output_file}")

    if print_magnet:
        logging.info(f"Magnet URI: {t.magnet()}")

    return output_file


def show_trackers(torrent_file: str):
    try:
        t = torf.Torrent.read(torrent_file)
        for tracker_list in (t.trackers or []):
            for tr in tracker_list:
                logging.info(f"  Tracker: {tr}")
    except Exception as e:
        logging.error(f"Failed to read torrent: {e}")


def list_files_cmd():
    for f in sorted(os.listdir(".")):
        logging.info(f"  {f}")


def print_help():
    logging.info("""
Torrent-Creator v1.3.0  (uses torf for correct bencoding)

Usage:
  torrent-creator.py <file_or_folder>         Create torrent
  torrent-creator.py -p                        Show output path
  torrent-creator.py -a                        Show announce URL
  torrent-creator.py -t <file.torrent>         Show trackers
  torrent-creator.py -l                        List current directory
  torrent-creator.py -o <path>                 Override output dir
  torrent-creator.py --announce <url>          Override announce URL
  torrent-creator.py --ps <bytes>              Override piece size
  torrent-creator.py --reset-env               Reconfigure .env
  torrent-creator.py -set [-o|-a|--ps|...]     Set .env values
  torrent-creator.py -current-conf             Show current config

Example:
  python torrent-creator.py "E:\\Music-Rips\\MyAlbum"
""")


# ─── main ─────────────────────────────────────────────────────────────────────
def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    # Bootstrap .env
    if not ENV_FILE.exists():
        prompt_env_setup()
    load_dotenv(dotenv_path=ENV_FILE)
    validate_env()

    parser = argparse.ArgumentParser(
        description="Torrent-Creator v1.3",
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-p",  action="store_true",     help="Show current output path.")
    parser.add_argument("-a",  "--announce",            help="Override announce URL.")
    parser.add_argument("-o",  "--output",              help="Override output directory.")
    parser.add_argument("--ps","--piece-size", type=int,help="Override piece size (bytes).")
    parser.add_argument("--platform", choices=["1","2"],help="Override platform.")
    parser.add_argument("--magnet", action="store_true",help="Print magnet URI.")
    parser.add_argument("--reset-env", action="store_true", help="Reconfigure .env.")
    parser.add_argument("-set", action="store_true",    help="Set env vars interactively.")
    parser.add_argument("-t","--trackers",action="store_true",help="Show trackers in torrent.")
    parser.add_argument("-l","--list",   action="store_true", help="List directory files.")
    parser.add_argument("--tracker-type",choices=["1","2"],   help="1=Public, 2=Private.")
    parser.add_argument("-current-conf", action="store_true", help="Show current config.")
    parser.add_argument("filename", nargs="?",          help="File or folder to torrentize.")

    args = parser.parse_args()

    if args.reset_env:
        reset_env_file(); sys.exit(0)

    if args.set:
        if args.output:       update_env_var("TORRENT_OUTPUT_PATH", args.output)
        elif args.announce:   update_env_var("ANNOUNCE_URL", args.announce)
        elif args.ps:         update_env_var("PIECE_SIZE", str(args.ps))
        elif args.platform:   update_env_var("PLATFORM", args.platform)
        elif args.tracker_type: update_env_var("TRACKER_TYPE", args.tracker_type)
        else:
            print("1. Output Path  2. Announce URL  3. Piece Size  4. Tracker Type")
            choice = input("Choice: ").strip()
            if choice == "1":
                update_env_var("TORRENT_OUTPUT_PATH", input("New path: ").strip())
            elif choice == "2":
                update_env_var("ANNOUNCE_URL", input("New announce URL: ").strip())
            elif choice == "3":
                for k, v in PIECE_SIZES.items(): print(f"  {k}. {v//1024} KB")
                p = input("Choice: ").strip()
                update_env_var("PIECE_SIZE", str(PIECE_SIZES.get(p, 1048576)))
            elif choice == "4":
                update_env_var("TRACKER_TYPE", input("[1=Public, 2=Private]: ").strip())
        sys.exit(0)

    if getattr(args, "current_conf", False):
        show_current_conf(); sys.exit(0)

    if not sys.argv[1:]:
        print_help(); sys.exit(0)

    if args.p:
        logging.info(f"Output path: {os.getenv('TORRENT_OUTPUT_PATH')}"); sys.exit(0)

    if args.list:
        list_files_cmd(); sys.exit(0)

    if args.trackers:
        if not args.filename:
            logging.error("Provide path to .torrent file."); sys.exit(1)
        show_trackers(args.filename); sys.exit(0)

    if args.filename:
        announce_url = args.announce or os.getenv("ANNOUNCE_URL")
        output_path  = args.output  or os.getenv("TORRENT_OUTPUT_PATH")
        print_magnet = args.magnet  or os.getenv("PRINT_MAGNET_URL","false").lower()=="true"
        piece_size   = args.ps      or int(os.getenv("PIECE_SIZE", str(2**20)))

        if args.tracker_type:
            os.environ["TRACKER_TYPE"] = args.tracker_type

        if not announce_url or not output_path:
            logging.error("ANNOUNCE_URL and TORRENT_OUTPUT_PATH must be set."); sys.exit(1)
        if not os.path.exists(args.filename):
            logging.error("File or folder not found."); sys.exit(1)

        create_torrent(args.filename, announce_url, output_path, piece_size, print_magnet)
        sys.exit(0)

    logging.error("Invalid arguments. Use -h for help."); sys.exit(1)


if __name__ == "__main__":
    main()
