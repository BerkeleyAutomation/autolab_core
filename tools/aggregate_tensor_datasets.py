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

Aggregates a pair of tensor datasets, merging them into a single dataset
Author: Jeff Mahler
"""
import argparse
import copy
import logging
import numpy as np
import os
import shutil

from autolab_core import TensorDataset, YamlConfig
import autolab_core.utils as utils

if __name__ == "__main__":
    # set up logger
    logging.getLogger().setLevel(logging.INFO)

    # parse args
    parser = argparse.ArgumentParser(
        description="Merges a set of tensor datasets"
    )
    parser.add_argument(
        "--config_filename",
        type=str,
        default="cfg/tools/aggregate_tensor_datasets.yaml",
        help="configuration file to use",
    )
    args = parser.parse_args()
    config_filename = args.config_filename

    # open config file
    cfg = YamlConfig(config_filename)
    input_dataset_names = cfg["input_datasets"]
    output_dataset_name = cfg["output_dataset"]
    display_rate = cfg["display_rate"]

    # modify list of dataset names
    all_input_dataset_names = []
    for dataset_name in input_dataset_names:
        tensor_dir = os.path.join(dataset_name, "tensors")
        if os.path.exists(tensor_dir):
            all_input_dataset_names.append(dataset_name)
        else:
            dataset_subdirs = utils.filenames(dataset_name, tag="dataset_")
            all_input_dataset_names.extend(dataset_subdirs)

    # open tensor dataset
    dataset = TensorDataset.open(all_input_dataset_names[0])
    tensor_config = copy.deepcopy(dataset.config)
    for field_name in cfg["exclude_fields"]:
        if field_name in tensor_config["fields"].keys():
            del tensor_config["fields"][field_name]
    field_names = tensor_config["fields"].keys()
    alt_field_names = [
        f if f != "rewards" else "grasp_metrics" for f in field_names
    ]

    # init tensor dataset
    output_dataset = TensorDataset(output_dataset_name, tensor_config)

    # copy config
    out_config_filename = os.path.join(
        output_dataset_name, "merge_config.yaml"
    )
    shutil.copyfile(config_filename, out_config_filename)

    # incrementally add points to the new dataset
    obj_id = 0
    obj_ids = {"unknown": 0}
    for dataset_name in all_input_dataset_names:
        dataset = TensorDataset.open(dataset_name)
        if "obj_ids" in dataset.metadata.keys():
            dataset_obj_ids = dataset.metadata["obj_ids"]
        logging.info("Aggregating data from dataset %s" % (dataset_name))
        for i in range(dataset.num_datapoints):
            try:
                datapoint = dataset.datapoint(i, field_names=field_names)
            except IndexError:
                datapoint = dataset.datapoint(i, field_names=alt_field_names)
                datapoint["rewards"] = datapoint["grasp_metrics"]
                del datapoint["grasp_metrics"]

            if i % display_rate == 0:
                logging.info(
                    "Datapoint: %d of %d" % (i + 1, dataset.num_datapoints)
                )

            if "obj_ids" in dataset.metadata.keys():
                # modify object ids
                dataset_obj_ids = dataset.metadata["obj_ids"]
                for k in range(datapoint["obj_ids"].shape[0]):
                    dataset_obj_id = datapoint["obj_ids"][k]
                    if dataset_obj_id != np.iinfo(np.uint32).max:
                        dataset_obj_key = dataset_obj_ids[str(dataset_obj_id)]
                        if dataset_obj_key not in obj_ids.keys():
                            obj_ids[dataset_obj_key] = obj_id
                            obj_id += 1
                        datapoint["obj_ids"][k] = obj_ids[dataset_obj_key]

                # modify grasped obj id
                dataset_grasped_obj_id = datapoint["grasped_obj_ids"]
                grasped_obj_key = dataset_obj_ids[str(dataset_grasped_obj_id)]
                datapoint["grasped_obj_ids"] = obj_ids[grasped_obj_key]

            # add datapoint
            output_dataset.add(datapoint)

    # set metadata
    obj_ids = utils.reverse_dictionary(obj_ids)
    output_dataset.add_metadata("obj_ids", obj_ids)
    for field_name, field_data in dataset.metadata.iteritems():
        if field_name not in ["obj_ids"]:
            output_dataset.add_metadata(field_name, field_data)

    # flush to disk
    output_dataset.flush()
