"""
Generic Random Variable wrapper classes 
Author: Jeff Mahler
"""
from abc import ABCMeta, abstractmethod

import numpy as np
import scipy.stats

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

