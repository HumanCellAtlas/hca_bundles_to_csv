# HCA bundles to CSV

Given a directory of bundles checked out from the datastore, this script will collect all the
metadata into a single CSV file, one row per bundle.

You can use the config file to filter properties and control the ordering of metadata properties in the output file.

If you prefer tab delimited, name the output file with a `.tab` or `.tsv` suffix.

# CLI Usage

`python hca_bundle_tools/file_metadata_to_csv.py -d <path to bundle directory> -o <output file>`

# API Usage

```python
from hca_bundle_tools.file_metadata_to_csv import Flatten

flattener = Flatten()

list_of_metadata_files_from_a_bundle = ...

# add all metadata files from a single bundle, you can keep add more bundles
flattener.add_bundle_files_to_row(list_of_metadata_files_from_a_bundle)

# finally dump all the files you added
flattener.dump(filename='output.csv')

```