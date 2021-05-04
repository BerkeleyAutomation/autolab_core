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

Converts datasets from the old format to a format readable by TensorDataset
Author: Jeff Mahler
"""
import argparse
import json
import numpy as np
import os
import shutil
import logging

from autolab_core.constants import JSON_INDENT
import autolab_core.utils as utils

if __name__ == "__main__":
    # initialize logging
    logging.getLogger().setLevel(logging.INFO)

    # parse args
    parser = argparse.ArgumentParser(
        description="Convert a legacy dataset to TensorDataset (in-place)"
    )
    parser.add_argument(
        "dataset_dir", type=str, default=None, help="path to a tensor dataset"
    )
    args = parser.parse_args()
    dataset_dir = args.dataset_dir

    # read filenames
    filenames = utils.filenames(dataset_dir)

    # create config file
    datapoints_per_file = None
    field_config = {}
    for filename in filenames:
        _, f = os.path.split(filename)
        _, ext = os.path.splitext(f)
        if ext != ".npz":
            continue

        u_ind = f.rfind("_")
        field_name = f[:u_ind]

        if field_name not in field_config.keys():
            field_config[field_name] = {}
            data = np.load(filename)["arr_0"]
            if datapoints_per_file is None:
                datapoints_per_file = data.shape[0]
            dtype = str(data.dtype)
            field_config[field_name]["dtype"] = dtype
            if len(data.shape) > 1:
                height = data.shape[1]
                field_config[field_name]["height"] = height
            if len(data.shape) > 2:
                width = data.shape[2]
                field_config[field_name]["width"] = width
            if len(data.shape) > 3:
                channels = data.shape[3]
                field_config[field_name]["channels"] = channels

    # write tensor dataset headers
    tensor_config = {
        "datapoints_per_file": datapoints_per_file,
        "fields": field_config,
    }

    config_filename = os.path.join(dataset_dir, "config.json")
    json.dump(
        tensor_config,
        open(config_filename, "w"),
        indent=JSON_INDENT,
        sort_keys=True,
    )

    metadata_filename = os.path.join(dataset_dir, "metadata.json")
    json.dump(
        {}, open(metadata_filename, "w"), indent=JSON_INDENT, sort_keys=True
    )

    tensor_dir = os.path.join(dataset_dir, "tensors")
    if not os.path.exists(tensor_dir):
        os.mkdir(tensor_dir)

    # move each individual file
    for filename in filenames:
        logging.info("Moving file {}".format(filename))
        if filename != tensor_dir:
            _, f = os.path.split(filename)
            new_filename = os.path.join(tensor_dir, f)
            shutil.move(filename, new_filename)
