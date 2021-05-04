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

Subsamples a TensorDataset.
Author: Jeff Mahler
"""
import argparse
import logging
import numpy as np

from autolab_core import TensorDataset

if __name__ == "__main__":
    # initialize logging
    logging.getLogger().setLevel(logging.INFO)

    # parse args
    parser = argparse.ArgumentParser(description="Subsamples a dataset")
    parser.add_argument(
        "dataset_path",
        type=str,
        default=None,
        help="directory of the dataset to subsample",
    )
    parser.add_argument(
        "output_path",
        type=str,
        default=None,
        help="directory to store the subsampled dataset",
    )
    args = parser.parse_args()
    dataset_path = args.dataset_path
    output_path = args.output_path

    dataset = TensorDataset.open(dataset_path)
    out_dataset = TensorDataset(output_path, dataset.config)

    ind = np.arange(dataset.num_datapoints)
    np.random.shuffle(ind)

    for i, j in enumerate(ind):
        logging.info("Saving datapoint %d" % (i))
        datapoint = dataset[j]
        out_dataset.add(datapoint)
    out_dataset.flush()

    for split_name in dataset.split_names:
        _, val_indices, _ = dataset.split(split_name)
        new_val_indices = []
        for i in range(ind.shape[0]):
            if ind[i] in val_indices:
                new_val_indices.append(i)

        out_dataset.make_split(split_name, val_indices=new_val_indices)
