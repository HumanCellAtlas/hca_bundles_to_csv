
from hca_bundle_tools.file_metadata_to_csv import Flatten, MissingSchemaTypeError, MissingFileTypeError, \
    MissingFileNameError, \
    MissingDescribedByError, convert_bundle_dirs
import unittest
from unittest import TestCase
from unittest.mock import patch
import filecmp
import os, sys

class TestSchemaTemplate(TestCase):

    def setUp(self):
        self.doc1 = {
            "describedBy" : "foo/seq_file",
            "schema_type" : "file",
            "provenance" : {
                "document_id" : "file_id1",
            },
            "file_core" : {
                "file_name" : "test_file.fastq.gz",
                "file_format": "fastq.gz"},
            "foo": "bar 1",
        }

        self.doc2 = {
            "describedBy" : "foo/donor",
            "schema_type" : "biomaterial",
            "provenance" : {
                "document_id" : "bm_id1",
            },
            "name": "bob",
            "list": ["xxx","yyy"],
            "nested": {
                "nest_value" : "zzz",
                "nest_list": ["xxx", "yyy"],
                "nest_list_dic": [ {"yyy" : "zzz"}]
                }
            }

    def test_flatten(self):

        flattener = Flatten()

        flattener.add_bundle_files_to_row([self.doc1, self.doc2])
        output = 'test1_tmp.csv'
        flattener.dump(filename=output)
        self.assertTrue(filecmp.cmp('test1.csv', output))
        os.remove(output)

        output = 'test1_tmp.tsv'
        flattener.dump(filename=output, delim='\t')
        self.assertTrue(filecmp.cmp('test1.tsv', output))
        os.remove(output)


    def test_flatten_with_dirname(self):

        flattener = Flatten()

        flattener.add_bundle_files_to_row([self.doc1, self.doc2], dir_name="1234-aaaa")
        output = 'test2_tmp.csv'
        flattener.dump(filename=output)
        self.assertTrue(filecmp.cmp('test2.csv', output))
        os.remove(output)


    def test_flatten_with_default_filter(self):

        flattener = Flatten()

        doc3 = {
            "describedBy" : "foo/seq_file",
            "schema_type" : "file",
            "provenance" : {
                "document_id" : "file_id2",
            },
            "file_core" : {
                "file_name" : "test_file.fastq.gz",
                "file_format": "foo_bar.gz"},
            "foo": "bar 1",
        }


        flattener.add_bundle_files_to_row([self.doc1, self.doc2, doc3])
        output = 'test3_tmp.csv'
        flattener.dump(filename=output)
        self.assertTrue(filecmp.cmp('test1.csv', output))
        os.remove(output)

    def test_flatten_with_custom_filter(self):

        flattener = Flatten(format_filter=["foo_bar.gz"])

        doc3 = {
            "describedBy" : "foo/seq_file",
            "schema_type" : "file",
            "provenance" : {
                "document_id" : "file_id2",
            },
            "file_core" : {
                "file_name" : "test_file.fastq.gz",
                "file_format": "foo_bar.gz"},
            "foo": "bar 1",
        }


        flattener.add_bundle_files_to_row([self.doc1, self.doc2, doc3])
        output = 'test4_tmp.csv'
        flattener.dump(filename=output)
        self.assertTrue(filecmp.cmp('test4.csv', output))
        os.remove(output)

    def test_ignore_links_bundle(self):

        flattener = Flatten()

        doc3 = {
            "schema_type" : "link_bundle",
        }

        flattener.add_bundle_files_to_row([self.doc1, self.doc2, doc3])
        output = 'test5_tmp.csv'
        flattener.dump(filename=output)
        self.assertTrue(filecmp.cmp('test1.csv', output))
        os.remove(output)

    def test_no_schema_type(self):

        flattener = Flatten()

        doc1 = {}
        doc2 = {}

        with self.assertRaises(MissingSchemaTypeError):
            flattener.add_bundle_files_to_row([doc1, doc2])


    def test_no_file_uuid(self):

        flattener = Flatten()

        doc1 = { "schema_type" : "file"}
        doc2 = { "schema_type" : "biomaterial"}

        with self.assertRaises(MissingFileTypeError):
            flattener.add_bundle_files_to_row([doc1, doc2])

    def test_no_file_name(self):

        flattener = Flatten()

        doc1 = { "schema_type" : "file",
                 "provenance": {
                     "document_id": "file_id1",
                 },

                 }
        doc2 = { "schema_type" : "biomaterial"}

        with self.assertRaises(MissingFileNameError):
            flattener.add_bundle_files_to_row([doc1, doc2])

    def test_no_described_by(self):

        flattener = Flatten()

        doc1 = { "schema_type" : "file",
                 "provenance": {
                     "document_id": "file_id1",
                 },
                 "file_core": {
                     "file_name": "test_file.fastq.gz",
                     "file_format": "fastq.gz"}
                 }
        doc2 = { "schema_type" : "biomaterial"}

        with self.assertRaises(MissingDescribedByError):
            flattener.add_bundle_files_to_row([doc1, doc2])


    def test_bundle_parser(self):
        testargs = ["file_metadata_to_csv", "-d", ".", "-o", "bundles_tmp.csv"]
        with patch.object(sys, 'argv', testargs):
             convert_bundle_dirs()
        self.assertTrue(filecmp.cmp('bundles.csv', 'bundles_tmp.csv'))
        os.remove("bundles_tmp.csv")






if __name__ == '__main__':
    unittest.main()