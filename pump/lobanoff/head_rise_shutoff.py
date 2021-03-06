"""Figure 3-2: Percent Head Rise at Shutoff, and whether there's droop"""
from __future__ import print_function
import numpy as np
from matplotlib import pyplot as plt
from numpy.polynomial import polynomial
from utils import memoized, polyfit2d
from units import ureg
from pump.lobanoff._data import _data as _lobanoff_data
from pump.lobanoff.discharge_angle import get_limits as get_vane_limits


def _data():
    return _lobanoff_data()['head_rise']


@memoized
def get_vane_limits(droop=None):
    """Return the minimum and maximum vane-count"""
    vanes = [
        x['vanes']
        for x in _data()
        if droop is None
        or (droop and x['droop'])
        or (not droop and not x['droop'])
    ]
    return min(vanes), max(vanes)


@memoized
def get_coeffs():
    """Polynomial coefficients relating vane-count and specific speed to percent head rise"""
    fitdata = np.ndarray(shape=(3, 0), dtype=float)
    for curve in _data():
        x = np.ones(len(curve['points'])) * np.average(curve['vanes'])
        y, z = np.transpose(curve['points'])
        fitdata = np.append(fitdata, [x, y, z], axis=1)
    return polyfit2d(*fitdata, order=3)


@memoized
def get_Ns_limit_coeffs():
    """Polynomial coefficients relating vane-count to highest Ns in graph"""
    vanes = [x['vanes'] for x in _data()]
    val = [x['points'][-1][0] for x in _data()]
    coeffs = np.polyfit(vanes, val, 2)
    test = np.polyval(coeffs, vanes)
    return coeffs


def plot():
    """Plot raw data and polynomial approximation"""
    plt.figure()

    # Plot data
    for curve in _data():
        vanes = curve['vanes']
        x, y = np.transpose(curve['points']).tolist()
        plt.plot(x, y, 'r--')
        label = str(curve['vanes']) + ' vanes, ' + str(curve['discharge_angle']) + ' deg' + (', droop' if curve['droop'] else '')
        plt.annotate(label, xy=(x[-1], y[-1]))

    # Plot fitted curves
    for vanes in range(get_vane_limits()[0], get_vane_limits()[1] + 1):
        endpoint = np.polyval(get_Ns_limit_coeffs(), vanes)
        x = np.linspace(0, endpoint)
        y = polynomial.polyval2d(np.ones(len(x)) * vanes, x, get_coeffs())
        plt.plot(x, y, 'g-')

    # plot limit of data
    vanespace = np.linspace(*get_vane_limits())
    limit_Ns = np.polyval(get_Ns_limit_coeffs(), vanespace)
    limit_phr = polynomial.polyval2d(vanespace, limit_Ns, get_coeffs())
    plt.plot(limit_Ns, limit_phr)

    plt.gca().set_title(__doc__)
    plt.gca().set_xticks(np.arange(0, endpoint + 1, 400))
    plt.gca().set_yticks(np.arange(0, 65, 5))
    plt.xlabel('Ns - Specific Speed')
    plt.ylabel('Percent Head Rise from B.E.P. to shutoff')
    plt.grid()
    plt.draw()


if __name__ == '__main__':
    plot()
    plt.show()


@ureg.wraps('pct', ('Ns_loba', 'count'))
def calc(Ns, vanes):
    endpoint = np.polyval(get_Ns_limit_coeffs(), vanes)
    assert 0 <= Ns <= endpoint
    return polynomial.polyval2d(vanes, Ns, get_coeffs())
