"""
Generic Random Variable wrapper classes 
Author: Jeff Mahler
"""
from abc import ABCMeta, abstractmethod

import numpy as np
import scipy.stats

from .rigid_transformations import RigidTransform
from .utils import skew

class RandomVariable(object):
    """Abstract base class for random variables.
    """
    __metaclass__ = ABCMeta

    def __init__(self, num_prealloc_samples=0):
        """Initialize a random variable with optional pre-sampling.

        Parameters
        ----------
        num_prealloc_samples : int
            The number of samples to pre-allocate.
        """
        self.num_prealloc_samples_ = num_prealloc_samples
        if self.num_prealloc_samples_ > 0:
            self._preallocate_samples()

    def _preallocate_samples(self):
        """Preallocate samples for faster adaptive sampling.
        """
        self.prealloc_samples_ = []
        for i in range(self.num_prealloc_samples_):
            self.prealloc_samples_.append(self.sample())

    @abstractmethod
    def sample(self, size=1):
        """Generate samples of the random variable.

        Parameters
        ----------
        size : int
            The number of samples to generate.

        Returns
        -------
        :obj:`numpy.ndarray` of float or int
            The samples of the random variable. If `size == 1`, then
            the returned value will not be wrapped in an array.
        """
        pass

    def rvs(self, size=1, iteration=1):
        """Sample the random variable, using the preallocated samples if
        possible.

        Parameters
        ----------
        size : int
            The number of samples to generate.

        iteration : int
            The location in the preallocated sample array to start sampling
            from.

        Returns
        -------
        :obj:`numpy.ndarray` of float or int
            The samples of the random variable. If `size == 1`, then
            the returned value will not be wrapped in an array.
        """
        if self.num_prealloc_samples_ > 0:
            samples = []
            for i in range(size):
                samples.append(self.prealloc_samples_[(iteration + i) % self.num_prealloc_samples_])
            if size == 1:
                return samples[0]
            return samples
        # generate a new sample
        return self.sample(size=size)

class BernoulliRV(RandomVariable):
    """A Bernoulli random variable.
    """

    def __init__(self, p):
        """Initialize a Bernoulli random variable with probability p.

        Parameters
        ----------
        p : float
            The probability that the random variable takes the value 1.
        """
        self.p = p

    def sample(self, size=1):
        """Generate samples of the random variable.

        Parameters
        ----------
        size : int
            The number of samples to generate.

        Returns
        -------
        :obj:`numpy.ndarray` of int or int
            The samples of the random variable. If `size == 1`, then
            the returned value will not be wrapped in an array.
        """
        samples = scipy.stats.bernoulli.rvs(self.p, size=size)
        if size == 1:
            return samples[0]
        return samples

class GaussianRV(RandomVariable):
    """A Gaussian random variable.
    """

    def __init__(self, mu, sigma):
        """Initialize a Gaussian random variable.

        Parameters
        ----------
        mu : float
            The mean of the Gaussian.

        sigma : float
            The standard deviation of the Gaussian.
        """
        self.mu = mu
        self.sigma = sigma

    def sample(self, size=1):
        """Generate samples of the random variable.

        Parameters
        ----------
        size : int
            The number of samples to generate.

        Returns
        -------
        :obj:`numpy.ndarray` of float
            The samples of the random variable.
        """
        samples = scipy.stats.multivariate_normal.rvs(self.mu, self.sigma, size=size)
        return samples

class ArtificialRV(RandomVariable):
    """A fake RV that deterministically returns the given object.
    """

    def __init__(self, obj, num_prealloc_samples=0):
        """Initialize an artifical RV.

        Parameters
        ----------
        obj : item
            The item to always return.

        num_prealloc_samples : int
            The number of samples to pre-allocate.
        """
        self.obj_ = obj
        super(ArtificialRV, self).__init__(num_prealloc_samples)

    def sample(self, size = 1):
        """Generate copies of the artifical RV.

        Parameters
        ----------
        size : int
            The number of samples to generate.

        Returns
        -------
        :obj:`numpy.ndarray` of item
            The copies of the fake RV.
        """
        return np.array([self.obj_] * size)

class ArtificialSingleRV(ArtificialRV):
    """A single ArtificialRV.
    """
    def sample(self, size = None):
        """Generate a single copy of the artificial RV.

        Returns
        -------
        item
            The copies of the fake RV.
        """
        return self.obj_

class IsotropicGaussianRigidTransformRandomVariable(RandomVariable):
    """ Random variable for sampling RigidTransformations with
    a zero-mean isotropic Gaussian distribution over pose variables.

    Attributes
    ----------
    t_rv : :obj:`scipy.stats.multivariate_normal`
        multivariate Gaussian random variable for object translation
    r_xi_rv : :obj:`scipy.stats.multivariate_normal`
        multivariate Gaussian random variable of object rotations over the Lie Algebra
    """
    def __init__(self, sigma_trans, sigma_rot,
                 from_frame='world', to_frame='world',
                 num_prealloc_samples=0):
        # read params
        self._sigma_trans = max(1e-10, sigma_trans)
        self._sigma_rot = max(1e-10, sigma_rot)
        self._from_frame = from_frame
        self._to_frame = to_frame

        # setup random variables
        self._t_rv = scipy.stats.multivariate_normal(np.zeros(3), self._sigma_trans**2)
        self._r_xi_rv = scipy.stats.multivariate_normal(np.zeros(3), self._sigma_rot**2)
        RandomVariable.__init__(self, num_prealloc_samples)

    def sample(self, size=1):
        """ Sample rigid transform random variables.

        Parameters
        ----------
        size : int
            number of sample to take
        
        Returns
        -------
        :obj:`list` of :obj:`RigidTransform`
            sampled rigid transformations
        """
        samples = []
        for i in range(size):
            # sample random pose
            xi = self._r_xi_rv.rvs(size=1)
            S_xi = skew(xi)
            R_sample = scipy.linalg.expm(S_xi)
            t_sample = self._t_rv.rvs(size=1)
            samples.append(RigidTransform(rotation=R_sample,
                                          translation=t_sample,
                                          from_frame=self._from_frame,
                                          to_frame=self._to_frame))

        # not a list if only 1 sample
        if size == 1 and len(samples) > 0:
            return samples[0]
        return samples

