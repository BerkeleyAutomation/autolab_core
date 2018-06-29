# -*- coding: utf-8 -*-
"""
Copyright ©2017. The Regents of the University of California (Regents). All Rights Reserved.
Permission to use, copy, modify, and distribute this software and its documentation for educational,
research, and not-for-profit purposes, without fee and without a signed licensing agreement, is
hereby granted, provided that the above copyright notice, this paragraph and the following two
paragraphs appear in all copies, modifications, and distributions. Contact The Office of Technology
Licensing, UC Berkeley, 2150 Shattuck Avenue, Suite 510, Berkeley, CA 94720-1620, (510) 643-
7201, otl@berkeley.edu, http://ipira.berkeley.edu/industry-info for commercial licensing opportunities.

IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS BEEN
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
PURPOSE. THE SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED
HEREUNDER IS PROVIDED "AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE
MAINTENANCE, SUPPORT, UPDATES, ENHANCEMENTS, OR MODIFICATIONS.
"""
"""
Aggregates a pair of tensor datasets, merging them into a single dataset
Author: Jeff Mahler
"""
import argparse
import copy
import IPython
import logging
import numpy as np
import os
import shutil
import sys

from autolab_core import TensorDataset, YamlConfig
import autolab_core.utils as utils

if __name__ == '__main__':
    # set up logger
    logging.getLogger().setLevel(logging.INFO)
    
    # parse args
    parser = argparse.ArgumentParser(description='Merges a set of tensor datasets')
    parser.add_argument('--config_filename', type=str, default='cfg/tools/aggregate_tensor_datasets.yaml', help='configuration file to use')
    args = parser.parse_args()
    config_filename = args.config_filename

    # open config file
    cfg = YamlConfig(config_filename)
    input_dataset_names = cfg['input_datasets']
    output_dataset_name = cfg['output_dataset']
    display_rate = cfg['display_rate']

    # modify list of dataset names
    all_input_dataset_names = []
    for dataset_name in input_dataset_names:
        tensor_dir = os.path.join(dataset_name, 'tensors')
        if os.path.exists(tensor_dir):
            all_input_dataset_names.append(dataset_name)
        else:
            dataset_subdirs = utils.filenames(dataset_name,
                                              tag='dataset_')
            all_input_dataset_names.extend(dataset_subdirs)

    # open tensor dataset
    dataset = TensorDataset.open(all_input_dataset_names[0])
    tensor_config = copy.deepcopy(dataset.config)
    for field_name in cfg['exclude_fields']:
        del tensor_config['fields'][field_name]    
    field_names = tensor_config['fields'].keys()

    # init tensor dataset
    output_dataset = TensorDataset(output_dataset_name, tensor_config)

    # copy config
    out_config_filename = os.path.join(output_dataset_name, 'merge_config.yaml')
    shutil.copyfile(config_filename, out_config_filename)
    
    # incrementally add points to the new dataset
    obj_id = 0
    heap_id = 0
    obj_ids = {}
    heap_indices = {}
    for dataset_name in all_input_dataset_names:
        j = 0
        dataset = TensorDataset.open(dataset_name)
        dataset_obj_ids = dataset.metadata['obj_ids']
        logging.info('Aggregating data from dataset %s' %(dataset_name))        
        for i in range(dataset.num_datapoints):
            datapoint = dataset.datapoint(i, field_names=field_names)
            
            if i % display_rate == 0:
                logging.info('Datapoint: %d of %d' %(i+1, dataset.num_datapoints))

            # update heap id
            if j > 0 and datapoint['timesteps'] == 0:
                heap_id += 1
                heap_indices[heap_id] = output_dataset.num_datapoints
                
            # modify object ids
            for k in range(datapoint['obj_ids'].shape[0]):
                dataset_obj_id = datapoint['obj_ids'][k]
                if dataset_obj_id != np.iinfo(np.uint32).max:
                    dataset_obj_key = dataset_obj_ids[str(dataset_obj_id)]
                    if dataset_obj_key not in obj_ids.keys():
                        obj_ids[dataset_obj_key] = obj_id
                        obj_id += 1
                    datapoint['obj_ids'][k] = obj_ids[dataset_obj_key]

            # modify grasped obj id
            dataset_grasped_obj_id = datapoint['grasped_obj_ids']
            grasped_obj_key = dataset_obj_ids[str(dataset_grasped_obj_id)]
            datapoint['grasped_obj_ids'] = obj_ids[grasped_obj_key]

            # modify heap id
            datapoint['heap_ids'] = heap_id
                
            # add datapoint    
            output_dataset.add(datapoint)
            j += 1

    # set metadata
    obj_ids = utils.reverse_dictionary(obj_ids)
    output_dataset.add_metadata('obj_ids', obj_ids)
    output_dataset.add_metadata('action_ids', dataset.metadata['action_ids'])
    output_dataset.add_metadata('heap_indices', heap_indices)
            
    # flush to disk
    output_dataset.flush()
