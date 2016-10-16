"""
Common geometric primitives.
Author: Jeff Mahler
"""
import numpy as np

class Box(object):
    """A 2D box or 3D rectangular prism.

    Attributes
    ----------
    dims : :obj:`numpy.ndarray` of float
        Maximal extent in x, y, and (optionally) z.

    width : float
        Maximal extent in x.

    height : float
        Maximal extent in y.

    area : float
        Area of projection onto xy plane.

    min_pt : :obj:`numpy.ndarray` of float
        The minimum x, y, and (optionally) z points.

    max_pt : :obj:`numpy.ndarray` of float
        The maximum x, y, and (optionally) z points.

    center : :obj:`numpy.ndarray` of float
        The center of the box in 2 or 3D coords.

    frame : :obj:`str`
        The frame in which this box is placed.
    """

    def __init__(self, min_pt, max_pt, frame):
        """Initialize a box.

        Parameters
        ----------
        min_pt : :obj:`numpy.ndarray` of float
            The minimum x, y, and (optionally) z points.

        max_pt : :obj:`numpy.ndarray` of float
            The maximum x, y, and (optionally) z points.

        frame : :obj:`str`
            The frame in which this box is placed.

        Raises
        ------
        ValueError
            If max_pt is not strictly larger than min_pt in all dims.
        """
        if np.any((max_pt - min_pt) < 0):
            raise ValueError('Min point must be smaller than max point')
        self._min_pt = min_pt
        self._max_pt = max_pt
        self._frame = frame

    @property
    def dims(self):
        """:obj:`numpy.ndarray` of float: Maximal extent in x, y, and (optionally) z
        """
        return self._max_pt - self._min_pt

    @property
    def width(self):
        """float: Maximal extent in x.
        """
        return self.dims[0]

    @property
    def height(self):
        """float: Maximal extent in y.
        """
        return self.dims[1]

    @property
    def area(self):
        """float: Area of projection onto xy plane.
        """
        return self.width * self.height

    @property
    def min_pt(self):
        """:obj:`numpy.ndarray` of float: The minimum x, y, and (optionally) z points.
        """
        return self._min_pt

    @property
    def max_pt(self):
        """:obj:`numpy.ndarray` of float: The maximum x, y, and (optionally) z points.
        """
        return self._max_pt

    @property
    def center(self):
        """:obj:`numpy.ndarray` of float: The center of the box in 2 or 3D coords.
        """
        return self.min_pt + self.dims / 2.0

    @property
    def frame(self):
        """:obj:`str`: The frame in which this box is placed.
        """
        return self._frame
