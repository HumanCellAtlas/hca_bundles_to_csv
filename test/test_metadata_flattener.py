
from hca_bundle_tools.file_metadata_to_csv import Flatten, MissingSchemaTypeError, MissingFileTypeError, \
    MissingFileNameError, \
    MissingDescribedByError, convert_bundle_dirs
import unittest
from unittest import TestCase
from unittest.mock import patch
import filecmp
import os, sys

BASE_PATH = os.path.dirname(__file__)


class TestSchemaTemplate(TestCase):

    def setUp(self):
        self.doc1 = {
            "describedBy" : "foo/sequence_file",
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

        self.project_doc = {
            "describedBy": "foo/project",
            "schema_type": "project",
            "project_core": {
                "project_short_name": "test short name",
                "project_title": "test title",
                "project_description": "test description"
            },
            "provenance": {
                "document_id": "88888888-8888-8888-8888-888888888888",
                "submission_date": "2018-12-04T18:11:31.185Z",
                "update_date": "2018-12-04T18:11:35.452Z"
            }
        }

        self.default_test_docs = [self.doc1, self.doc2, self.project_doc]

        self.manifest = {
            "bundle": {
                "creator_uid": 8008,
                "files": [
                    {
                        "content-type": "application/json; dcp-type=\"metadata/biomaterial\"",
                        "crc32c": "f258f5b4",
                        "indexed": True,
                        "name": "donor_organism_1.json",
                        "s3_etag": "002a2b1831b6e83d72a83941c40374fc",
                        "sha1": "028b6c7ce3f36d7dc90eb6abaa82dd6cb9a05b08",
                        "sha256": "bacbfc611ae4c2148b589e0e606a4dd6cbbcbfbc031043a9f61a38e1d609d5c0",
                        "size": 1050,
                        "uuid": "350ec5b4-cbe1-4379-b1eb-d63a4dd3f90f",
                        "version": "2018-12-04T181135.586000Z"
                    },
                    {
                        "content-type": "application/gzip; dcp-type=data",
                        "crc32c": "28812498",
                        "indexed": False,
                        "name": "test_file.fastq.gz",
                        "s3_etag": "75c5d405af994644c7d2b382f4444848-46",
                        "sha1": "026b8b4dd24c433e91195fdf5d385aea97c307c0",
                        "sha256": "9daf6a998ef9c6ce183422a816511115fc490add592a1852e866b10b428861c7",
                        "size": 3070190561,
                        "uuid": "99999999-9999-9999-9999-999999999999",
                        "version": "1999-01-00T000000.000000Z"
                    }
                ],
                "uuid": "00000000-0000-0000-0000-000000000000",
                "version": "1999-01-00T000000.000000Z"
            }
        }

    def test_flatten(self):

        flattener = Flatten()

        flattener.add_bundle_files_to_row(self.manifest, self.default_test_docs)

        expected = os.path.join(BASE_PATH, 'test1.csv')
        output = os.path.join(BASE_PATH, 'test1_tmp.csv')

        flattener.dump(filename=output)
        self.assertTrue(filecmp.cmp(expected, output))
        os.remove(output)

        expected = os.path.join(BASE_PATH, 'test1.tsv')
        output = os.path.join(BASE_PATH, 'test1_tmp.tsv')

        flattener.dump(filename=output, delim='\t')
        self.assertTrue(filecmp.cmp(expected, output))
        os.remove(output)


    def test_flatten_with_dirname(self):

        flattener = Flatten()

        flattener.add_bundle_files_to_row(self.manifest, self.default_test_docs, dir_name="1234-aaaa")
        expected = os.path.join(BASE_PATH, 'test2.csv')
        output = os.path.join(BASE_PATH, 'test2_tmp.csv')
        flattener.dump(filename=output)
        self.assertTrue(filecmp.cmp(expected, output))
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


        flattener.add_bundle_files_to_row(self.manifest, self.default_test_docs + [doc3])
        expected = os.path.join(BASE_PATH, 'test4.csv')
        output = os.path.join(BASE_PATH, 'test4_tmp.csv')
        flattener.dump(filename=output)
        self.assertTrue(filecmp.cmp(expected, output))
        os.remove(output)

    def test_ignore_links_bundle(self):

        flattener = Flatten()

        doc3 = {
            "schema_type" : "link_bundle",
        }

        flattener.add_bundle_files_to_row(self.manifest, self.default_test_docs + [doc3])
        expected = os.path.join(BASE_PATH, 'test1.csv')
        output = os.path.join(BASE_PATH, 'test5_tmp.csv')

        flattener.dump(filename=output)
        self.assertTrue(filecmp.cmp(expected, output))
        os.remove(output)

    def test_no_schema_type(self):

        flattener = Flatten()

        doc1 = {}
        doc2 = {}

        with self.assertRaises(MissingSchemaTypeError):
            flattener.add_bundle_files_to_row(self.manifest, [doc1, doc2])


    def test_no_file_uuid(self):

        flattener = Flatten()

        with self.assertRaises(MissingFileTypeError):
            flattener.add_bundle_files_to_row(self.manifest, [self.project_doc, self.doc2])

    def test_no_file_name(self):

        flattener = Flatten()

        doc1 = { "schema_type" : "file",
                 "provenance": {
                     "document_id": "file_id1",
                 },

                 }
        doc2 = { "schema_type" : "biomaterial"}

        with self.assertRaises(MissingFileNameError):
            flattener.add_bundle_files_to_row(self.manifest, [doc1, doc2])

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
            flattener.add_bundle_files_to_row(self.manifest, [doc1, doc2])


    def test_bundle_parser(self):
        expected = os.path.join(BASE_PATH, "bundles_tmp.csv")
        input = os.path.join(BASE_PATH, "bundles.csv")
        testargs = ["file_metadata_to_csv", "-d", ".", "-o", expected ]
        with patch.object(sys, 'argv', testargs):
             convert_bundle_dirs()
        self.assertTrue(filecmp.cmp(expected, expected))
        os.remove(expected)






if __name__ == '__main__':
    unittest.main()