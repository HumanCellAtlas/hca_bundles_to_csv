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

def set_value_as_new_col(master, key, value):
    if key not in master:
        master[key] = str(value)
    else:
        start, count = key.rsplit(".", 1)
        if count and count.isdigit():
            key = start + ( int(count) + 1)
        else:
            key = key + ".1"

        master[key] = str(value)

def set_value(master, key, value):

    # if config["LAYOUT"] == "multicolumn":
    #     set_value_as_new_col(master, key, value)
    # else:
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
        csv_writer = csv.DictWriter(csvfile, all_keys, delimiter=delim)
        csv_writer.writeheader()
        for obj in all_objects:
            csv_writer.writerow(obj)

def get_file_uuids_from_bundle_dir(bundle_dir, bundle):
    file_uuids = {}
    for file in glob.glob(bundle_dir + os.sep + bundle + os.sep + '*.json'):
        head, filename = os.path.split(file)

        with open(file) as f:
            data = json.load(f)
            if data["schema_type"] == "file":
                file_uuids[filename] = data

    return file_uuids

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


    # read each bundle directory
    for bundle in os.listdir(bundle_dir):

        # ignore any directory that isn't named with a uuid
        if uuid4hex.match(bundle):

            # get all the files
            file_uuids = get_file_uuids_from_bundle_dir(bundle_dir, bundle)

            for file, content in file_uuids.items():
                obj = {}
                print("flattening " + bundle)
                obj["folder"] = bundle
                obj["file_name"] = content["file_core"]["file_name"]
                obj["file_format"] = content["file_core"]["file_format"]


                match = p.match(file)
                schema_name = match.group(1)
                flatten(obj, content, schema_name)

                for dir in glob.glob(bundle_dir + os.sep + bundle +  os.sep+ '*.json'):


                    head, filename = os.path.split(dir)

                    # ignore files if in file per row mode and we don't need links.json
                    if filename in file_uuids or "links" in filename:
                        continue

                    match = p.match(filename)
                    schema_name = match.group(1)
                    metadoc = json.load(open(dir))

                    flatten(obj, metadoc, schema_name)

                all_keys.extend(obj.keys())
                all_keys = list(set(all_keys))
                all_objects.append(obj)

    dump(all_keys, all_objects, outfile)

if __name__ == '__main__':
    main()