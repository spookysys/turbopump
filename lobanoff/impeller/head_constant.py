"""Figure 3-3: Head Constant Ku [US]"""
from __future__ import print_function
from itertools import chain
import numpy as np
from matplotlib import pyplot as plt
from misc import memoized
from . import _jsondata as _module_jsondata


def _jsondata():
    return _module_jsondata()['head_constant']


@memoized
def get_limits():
    """Return the vane-counts for which there is data"""
    vanes = list(chain.from_iterable(
        x['vanes'] for x in _jsondata()
    ))
    return min(vanes), max(vanes)


@memoized
def get_coeffs():
    """Calculate a set of coefficients relating vane-count to Ku at Ns=0
    (="offset"), and a slope which is the same for all vane-counts.
    """
    points = [x['points'] for x in _jsondata()]
    slope = np.average([(x[1][1] - x[0][1]) / (x[1][0] - x[0][0]) for x in points])
    offsets = [x[0][1] - slope * x[0][0] for x in points]

    vanes = [x['vanes'] for x in _jsondata()]
    offsets_expanded = [[x] * len(y) for x, y in zip(offsets, vanes)]
    offsets_expanded = list(chain.from_iterable(offsets_expanded))
    vanes_expanded = list(chain.from_iterable(vanes))
    coeffs = np.polyfit(vanes_expanded, offsets_expanded, 2)

    return (coeffs, slope)


def plot():
    offset_coeffs, slope = get_coeffs()

    # Plot fitted curves
    for vanes in range(get_limits()[0], get_limits()[1] + 1):
        offset = np.polyval(offset_coeffs, vanes)
        x = np.linspace(0, 3600)
        y = offset + slope * x
        plt.plot(x, y)
        plt.annotate(str(vanes), xy=(x[-1], y[-1]))

    plt.gca().set_title(__doc__)
    plt.gca().set_xticks(np.arange(0, 3600 + 1, 400))
    plt.gca().set_yticks(np.arange(0.7, 1.3, 0.05))
    plt.xlabel('Ns - Specific Speed')
    plt.ylabel('Ku - Head Constant')
    plt.grid()
    plt.show()


if __name__ == '__main__':
    plot()