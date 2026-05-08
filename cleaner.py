#!/usr/bin/env python3

### HEADER ##################################################################################################################
## Copyright (C) 2026 David Perez - All Rights Reserved
## Unauthorized copying of this software, via any medium is strictly prohibited.
## Proprietary and confidential.
##
## File: cleaner.py
## Author: David Perez <davidperez.code@gmail.com>
## Create date: 2026/03/19
## Description: Utility class for removing temporary files and directories, including cache data.
### END HEADER ##############################################################################################################

__version__ = "1.0.0"
__author__ = "David Perez"
__email__ = "davidperez.code@gmail.com"

MODULE_NAME = "cleaner"

import os
import argparse
import shutil
import sys

def show_version():
    '''
        Show software information
    '''
    print(f"{MODULE_NAME} version: {__version__}")
    sys.exit(0)

def arg_parse():
    '''
        Arguments parse
    '''
    parser = argparse.ArgumentParser(description='Utility class for removing temporary files and directories, including cache data.')
    parser.add_argument('--root_dir', default='.', help='Root directory to start cleaning. Default: current directory.')
    parser.add_argument('--version', default=False, action='store_true', dest='version', help='Show version')
    parser.add_argument('--verbose', default=False, action='store_true', dest='verbose', help='Execute in debug mode')
    args = parser.parse_args()

    return args

class Cleaner:
    """
    Utility class for removing temporary files and directories, including cache data.
    """
    @staticmethod
    def remove_pycache(root_dir: str = "."):
        """
        Recursively find and remove all __pycache__ directories under root_dir.
        """
        removed_count = 0
        for dirpath, dirnames, filenames in os.walk(root_dir):
            if '__pycache__' in dirnames:
                pycache_path = os.path.join(dirpath, '__pycache__')
                try:
                    shutil.rmtree(pycache_path)
                    print(f"Removed: {pycache_path}")
                    removed_count += 1

                except Exception as e:
                    print(f"Failed to remove {pycache_path}: {e}")

        if removed_count == 0:
            print("No __pycache__ directories found.")

        else:
            print(f"Removed {removed_count} __pycache__ directories.")

if __name__ == "__main__":
    args = arg_parse()
    if args.version:
        show_version()
        sys.exit(0)

    root_dir = args.root_dir
    Cleaner.remove_pycache(root_dir)
