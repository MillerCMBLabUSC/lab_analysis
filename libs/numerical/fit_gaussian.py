import numpy as np
from scipy.optimize import leastsq
import pylab as pl


def fit_gaussian(xdata, ydata, units='', figure=None, show_legend=True, label="raw_data"):
    '''
    Perform least squared fitting with a gaussian
    '''
    from scipy import optimize
    xdata = np.array(xdata)
    ydata = np.array(ydata)
    fitfunc = lambda p, x: p[0] * np.exp(-1 * (p[1] - x) ** 2 / (2 * p[2] ** 2)) + p[3]
    errfunc = lambda p, x, y: fitfunc(p, x) - y
    #Initial guesses
    p = [0, 0, 0, 0]
    p[0] = max(ydata)
    p[1] = xdata[np.where(ydata == max(ydata))[0]][0]
    p[2] = xdata[1] - xdata[0]    # Assume really wide distribution to start
    p[3] = np.mean(ydata)
    output = []
    p1, success = leastsq(errfunc, p[:], args=(xdata, ydata))
    t = "Fit: Peak:%4.2f Cent:%4.2f Wid:%4.3f %s" % (p[0], p1[1], abs(p1[2]), units)
    if not figure is None:
        pl.plot(xdata, ydata, 'o', label=label)
        pl.plot(xdata, fitfunc(p1, xdata), label=t)
        if show_legend:
            pl.legend(loc='lower right')
    return {"figure": figure, "height": p[0], "mean": p1[1], "std": abs(p1[2]),
            "fit": (p1, success)}

def gaus_fit_3params(hist_bins, hist_y, x_for_fit, low_bound_std=None):
    """
    hist_bins : edges of the bins of the histogram (what is fed to pl.hist)
    hist_y : histogram values
    x_for_fit : x-value that will be used to return fit, set to None to avoid returning a fit
    low_bound_std : lower accepted value for the sigma, None means no bounding

    returns :

    """
    bin_centers = pl.array(hist_bins[:-1]) + (hist_bins[1] - hist_bins[0])/2.

    #boundaries for parameters
    lbound = lambda p, x: 1e4*pl.sqrt(p-x) if (x < p) else 0
    #ubound = lambda p, x: 1e4*pl.sqrt(x-p) if (x > p) else 0
    #bound = lambda p, x: lbound(p[0], x) + ubound(p[1], x)

    #error function
    if low_bound_std is None:
        errfunc = lambda p, x, y: gauss_func_3params(p, x) - y
    else:
        errfunc = lambda p, x, y: gauss_func_3params(p, x) - y + lbound(low_bound_std, p[2])

    #initial parameters
    p0 = [0, 0, 0]
    p0[0] = max(hist_y)
    p0[1] = bin_centers[pl.where(hist_y == max(hist_y))[0]][0]
    p0[2] = bin_centers[1] - bin_centers[0]    # Assume really wide distribution to start

    p1, success = leastsq(errfunc, p0[:], args=(bin_centers, hist_y))

    if not x_for_fit is None:
        fit_ = gauss_func_3params(p1, x_for_fit)
    else:
        fit_ = None
    return p1, fit_

def gauss_func_3params(p, x):
    """
    gaussian with 0 offset
    """
    return p[0] * pl.exp(-1 * (p[1] - x) ** 2 / (2 * p[2] ** 2))


if __name__ == "__main__":
    print "-- Testing fit gaussian -- "
    fig = pl.figure()
    p = [10, 5, 3]
    xdata = np.arange(0, 20, 0.1)
    ydata = [p[0] * np.exp(-1 * (p[1] - x) ** 2 / (2 * p[2] ** 2)) for x in xdata]
    fit_gaussian(xdata, ydata, figure=fig)
    fig2 = pl.figure()
    ydata2 = np.array(ydata) * 0.1
    fit_gaussian(xdata, ydata2, figure=fig2)
    pl.show()
