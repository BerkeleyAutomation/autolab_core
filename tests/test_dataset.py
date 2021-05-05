"""
Copyright ©2017. The Regents of the University of California (Regents).
All Rights Reserved. Permission to use, copy, modify, and distribute this
software and its documentation for educational, research, and not-for-profit
purposes, without fee and without a signed licensing agreement, is hereby
granted, provided that the above copyright notice, this paragraph and the
following two paragraphs appear in all copies, modifications, and
distributions. Contact The Office of Technology Licensing, UC Berkeley,
2150 Shattuck Avenue, Suite 510, Berkeley, CA 94720-1620, (510) 643-7201,
otl@berkeley.edu, http://ipira.berkeley.edu/industry-info for commercial
licensing opportunities.

IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT,
SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS,
ARISING OUT OF THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF
REGENTS HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
PURPOSE. THE SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED
HEREUNDER IS PROVIDED "AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE
MAINTENANCE, SUPPORT, UPDATES, ENHANCEMENTS, OR MODIFICATIONS.

Tests tensor dataset basic functionality
Author: Jeff Mahler
"""
import unittest
import numpy as np
import os
import random
import shutil

import autolab_core.utils as utils
from autolab_core.constants import READ_WRITE_ACCESS
from autolab_core import TensorDataset

SEED = 4134298
HEIGHT = 3
WIDTH = 3
CHANNELS = 3
DATAPOINTS_PER_FILE = 10
TEST_TENSOR_DATASET_NAME = "test_dataset"
TENSOR_CONFIG = {
    "datapoints_per_file": DATAPOINTS_PER_FILE,
    "fields": {
        "float_value": {"dtype": "float32"},
        "int_value": {"dtype": "int16"},
        "str_value": {"dtype": "str"},
        "vector_value": {"dtype": "float32", "height": HEIGHT},
        "matrix_value": {"dtype": "float32", "height": HEIGHT, "width": WIDTH},
        "image_value": {
            "dtype": "float32",
            "height": HEIGHT,
            "width": WIDTH,
            "channels": CHANNELS,
        },
    },
}


class TensorDatasetTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if os.path.exists(TEST_TENSOR_DATASET_NAME):
            shutil.rmtree(TEST_TENSOR_DATASET_NAME)

    def test_open(self):
        # Try opening nonexistent dataset (should raise error)
        open_successful = True
        try:
            TensorDataset.open(TEST_TENSOR_DATASET_NAME)
        except FileNotFoundError:
            open_successful = False
        self.assertFalse(open_successful)

    def test_single_read_write(self):
        # seed
        np.random.seed(SEED)
        random.seed(SEED)

        # open dataset
        create_successful = True
        try:
            dataset = TensorDataset(TEST_TENSOR_DATASET_NAME, TENSOR_CONFIG)
        except (ValueError, IOError):
            create_successful = False
        self.assertTrue(create_successful)

        # check field names
        write_datapoint = dataset.datapoint_template
        for field_name in write_datapoint.keys():
            self.assertTrue(field_name in dataset.field_names)

        # add the datapoint
        write_datapoint["float_value"] = np.random.rand()
        write_datapoint["int_value"] = int(100 * np.random.rand())
        write_datapoint["str_value"] = utils.gen_experiment_id()
        write_datapoint["vector_value"] = np.random.rand(HEIGHT)
        write_datapoint["matrix_value"] = np.random.rand(HEIGHT, WIDTH)
        write_datapoint["image_value"] = np.random.rand(
            HEIGHT, WIDTH, CHANNELS
        )
        dataset.add(write_datapoint)

        # check num datapoints
        self.assertTrue(dataset.num_datapoints == 1)

        # add metadata
        metadata_num = np.random.rand()
        dataset.add_metadata("test", metadata_num)

        # check written arrays
        dataset.flush()
        for field_name in dataset.field_names:
            filename = os.path.join(
                TEST_TENSOR_DATASET_NAME,
                "tensors",
                "%s_00000.npz" % (field_name),
            )
            value = np.load(filename)["arr_0"]
            if isinstance(value[0], str):
                self.assertTrue(value[0] == write_datapoint[field_name])
            else:
                self.assertTrue(
                    np.allclose(value[0], write_datapoint[field_name])
                )

        # re-open the dataset
        del dataset
        dataset = TensorDataset.open(TEST_TENSOR_DATASET_NAME)

        # read metadata
        self.assertTrue(np.allclose(dataset.metadata["test"], metadata_num))

        # read datapoint
        read_datapoint = dataset.datapoint(0)
        for field_name in dataset.field_names:
            if isinstance(read_datapoint[field_name], str):
                self.assertTrue(
                    read_datapoint[field_name] == write_datapoint[field_name]
                )
            else:
                self.assertTrue(
                    np.allclose(
                        read_datapoint[field_name], write_datapoint[field_name]
                    )
                )

        # check iterator
        for read_datapoint in dataset:
            for field_name in dataset.field_names:
                if isinstance(read_datapoint[field_name], str):
                    self.assertTrue(
                        read_datapoint[field_name]
                        == write_datapoint[field_name]
                    )
                else:
                    self.assertTrue(
                        np.allclose(
                            read_datapoint[field_name],
                            write_datapoint[field_name],
                        )
                    )

        # read individual fields
        for field_name in dataset.field_names:
            read_datapoint = dataset.datapoint(0, field_names=[field_name])
            if isinstance(read_datapoint[field_name], str):
                self.assertTrue(
                    read_datapoint[field_name] == write_datapoint[field_name]
                )
            else:
                self.assertTrue(
                    np.allclose(
                        read_datapoint[field_name], write_datapoint[field_name]
                    )
                )

        # re-open the dataset in write-only
        del dataset
        dataset = TensorDataset.open(
            TEST_TENSOR_DATASET_NAME, access_mode=READ_WRITE_ACCESS
        )

        # delete datapoint
        dataset.delete_last()

        # check that the dataset is correct
        self.assertTrue(dataset.num_datapoints == 0)
        self.assertTrue(dataset.num_tensors == 0)
        for field_name in dataset.field_names:
            filename = os.path.join(
                TEST_TENSOR_DATASET_NAME,
                "tensors",
                "%s_00000.npz" % (field_name),
            )
            self.assertFalse(os.path.exists(filename))

        # remove dataset
        if os.path.exists(TEST_TENSOR_DATASET_NAME):
            shutil.rmtree(TEST_TENSOR_DATASET_NAME)

    def test_multi_tensor_read_write(self):
        # seed
        np.random.seed(SEED)
        random.seed(SEED)

        # open dataset
        dataset = TensorDataset(TEST_TENSOR_DATASET_NAME, TENSOR_CONFIG)

        write_datapoints = []
        for i in range(DATAPOINTS_PER_FILE + 1):
            write_datapoint = {}
            write_datapoint["float_value"] = np.random.rand()
            write_datapoint["int_value"] = int(100 * np.random.rand())
            write_datapoint["str_value"] = utils.gen_experiment_id()
            write_datapoint["vector_value"] = np.random.rand(HEIGHT)
            write_datapoint["matrix_value"] = np.random.rand(HEIGHT, WIDTH)
            write_datapoint["image_value"] = np.random.rand(
                HEIGHT, WIDTH, CHANNELS
            )
            dataset.add(write_datapoint)
            write_datapoints.append(write_datapoint)

        # check num datapoints
        self.assertTrue(dataset.num_datapoints == DATAPOINTS_PER_FILE + 1)
        self.assertTrue(dataset.num_tensors == 2)

        # check read
        dataset.flush()
        del dataset
        dataset = TensorDataset.open(
            TEST_TENSOR_DATASET_NAME, access_mode=READ_WRITE_ACCESS
        )
        for i, read_datapoint in enumerate(dataset):
            write_datapoint = write_datapoints[i]
            for field_name in dataset.field_names:
                if isinstance(read_datapoint[field_name], str):
                    self.assertTrue(
                        read_datapoint[field_name]
                        == write_datapoint[field_name]
                    )
                else:
                    self.assertTrue(
                        np.allclose(
                            read_datapoint[field_name],
                            write_datapoint[field_name],
                        )
                    )

        for i, read_datapoint in enumerate(dataset):
            # check iterator item
            write_datapoint = write_datapoints[i]
            for field_name in dataset.field_names:
                if isinstance(read_datapoint[field_name], str):
                    self.assertTrue(
                        read_datapoint[field_name]
                        == write_datapoint[field_name]
                    )
                else:
                    self.assertTrue(
                        np.allclose(
                            read_datapoint[field_name],
                            write_datapoint[field_name],
                        )
                    )

            # check random item
            ind = np.random.choice(dataset.num_datapoints)
            write_datapoint = write_datapoints[ind]
            read_datapoint = dataset.datapoint(ind)
            for field_name in dataset.field_names:
                if isinstance(read_datapoint[field_name], str):
                    self.assertTrue(
                        read_datapoint[field_name]
                        == write_datapoint[field_name]
                    )
                else:
                    self.assertTrue(
                        np.allclose(
                            read_datapoint[field_name],
                            write_datapoint[field_name],
                        )
                    )

        # check deletion
        dataset.delete_last()
        self.assertTrue(dataset.num_datapoints == DATAPOINTS_PER_FILE)
        self.assertTrue(dataset.num_tensors == 1)
        dataset.add(write_datapoints[-1])
        for write_datapoint in write_datapoints:
            dataset.add(write_datapoint)
        self.assertTrue(
            dataset.num_datapoints == 2 * (DATAPOINTS_PER_FILE + 1)
        )
        self.assertTrue(dataset.num_tensors == 3)

        # check valid
        for i in range(dataset.num_datapoints):
            read_datapoint = dataset.datapoint(i)
            write_datapoint = write_datapoints[i % (len(write_datapoints))]
            for field_name in dataset.field_names:
                if isinstance(read_datapoint[field_name], str):
                    self.assertTrue(
                        read_datapoint[field_name]
                        == write_datapoint[field_name]
                    )
                else:
                    self.assertTrue(
                        np.allclose(
                            read_datapoint[field_name],
                            write_datapoint[field_name],
                        )
                    )

        # check read then write out of order
        ind = np.random.choice(DATAPOINTS_PER_FILE)
        write_datapoint = write_datapoints[ind]
        read_datapoint = dataset.datapoint(ind)
        for field_name in dataset.field_names:
            if isinstance(read_datapoint[field_name], str):
                self.assertTrue(
                    read_datapoint[field_name] == write_datapoint[field_name]
                )
            else:
                self.assertTrue(
                    np.allclose(
                        read_datapoint[field_name], write_datapoint[field_name]
                    )
                )

        write_datapoint = write_datapoints[0]
        dataset.add(write_datapoint)
        read_datapoint = dataset.datapoint(dataset.num_datapoints - 1)
        for field_name in dataset.field_names:
            if isinstance(read_datapoint[field_name], str):
                self.assertTrue(
                    read_datapoint[field_name] == write_datapoint[field_name]
                )
            else:
                self.assertTrue(
                    np.allclose(
                        read_datapoint[field_name], write_datapoint[field_name]
                    )
                )
        dataset.delete_last()

        # check data integrity
        for i, read_datapoint in enumerate(dataset):
            write_datapoint = write_datapoints[i % len(write_datapoints)]
            for field_name in dataset.field_names:
                if isinstance(read_datapoint[field_name], str):
                    self.assertTrue(
                        read_datapoint[field_name]
                        == write_datapoint[field_name]
                    )
                else:
                    self.assertTrue(
                        np.allclose(
                            read_datapoint[field_name],
                            write_datapoint[field_name],
                        )
                    )

        # delete last
        dataset.delete_last(len(write_datapoints))
        self.assertTrue(dataset.num_datapoints == DATAPOINTS_PER_FILE + 1)
        self.assertTrue(dataset.num_tensors == 2)
        for i, read_datapoint in enumerate(dataset):
            write_datapoint = write_datapoints[i]
            for field_name in dataset.field_names:
                if isinstance(read_datapoint[field_name], str):
                    self.assertTrue(
                        read_datapoint[field_name]
                        == write_datapoint[field_name]
                    )
                else:
                    self.assertTrue(
                        np.allclose(
                            read_datapoint[field_name],
                            write_datapoint[field_name],
                        )
                    )

        # remove dataset
        if os.path.exists(TEST_TENSOR_DATASET_NAME):
            shutil.rmtree(TEST_TENSOR_DATASET_NAME)


if __name__ == "__main__":
    unittest.main()
