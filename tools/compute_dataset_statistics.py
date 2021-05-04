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

Analysis tool for experiments with the OpenAI gym environment
Author: Jeff Mahler
"""
import argparse
import json
import logging
import numpy as np
import os
import random

from autolab_core import TensorDataset, YamlConfig
import autolab_core.utils as utils

from visualization import Visualizer2D as vis2d

SEED = 2345


def compute_dataset_statistics(dataset_path, output_path, config):
    """
    Compute the statistics of fields of a TensorDataset

    Parameters
    ----------
    dataset_path : str
        path to the dataset
    output_dir : str
        where to save the data
    config : :obj:`YamlConfig`
        parameters for the analysis
    """
    # parse config
    analysis_fields = config["analysis_fields"]
    num_percentiles = config["num_percentiles"]
    thresholds = config["thresholds"]
    log_rate = config["log_rate"]

    num_bins = config["num_bins"]
    font_size = config["font_size"]
    dpi = config["dpi"]

    # create dataset for the aggregated results
    dataset = TensorDataset.open(dataset_path)
    num_datapoints = dataset.num_datapoints

    # allocate buffers
    analysis_data = {}
    for field in analysis_fields:
        analysis_data[field] = []

    # loop through dataset
    for i in range(num_datapoints):
        if i % log_rate == 0:
            logging.info(
                "Reading datapoint %d of %d" % (i + 1, num_datapoints)
            )

        # read datapoint
        datapoint = dataset.datapoint(i, analysis_fields)
        for key, value in datapoint.iteritems():
            analysis_data[key].append(value)

    # create output CSV
    stats_headers = {
        "name": "str",
        "mean": "float",
        "median": "float",
        "std": "float",
    }
    for i in range(num_percentiles):
        pctile = int((100.0 / num_percentiles) * i)
        field = "%d_pctile" % (pctile)
        stats_headers[field] = "float"
    for t in thresholds:
        field = "pct_above_%.3f" % (t)
        stats_headers[field] = "float"

    # analyze statistics
    for field, data in analysis_data.iteritems():
        # init arrays
        data = np.array(data)

        # init filename
        stats_filename = os.path.join(output_path, "%s_stats.json" % (field))
        if os.path.exists(stats_filename):
            logging.warning("Statistics file %s exists!" % (stats_filename))

        # stats
        mean = np.mean(data)
        median = np.median(data)
        std = np.std(data)
        stats = {
            "name": str(field),
            "mean": float(mean),
            "median": float(median),
            "std": float(std),
        }
        for i in range(num_percentiles):
            pctile = int((100.0 / num_percentiles) * i)
            pctile_field = "%d_pctile" % (pctile)
            stats[pctile_field] = float(np.percentile(data, pctile))
        for t in thresholds:
            t_field = "pct_above_%.3f" % (t)
            stats[t_field] = float(np.mean(1 * (data > t)))
        json.dump(stats, open(stats_filename, "w"), indent=2, sort_keys=True)

        # histogram
        num_unique = np.unique(data).shape[0]
        nb = min(num_bins, data.shape[0], num_unique)
        bounds = (np.min(data), np.max(data))
        vis2d.figure()
        utils.histogram(data, nb, bounds, normalized=False, plot=True)
        vis2d.xlabel(field, fontsize=font_size)
        vis2d.ylabel("Count", fontsize=font_size)
        data_filename = os.path.join(output_path, "histogram_%s.pdf" % (field))
        vis2d.show(data_filename, dpi=dpi)


if __name__ == "__main__":
    # initialize logging
    logging.getLogger().setLevel(logging.INFO)

    # parse args
    parser = argparse.ArgumentParser(
        description="Compute statistics of select fields of a tensor dataset"
    )
    parser.add_argument(
        "dataset_path",
        type=str,
        default=None,
        help="path to an experiment dataset",
    )
    parser.add_argument(
        "--output_path",
        type=str,
        default=None,
        help="path to save dataset statistics",
    )
    parser.add_argument(
        "--debug",
        type=bool,
        default=True,
        help="whether to set the random seed",
    )
    parser.add_argument(
        "--config_filename",
        type=str,
        default=None,
        help="configuration file to use",
    )
    args = parser.parse_args()
    dataset_path = args.dataset_path
    output_path = args.output_path
    debug = args.debug
    config_filename = args.config_filename

    # auto-save in dataset
    if output_path is None:
        output_path = os.path.join(dataset_path, "stats")

    # create output dir
    if not os.path.exists(output_path):
        os.mkdir(output_path)

    # set random seed
    if debug:
        np.random.seed(SEED)
        random.seed(SEED)

    # handle config filename
    if config_filename is None:
        config_filename = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "..",
            "cfg/tools/compute_dataset_statistics.yaml",
        )

    # turn relative paths absolute
    if not os.path.isabs(config_filename):
        config_filename = os.path.join(os.getcwd(), config_filename)

    # load config
    config = YamlConfig(config_filename)

    # run analysis
    compute_dataset_statistics(dataset_path, output_path, config)
