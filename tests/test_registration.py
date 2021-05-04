"""
Tests the image class.
Author: Jeff Mahler
"""
import unittest

import numpy as np

from .constants import NUM_POINTS, NUM_ITERS
from autolab_core import (
    RigidTransform,
    PointCloud,
    NormalCloud,
    PointToPlaneICPSolver,
    PointToPlaneFeatureMatcher,
)


class TestRegistration(unittest.TestCase):
    def test_registration(self):
        np.random.seed(101)

        source_points = np.random.rand(3, NUM_POINTS).astype(np.float32)
        source_normals = np.random.rand(3, NUM_POINTS).astype(np.float32)
        source_normals = source_normals / np.tile(
            np.linalg.norm(source_normals, axis=0)[np.newaxis, :], [3, 1]
        )

        source_point_cloud = PointCloud(source_points, frame="world")
        source_normal_cloud = NormalCloud(source_normals, frame="world")

        matcher = PointToPlaneFeatureMatcher()
        solver = PointToPlaneICPSolver(sample_size=NUM_POINTS)

        # 3d registration
        tf = RigidTransform(
            rotation=RigidTransform.random_rotation(),
            translation=RigidTransform.random_translation(),
            from_frame="world",
            to_frame="world",
        )
        tf = RigidTransform(
            from_frame="world", to_frame="world"
        ).interpolate_with(tf, 0.01)
        target_point_cloud = tf * source_point_cloud
        target_normal_cloud = tf * source_normal_cloud

        result = solver.register(
            source_point_cloud,
            target_point_cloud,
            source_normal_cloud,
            target_normal_cloud,
            matcher,
            num_iterations=NUM_ITERS,
        )

        self.assertTrue(
            np.allclose(tf.matrix, result.T_source_target.matrix, atol=1e-3)
        )

        # 2d registration
        theta = 0.1 * np.random.rand()
        t = 0.005 * np.random.rand(3, 1)
        t[2] = 0
        R = np.array(
            [
                [np.cos(theta), -np.sin(theta), 0],
                [np.sin(theta), np.cos(theta), 0],
                [0, 0, 1],
            ]
        )
        tf = RigidTransform(R, t, from_frame="world", to_frame="world")
        target_point_cloud = tf * source_point_cloud
        target_normal_cloud = tf * source_normal_cloud

        result = solver.register_2d(
            source_point_cloud,
            target_point_cloud,
            source_normal_cloud,
            target_normal_cloud,
            matcher,
            num_iterations=NUM_ITERS,
        )

        self.assertTrue(
            np.allclose(tf.matrix, result.T_source_target.matrix, atol=1e-3)
        )


if __name__ == "__main__":
    unittest.main()
