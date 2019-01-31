import glob
import json
import csv
import sys
import os
import re
import configparser
import functools

config = configparser.ConfigParser(allow_no_value=True)
config.read('config.ini')
ignore = config["IGNORE"].keys()

def set_value(master, key, value):
    if key not in master:
        master[key] = str(value)
    else:
        existing_values = master[key].split(" || ")
        existing_values.append(str(value))
        uniq = sorted(list(set(existing_values)))
        master[key] = " || ".join(uniq)

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

def cmp_keys(a,b):

    orderings = config["ORDER"]

    best_a = sys.maxsize
    best_b = sys.maxsize

    for idx, val in enumerate(orderings):
        p = re.compile(val)

        match_a = p.match(a)
        match_b = p.match(b)

        if (match_a):
            if (idx < best_a):
                best_a = idx

        if (match_b):
            if (idx < best_b):
                best_b = idx

    if (best_a == best_b):
        if a > b:
            return 1
        elif a < b:
            return -1
        return 0
    return best_a - best_b

def dump(all_keys, all_objects, outfile):
    all_keys.sort(key=functools.cmp_to_key(cmp_keys))

    delim = ','
    if outfile.endswith('.tab') or outfile.endswith('.tsv'):
        delim = '\t'

    with open(outfile, 'w') as csvfile:
        csv_writer = csv.DictWriter(csvfile, all_keys, delim)
        csv_writer.writeheader()
        for obj in all_objects:
            csv_writer.writerow(obj)

def main():

    if len(sys.argv) != 3:
        print('USAGE: python bundles_2_csv.py path_to_bundle_directory output_file')
        sys.exit(1)

    all_objects = []
    all_keys = []

    p = re.compile('(.*)_\d+\.json')
    bundle_dir = sys.argv[1]
    outfile = sys.argv[2]

    uuid4hex = re.compile('^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$', re.I)
    for bundle in os.listdir(bundle_dir):

        if uuid4hex.match(bundle):
            obj = {}
            print("flattening " + bundle)
            obj["bundle_id"] = bundle

            for dir in glob.glob(bundle_dir + os.sep + bundle +  os.sep+ '*.json'):
                head, tail = os.path.split(dir)

                # we don't need links.json
                if "links" in tail:
                    continue

                match = p.match(tail)
                metadoc = json.load(open(dir))
                flatten(obj, metadoc, match.group(1))

            if obj:
                all_keys.extend(obj.keys())
                all_keys = list(set(all_keys))
                all_objects.append(obj)

    dump(all_keys, all_objects, outfile)

if __name__ == '__main__':
    main()