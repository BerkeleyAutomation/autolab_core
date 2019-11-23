"""
Test basic functionality of the point classes 
Authors: Jeff Mahler
"""
import copy
import logging
import numpy as np
import socket
import time
import unittest

from autolab_core import BagOfPoints, ImageCoords, Point, PointCloud, RgbCloud, RgbPointCloud

class PointsTest(unittest.TestCase):
    def test_inits(self, num_points=10):
        # basic init
        data = np.random.rand(3, num_points)
        p_a = PointCloud(data, 'a')
        self.assertTrue(np.abs(data.shape[0] - p_a.shape[0]) < 1e-5, msg='BagOfPoints has incorrect shape')
        self.assertTrue(np.abs(data.shape[1] - p_a.shape[1]) < 1e-5, msg='BagOfPoints has incorrect shape')
        self.assertTrue(np.sum(np.abs(data - p_a.data)) < 1e-5, msg='BagOfPoints has incorrect data')
        self.assertTrue(np.abs(data.shape[0] - p_a.dim) < 1e-5, msg='BagOfPoints has incorrect dim')
        self.assertTrue(np.abs(data.shape[1] - p_a.num_points) < 1e-5, msg='BagOfPoints has incorrect num points')
        self.assertEqual('a', p_a.frame, msg='BagOfPoints has incorrect frame')

        # point init with multiple points
        caught_bad_init = False
        try:
            data = np.random.rand(3, num_points)
            p_a = Point(data, 'a')
        except ValueError as e:
            caught_bad_init = True
        self.assertTrue(caught_bad_init, msg='Failed to catch point init with more than one point')

        # point init with bad dim
        caught_bad_init = False
        try:
            data = np.random.rand(3,3)
            p_a = Point(data, 'a')
        except ValueError as e:
            caught_bad_init = True
        self.assertTrue(caught_bad_init, msg='Failed to catch point init with 3x3')

        # point cloud with bad shape
        caught_bad_init = False
        try:
            data = np.random.rand(3,3,3)
            p_a = PointCloud(data, 'a')
        except ValueError as e:
            caught_bad_init = True
        self.assertTrue(caught_bad_init, msg='Failed to catch point cloud init with 3x3x3')

        # point cloud with bad dim
        caught_bad_init = False
        try:
            data = np.random.rand(4, num_points)
            p_a = PointCloud(data, 'a')
        except ValueError as e:
            caught_bad_init = True
        self.assertTrue(caught_bad_init, msg='Failed to catch point cloud init with 4x%d' %(num_points))        

        # point cloud with bad type
        caught_bad_init = False
        try:
            data = 100 * np.random.rand(3, num_points).astype(np.uint8)
            p_a = PointCloud(data, 'a')
        except ValueError as e:
            caught_bad_init = True
        self.assertTrue(caught_bad_init, msg='Failed to catch point cloud init with uint type')        

        # image coords with bad type
        caught_bad_init = False
        try:
            data = np.random.rand(2, num_points)
            p_a = ImageCoords(data, 'a')
        except ValueError as e:
            caught_bad_init = True
        self.assertTrue(caught_bad_init, msg='Failed to catch image coords init with float type')        
        
        # image coords with bad dim
        caught_bad_init = False
        try:
            data = 100 * np.random.rand(3, num_points).astype(np.uint16)
            p_a = ImageCoords(data, 'a')
        except ValueError as e:
            caught_bad_init = True
        self.assertTrue(caught_bad_init, msg='Failed to catch image coords init with 3xN array')        

        # rgb coordinate with bad type
        caught_bad_init = False
        try:
            data = np.random.rand(3, num_points)
            p_a = RgbCloud(data, 'a')
        except ValueError as e:
            caught_bad_init = True
        self.assertTrue(caught_bad_init, msg='Failed to catch rgb cloud init with float type')        

        # image coords with bad dim
        caught_bad_init = False
        try:
            data = 100 * np.random.rand(4, num_points).astype(np.uint16)
            p_a = RgbCloud(data, 'a')
        except ValueError as e:
            caught_bad_init = True
        self.assertTrue(caught_bad_init, msg='Failed to catch rgb cloud init with 4xN array')
    
    def test_divs(self, num_points=10):
        data = np.random.rand(3, num_points)
        p_a = PointCloud(data, 'a')
        p_b = Point(np.random.rand(3), 'b')

        # div on left
        p_a_int = p_a / 5
        assert np.allclose(p_a_int._data, p_a._data / 5)
        p_a_float = p_a / 2.5
        assert np.allclose(p_a_float._data, p_a._data / 2.5)
        p_b_int = p_b / 5
        assert np.allclose(p_b_int._data, p_b._data / 5)
        p_b_float = p_b / 2.5
        assert np.allclose(p_b_float._data, p_b._data / 2.5)

        # div on right
        p_a_int = 5 / p_a
        assert np.allclose(p_a_int._data, 5 / p_a._data)
        p_a_float = 2.5 / p_a
        assert np.allclose(p_a_float._data, 2.5 / p_a._data)
        p_b_int = 5 / p_b
        assert np.allclose(p_b_int._data, 5 / p_b._data)
        p_b_float = 2.5 / p_b
        assert np.allclose(p_b_float._data, 2.5 / p_b._data)
        
if __name__ == '__main__':
    unittest.main()
