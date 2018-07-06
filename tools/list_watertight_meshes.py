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
Lists the set of watertight meshes from an input directory.
Author: Jeff Mahler
"""
import numpy as np
import os
import sys

import autolab_core.utils as utils
import trimesh

if __name__ == '__main__':
    data_dir = sys.argv[1]

    out_filename = os.path.join(data_dir, 'watertight_listing.txt')
    out_f = open(out_filename, 'w')

    num_watertight = 0
    obj_filenames = utils.filenames(data_dir, tag='.obj')
    for k, obj_filename in enumerate(obj_filenames):
        mesh = trimesh.load_mesh(obj_filename)
        if mesh.is_watertight:
            num_watertight += 1
            print 'Pct Watertight:', float(num_watertight) / (k+1)
            print 'Pct Complete:', float(k) / len(obj_filenames)
            print obj_filename
            out_f.write('%s\n' %(obj_filename))

    print 'Pct Watertight:', float(num_watertight) / len(obj_filenames)
    out_f.close()
