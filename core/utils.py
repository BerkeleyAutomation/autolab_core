"""
Commonly used helper functions
Author: Jeff Mahler
"""
import matplotlib.pyplot as plt
import numpy as np

def gen_experiment_id(n=10):
    """Generate a random string with n characters.

    Parameters
    ----------
    n : int
        The length of the string to be generated.

    Returns
    -------
        A string with only alphabetic characters. 
    """
    chrs = 'abcdefghijklmnopqrstuvwxyz'
    inds = np.random.randint(0,len(chrs), size=n)
    return ''.join([chrs[i] for i in inds])

def histogram(values, num_bins, bounds, normalized=True, plot=False, color='b'):
    """Generate a histogram plot.

    Parameters
    ----------
    values : :obj:`numpy.ndarray`
        An array of values to put in the histogram.

    num_bins : int
        The number equal-width bins in the histogram.

    bounds : :obj:`tuple` of float
        Two floats - a min and a max - that define the lower and upper
        ranges of the histogram, respectively.

    normalized : bool
        If True, the bins will show the percentage of elements they contain
        rather than raw counts.

    plot : bool
        If True, this function uses pyplot to plot the histogram.

    color : :obj:`str`
        The color identifier for the plotted bins.

    Returns
    -------
    :obj:`tuple of `:obj:`numpy.ndarray`
        The values of the histogram and the bin edges as ndarrays.
    """
    hist, bins = np.histogram(values, bins=num_bins, range=bounds)
    width = (bins[1] - bins[0])
    if normalized:
        if np.sum(hist) > 0:
            hist = hist.astype(np.float32) / np.sum(hist)
    if plot:
        plt.bar(bins[:-1], hist, width=width, color=color)    
    return hist, bins

def skew(xi):
    """Return the skew-symmetric matrix that can be used to calculate
    cross-products with vector xi.

    Multiplying this matrix by a vector `v` gives the same result
    as `xi x v`.

    Parameters
    ----------
    xi : :obj:`numpy.ndarray` of float
        A 3-entry vector.

    Returns
    -------
    :obj:`numpy.ndarray` of float
        The 3x3 skew-symmetric cross product matrix for the vector.
    """
    S = np.array([[0, -xi[2], xi[1]],
                  [xi[2], 0, -xi[0]],
                  [-xi[1], xi[0], 0]])
    return S

def deskew(S):
    """Converts a skew-symmetric cross-product matrix to its corresponding
    vector. Only works for 3x3 matrices.

    Parameters
    ----------
    S : :obj:`numpy.ndarray` of float
        A 3x3 skew-symmetric matrix.

    Returns
    -------
    :obj:`numpy.ndarray` of float
        A 3-entry vector that corresponds to the given cross product matrix.
    """
    x = np.zeros(3)
    x[0] = S[2,1]
    x[1] = S[0,2]
    x[2] = S[1,0]
    return x

def reverse_dictionary(d):
    """ Reverses the key value pairs for a given dictionary.

    Parameters
    ----------
    d : :obj:`dict`
        dictionary to reverse

    Returns
    -------
    :obj:`dict`
        dictionary with keys and values swapped
    """
    rev_d = {}
    [rev_d.update({v:k}) for k, v in d.iteritems()]
    return rev_d
