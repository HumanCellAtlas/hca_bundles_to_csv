# HCA bundles to CSV

Given a directory of bundles checked out from the datastore, this script will collect all the
metadata into a single CSV file, one row per bundle.

You can use the config file to filter properties and control the ordering of metadata properties in the output file.

If you prefer tab delimited, name the output file with a `.tab` suffix.

# Usage

`python bundle_2_csv.py <path to bundle directory> bundles.tab`
