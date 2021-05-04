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

Test correct functionality of the rigid transform class
Authors: Jeff Mahler
"""
import numpy as np
import unittest

from autolab_core import Point, PointCloud, Direction
from autolab_core import RigidTransform, SimilarityTransform


class RigidTransformTest(unittest.TestCase):
    def test_init(self):
        R = RigidTransform.random_rotation()
        t = RigidTransform.random_translation()
        from_frame = "a"
        to_frame = "b"
        T_a_b = RigidTransform(R, t, from_frame, to_frame)
        self.assertTrue(np.sum(np.abs(R - T_a_b.rotation)) < 1e-5)
        self.assertTrue(np.sum(np.abs(t - T_a_b.translation)) < 1e-5)

    def test_bad_inits(self):
        # test bad rotation dim
        R = np.random.rand(3)
        caught_bad_rotation = False
        try:
            RigidTransform(R)
        except ValueError:
            caught_bad_rotation = True
        self.assertTrue(
            caught_bad_rotation, msg="Failed to catch 3x1 rotation matrix"
        )

        # test bad rotation dim
        R = np.random.rand(3, 3, 3)
        caught_bad_rotation = False
        try:
            RigidTransform(R)
        except ValueError:
            caught_bad_rotation = True
        self.assertTrue(
            caught_bad_rotation, msg="Failed to catch 3x3x3 rotation matrix"
        )

        # determinant not equal to one
        R = np.random.rand(3, 3)
        caught_bad_rotation = False
        try:
            RigidTransform(R)
        except ValueError:
            caught_bad_rotation = True
        self.assertTrue(
            caught_bad_rotation, msg="Failed to catch rotation with det != 1"
        )

        # translation with illegal dimensions
        t = np.random.rand(3, 3)
        caught_bad_translation = False
        try:
            RigidTransform(translation=t)
        except ValueError:
            caught_bad_translation = True
        self.assertTrue(
            caught_bad_translation, msg="Failed to catch 3x3 translation"
        )

        # translation with illegal dimensions
        t = np.random.rand(2)
        caught_bad_translation = False
        try:
            RigidTransform(translation=t)
        except ValueError:
            caught_bad_translation = True
        self.assertTrue(
            caught_bad_translation, msg="Failed to catch 2x1 translation"
        )

    def test_inverse(self):
        R_a_b = RigidTransform.random_rotation()
        t_a_b = RigidTransform.random_translation()
        T_a_b = RigidTransform(R_a_b, t_a_b, "a", "b")
        T_b_a = T_a_b.inverse()

        # multiple with numpy arrays
        M_a_b = np.r_[np.c_[R_a_b, t_a_b], [[0, 0, 0, 1]]]
        M_b_a = np.linalg.inv(M_a_b)

        self.assertTrue(
            np.sum(np.abs(T_b_a.matrix - M_b_a)) < 1e-5,
            msg="Inverse gave incorrect transformation",
        )

        # check frames
        self.assertEqual(
            T_b_a.from_frame, "b", msg="Inverse has incorrect input frame"
        )
        self.assertEqual(
            T_b_a.to_frame, "a", msg="Inverse has incorrect output frame"
        )

    def test_composition(self):
        R_a_b = RigidTransform.random_rotation()
        t_a_b = RigidTransform.random_translation()
        R_b_c = RigidTransform.random_rotation()
        t_b_c = RigidTransform.random_translation()
        T_a_b = RigidTransform(R_a_b, t_a_b, "a", "b")
        T_b_c = RigidTransform(R_b_c, t_b_c, "b", "c")

        # multiply with numpy arrays
        M_a_b = np.r_[np.c_[R_a_b, t_a_b], [[0, 0, 0, 1]]]
        M_b_c = np.r_[np.c_[R_b_c, t_b_c], [[0, 0, 0, 1]]]
        M_a_c = M_b_c.dot(M_a_b)

        # use multiplication operator
        T_a_c = T_b_c * T_a_b

        self.assertTrue(
            np.sum(np.abs(T_a_c.matrix - M_a_c)) < 1e-5,
            msg="Composition gave incorrect transformation",
        )

        # check frames
        self.assertEqual(
            T_a_c.from_frame, "a", msg="Composition has incorrect input frame"
        )
        self.assertEqual(
            T_a_c.to_frame, "c", msg="Composition has incorrect output frame"
        )

    def test_point_transformation(self):
        R_a_b = RigidTransform.random_rotation()
        t_a_b = RigidTransform.random_translation()
        T_a_b = RigidTransform(R_a_b, t_a_b, "a", "b")

        x_a = np.random.rand(3)
        p_a = Point(x_a, "a")

        # multiply with numpy arrays
        x_b = R_a_b.dot(x_a) + t_a_b

        # use multiplication operator
        p_b = T_a_b * p_a

        self.assertTrue(
            np.sum(np.abs(p_b.vector - x_b)) < 1e-5,
            msg="Point transformation incorrect: Expected {}, Got {}".format(
                x_b, p_b.data
            ),
        )

        # check frames
        self.assertEqual(
            p_b.frame, "b", msg="Transformed point has incorrect frame"
        )

    def test_point_cloud_transformation(self, num_points=10):
        R_a_b = RigidTransform.random_rotation()
        t_a_b = RigidTransform.random_translation()
        T_a_b = RigidTransform(R_a_b, t_a_b, "a", "b")

        x_a = np.random.rand(3, num_points)
        pc_a = PointCloud(x_a, "a")

        # multiply with numpy arrays
        x_b = R_a_b.dot(x_a) + np.tile(t_a_b.reshape(3, 1), [1, num_points])

        # use multiplication operator
        pc_b = T_a_b * pc_a

        self.assertTrue(
            np.sum(np.abs(pc_b.data - x_b)) < 1e-5,
            msg="Point cloud transformation incorrect:\n"
            "Expected:\n{}\nGot:\n{}".format(x_b, pc_b.data),
        )

        # check frames
        self.assertEqual(
            pc_b.frame, "b", msg="Transformed point cloud has incorrect frame"
        )

    def test_bad_transformation(self, num_points=10):
        R_a_b = RigidTransform.random_rotation()
        t_a_b = RigidTransform.random_translation()
        T_a_b = RigidTransform(R_a_b, t_a_b, "a", "b")

        # bad point frame
        caught_bad_frame = False
        try:
            x_c = np.random.rand(3)
            p_c = Point(x_c, "c")
            T_a_b * p_c
        except ValueError:
            caught_bad_frame = True
        self.assertTrue(
            caught_bad_frame, msg="Failed to catch bad point frame"
        )

        # bad point cloud frame
        caught_bad_frame = False
        try:
            x_c = np.random.rand(3, num_points)
            pc_c = PointCloud(x_c, "c")
            T_a_b * pc_c
        except ValueError:
            caught_bad_frame = True
        self.assertTrue(
            caught_bad_frame, msg="Failed to catch bad point cloud frame"
        )

        # illegal input
        caught_bad_input = False
        try:
            x_a = np.random.rand(3, num_points)
            T_a_b * x_a
        except ValueError:
            caught_bad_input = True
        self.assertTrue(
            caught_bad_input, msg="Failed to catch numpy array input"
        )

    def test_similarity_transformation(self):
        R_a_b = RigidTransform.random_rotation()
        t_a_b = RigidTransform.random_translation()
        s_a_b = 2 * np.random.rand()
        R_b_c = RigidTransform.random_rotation()
        t_b_c = RigidTransform.random_translation()
        s_b_c = 2 * np.random.rand()
        T_a_b = SimilarityTransform(R_a_b, t_a_b, s_a_b, "a", "b")
        T_b_c = SimilarityTransform(R_b_c, t_b_c, s_b_c, "b", "c")

        T_b_a = T_a_b.inverse()

        x_a = np.random.rand(3)
        p_a = Point(x_a, "a")
        p_a2 = T_b_a * T_a_b * p_a
        self.assertTrue(np.allclose(p_a.data, p_a2.data))

        p_b = T_a_b * p_a
        p_b2 = s_a_b * (R_a_b.dot(p_a.data)) + t_a_b
        self.assertTrue(np.allclose(p_b.data, p_b2))

        p_c = T_b_c * T_a_b * p_a
        p_c2 = s_b_c * (R_b_c.dot(p_b2)) + t_b_c
        self.assertTrue(np.allclose(p_c.data, p_c2))

        v_a = np.random.rand(3)
        v_a = v_a / np.linalg.norm(v_a)
        v_a = Direction(v_a, "a")
        v_b = T_a_b * v_a
        v_b2 = R_a_b.dot(v_a.data)
        self.assertTrue(np.allclose(v_b.data, v_b2))


if __name__ == "__main__":
    unittest.main()
