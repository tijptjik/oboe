from .config import GLOBAL
from .log import Logger
LOG = Logger("INFO")

import sys
import argparse
import time
from .Vault import Vault
from .Note import Note

def main():
    parser = argparse.ArgumentParser(
        prog="oboe",
        description="Converts an Obsidian vault into HTML")

    parser.add_argument("Vault",
                        metavar="vault",
                        type=str,
                        help="Path to the vault root")

    parser.add_argument("-o", "--output_directory",
                        default="./html",
                        help="Path to place the generated HTML")

    parser.add_argument("-t", "--template",
                        default=None,
                        help="Path to HTML template")

    parser.add_argument("-d", "--sub-directories",
                        nargs="+",
                        default=[],
                        help="Extra sub-directories in vault that you want included")

    parser.add_argument("-f", "--filter",
                        nargs="+",
                        default=[],
                        help="Filter notes by tags")

    parser.add_argument("-e", "--add-file-extensions",
                        action="store_true",
                        help="Whether to include a '.html' extension on links. Useful for viewing locally.")

    parser.add_argument("-l", "--log-level",
                        default=None,
                        help="The level of Oboe's logger")

    parser.add_argument("-b", "--omit-backlink-dash",
                        action="store_false",
                        help="Whether to remove a '- ' before each backlink in html.")

    args = parser.parse_args()

    if args.log_level:
        LOG.set_level(args.log_level)

    GLOBAL.HTML_LINK_EXTENSIONS = args.add_file_extensions
    GLOBAL.BACKLINK_DASH = args.omit_backlink_dash
    GLOBAL.VAULT_ROOT = args.Vault
    GLOBAL.OUTPUT_DIR = args.output_directory

    time_begin = time.time()

    vault = Vault(extra_folders=args.sub_directories, html_template=args.template, filter_list=args.filter)
    vault.export_html()

    time_end = time.time()

    LOG.debug(f"Oboe used {round(time_end - time_begin, 2)}s to finish.")
