"""Figure 3-8: K3 = C3 / sqrt(2gH) - Volute Velocity Constant, reduced volute velocity"""
import numpy as np
from matplotlib import pyplot as plt
from utils import memoized
from units import ureg
from pump.lobanoff._data import _data as _lobanoff_data


def _data():
    return _lobanoff_data()['volute_constant']


def _points():
    return np.transpose(_data())


@memoized
def get_coeffs():
    """Polynomial coefficients"""
    x, y = _points()
    return np.polyfit(x, y, 3)


@memoized
def get_Ns_limits():
    """Get the allowable range for Ns"""
    x, _ = _points()
    return min(x), max(x)


def plot():
    """Plot raw data and polynomial approximation"""
    plt.figure()

    # Plot data
    x, y = _points()
    plt.plot(x, y, 'r--')

    # Plot fitted curve
    x = np.linspace(*get_Ns_limits())
    y = np.polyval(get_coeffs(), x)
    plt.plot(x, y, 'g-')

    plt.gca().set_title(__doc__)
    plt.gca().set_xticks(np.arange(0, 3400 + 400, 400))
    plt.gca().set_yticks(np.arange(0.05, 0.75 + 0.05, 0.05))
    plt.xlabel('Ns - Specific Speed')
    plt.ylabel('K3 - Volute Velocity Constant')
    plt.grid()
    plt.draw()


if __name__ == '__main__':
    plot()
    plt.show()


@ureg.wraps('', ('Ns_loba'))
def calc(Ns):
    startpoint, endpoint = get_Ns_limits()
    assert startpoint <= Ns <= endpoint
    return np.polyval(get_coeffs(), Ns)
