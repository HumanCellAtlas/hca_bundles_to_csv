from itertools import product
from pprint import pprint as pp

import glob
import json
import csv
import sys
import os
import re

ignore = ["describedBy", "schema_type" ]

def set_value(master, key, value):
    if key not in master:
        master[key] = []
    master[key].append(value)
    master[key] = list(set(master[key]))


def flatten (master, obj, parent):
    for key, value in obj.items():
        if key in ignore:
            continue
        if (parent):
            newkey = parent + "." + key
        else:
            newkey = key
        if isinstance(value, dict):
            flatten(master, obj[key], newkey)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    flatten(master, item, newkey)
                else:
                    set_value(master, newkey, item)
        else:
            set_value(master, newkey, value)

def main():

    if len(sys.argv) != 2:
        print('USAGE: python flatten.py path_to_bundle_directory')
        sys.exit(1)

    all_objects = []
    all_keys = []

    p = re.compile('(.*)_\d+\.json')
    bundle_dir = sys.argv[1]

    for bundle in os.listdir(bundle_dir):

        obj = {}

        for dir in glob.glob(bundle +  os.sep+ '*.json'):
            head, tail = os.path.split(dir)

            # we don't need links.json
            if "links" in tail:
                continue

            match = p.match(tail)

            metadoc = json.load(open(dir))
            flatten(obj, metadoc, match.group(1))

        if obj:
            all_keys = list(set(obj.keys()))
            all_objects.append(obj)


    csv_writer = csv.DictWriter(sys.stdout, all_keys)
    csv_writer.writeheader()
    for obj in all_objects:
        csv_writer.writerow(obj)

if __name__ == '__main__':
    main()