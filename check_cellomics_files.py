#!/usr/bin/env python

"""
Given a list of Cellomics files, this script produces prints a report to stdout of any files
that are missing. A well will be flagged as missing if any of the individual channel files are missing.

Usage: 

check_cellomics_files.py <file_list> <number_of_fields>

file_list - The path to a file listing each Cellomics tif/TIF file. Each file should be on a new line.
number_of_fields - The number of fields used to capture each well. 

Example:
$ python check_cellomics_files.py my_cellomics_files.txt 9

The above command will check the list of files in my_cellomics_files 

Example output: 

If there are two plates: 123, and 421 and 421 has missing files in well A03, the output will be:

Plate 123
OK!
Plate 421
Missing A03: [11, 12, 13]

This suggests that plate 421, well A03 has missing files for fields 11, 12 and 13.
"""

from microscopium.screens import cellomics
from cytoolz import groupby
import numpy as np
import sys

INPUT_FILE = sys.argv[1]
FIELD_START = 0
FIELD_END = int(sys.argv[2]) - 1

def parse_input_file():
     with open(INPUT_FILE) as file:
         for line in file:
            line = line.strip()
            if line.endswith("tif") or line.endswith("TIF"):
                yield line


def get_plate_well(fn):
    sem = cellomics.cellomics_semantic_filename(fn.strip())
    return sem["plate"], sem["well"]


def get_field(fn):
    sem = cellomics.cellomics_semantic_filename(fn)
    return sem['field']


def check_missing_fields(fns):    
    # get fields present in list
    fields = list(map(get_field, fns))
    
    # find any missing fields in this channel
    start, end = np.min(FIELD_START), np.max(FIELD_END)   
    missing = sorted(set(range(start, end + 1)).difference(fields))
           
    return missing


if __name__ == "__main__":

    group_files = groupby(get_plate_well, parse_input_file())
    sorted_keys = sorted(group_files.keys())

    plate0 = sorted_keys[0][0]
    print("Plate {0}".format(plate0))
    missing_from_plate = 0

    last_plate = plate0
    for key in sorted_keys:
        current_plate = key[0]
        current_well = key[1]
        current_files = group_files[key]

        if(current_plate != last_plate):
            last_plate = current_plate

            if(missing_from_plate == 0):
                print("OK!")

            missing_from_plate = 0
            print("Plate {0}".format(current_plate))

        missing = check_missing_fields(current_files)

        if len(missing) > 0:
            missing_from_plate = missing_from_plate + 1
            print("{0} missing: {1}".format(current_well, missing))
