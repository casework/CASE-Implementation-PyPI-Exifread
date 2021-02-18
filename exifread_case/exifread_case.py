#!/usr/bin/env python3
# -*- coding: utf-8 -*

import os
import hashlib
import argparse
import exifread


parser = argparse.ArgumentParser()
parser.add_argument("file", help="file to extract exif from")
args = parser.parse_args()


def file_information(filepath):
    try:
        md5sum = hashlib.md5(open(filepath, "rb").read())
        file_stats = os.stat(filepath)
        print(f'File_name:          {filepath}')
        print(f'Size:               {file_stats.st_size}')
        print(f'MD5:                {md5sum.hexdigest()} \n')
    except IOError as io_e:
        print(io_e)
    except ValueError as v_e:
        print(v_e)


def get_exif(file):
    file = open(file, 'rb')
    tags = exifread.process_file(file)
    return tags


def print_exif(tags):
    for tag in tags:
        print(f'{tag} : {tags[tag]}')


def main():
    print(f'Exifread version {exifread.__version__}\n')
    file_information(args.file)
    tags = get_exif(args.file)
    print_exif(tags)


if __name__ == "__main__":
    main()

