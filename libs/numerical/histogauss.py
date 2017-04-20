import pylab as pl
import numpy as np
from scipy.optimize import leastsq
import scipy


def histogauss(inputdata, bins=10, figure=pl.gcf(), units='', colorkey = 1,
               show_legend=True, ignore_nan=False, remove_n_std=None, fitfunc=None,
               legend_location=None, subfigure=0, p0=None, **kwargs):
    '''
    Histograms data and fits a gaussian. Typically used for IV curve
    saturation power analysis.

    Original version taken from pywtl/common/analysis/make_histo_pturn_plot.py

    Returns a dict with the following key, values:
        figure - a matplotlib.pyplot.Figure instance with the histogram and figure
        mean - the mean of the fit gaussian
        std - the standard deviation of the git gaussian
        fit - all parameters returned by scipy.optimize.leastsq

    WARNING - May go nuts with non gaussian data
    '''
    if len(figure.axes) == 0:
        figure.add_subplot(111)
    if len(inputdata[~np.isnan(inputdata)]) == 0:
        return {"figure": figure, "mean": np.nan, "std": np.nan, "fit": np.nan}
    if ignore_nan:
        inputdata = inputdata[~np.isnan(inputdata)]
    if remove_n_std is not None:
        inputdata = inputdata[abs(inputdata) - np.mean(inputdata) <= remove_n_std * np.std(inputdata)]
    color_dict = {0: 'g', 1: 'b', 3: 'm', 2: 'r', 4: 'k', 5: 'y', 6: 'c'}
    color = color_dict[int(colorkey)]
    if fitfunc is None:
        fitfunc = lambda p, x: p[0] * np.exp(-1 * (p[1] - x) ** 2 / (2 * p[2] ** 2))
    errfunc = lambda p, x, y: fitfunc(p, x) - y
    data = figure.axes[subfigure].hist(inputdata, bins, figure=figure, color=color, **kwargs)
    xdata = (data[1][1:] + data[1][:-1]) / 2
    if p0 is None:
        if (type(bins) == list) or (type(bins) == pl.ndarray):
            p0 = [len(inputdata) / len(bins), np.mean(inputdata), np.std(inputdata)]
        else:
            p0 = [len(inputdata) / bins, np.mean(inputdata), np.std(inputdata)]
    p1, success = leastsq(errfunc, p0[:], args=(xdata, data[0]))
    step = (max(xdata) - min(xdata)) / bins
    plottingpoints = np.arange(min(xdata) - 3.0 * step, max(xdata) + 3.0 * step, step)
    # plottingpoints = np.arange(min(xdata), max(xdata), .0001)
    if 'line_label' in kwargs:
        legend_str = "Fit %s:\nmean = %4.1f +/- %4.1f %s" % (kwargs['line_label'], p1[1], abs(p1[2]), units)
    else:
        legend_str = "Fit:\nmean = %4.1f +/- %4.1f %s" % (p1[1], abs(p1[2]), units)
    # t = "Fit:\nmean = %4.1f %s\n $\sigma$ = %4.1f %s" % (p1[1], units, abs(p1[2]), units)
    # t = "Fit: $\sigma$ = %4.1f %s" %(abs(p1[2]), units)
    if int(colorkey) < 7:
        color = color_dict[int(colorkey) + 1]
    else:
        color = color_dict[1]
    figure.axes[subfigure].plot(plottingpoints, fitfunc(p1, plottingpoints), '-%s' % color, linewidth=3, label=legend_str)
    if show_legend:
        if legend_location is not None:
            pl.legend(loc=legend_location)
        else:
            pl.legend()
    return {"figure": figure, "mean": p1[1], "std": abs(p1[2]), "fit": (p1, success)}


def histopoisson(inputdata, bins=10, figure=pl.gcf(), units='', colorkey = 1,
               show_legend=True, ignore_nan=False, remove_n_std=None, fitfunc=None,
               legend_location=None, subfigure=0, p0=None, **kwargs):
    '''
    Histograms data and fits a Poisson dist. 

    Returns a dict with the following key, values:
        figure - a matplotlib.pyplot.Figure instance with the histogram and figure
        mean - the mean of the fit gaussian
        std - the standard deviation of the git gaussian
        fit - all parameters returned by scipy.optimize.leastsq

    WARNING - May go nuts with non gaussian data
    '''
    if len(figure.axes) == 0:
        figure.add_subplot(111)
    if len(inputdata[~np.isnan(inputdata)]) == 0:
        return {"figure": figure, "amplitude": np.nan, "k": np.nan, "fit": np.nan}
    if ignore_nan:
        inputdata = inputdata[~np.isnan(inputdata)]
    if remove_n_std is not None:
        inputdata = inputdata[abs(inputdata) - np.mean(inputdata) <= remove_n_std * np.std(inputdata)]
    color_dict = {0: 'g', 1: 'b', 2: 'm', 3: 'r', 4: 'k', 5: 'y', 6: 'c'}
    color = color_dict[int(colorkey)]
    if fitfunc is None:
        fitfunc = lambda p, x: p[0] * p[1]**(x) * np.exp(-p[1]) / scipy.misc.factorial(x)
    errfunc = lambda p, x, y: fitfunc(p, x) - y
    data = figure.axes[subfigure].hist(inputdata, bins, figure=figure, color=color, **kwargs)
    xdata = (data[1][1:] + data[1][:-1]) / 2
    if p0 is None:
        if (type(bins) == list) or (type(bins) == pl.ndarray):
            p0 = [len(inputdata) / len(bins), np.mean(inputdata)]
        else:
            p0 = [len(inputdata) / bins, np.mean(inputdata)]
    p1, success = leastsq(errfunc, p0[:], args=(xdata, data[0]))
    step = (max(xdata) - min(xdata)) / bins
    plottingpoints = np.arange(min(xdata) - 3.0 * step, max(xdata) + 3.0 * step, step)
    # plottingpoints = np.arange(min(xdata), max(xdata), .0001)
    if 'label' in kwargs:
        legend_str = "Fit %s:\nmean = %4.1f  %s" % (kwargs['label'], p1[1], units)
    else:
        legend_str = "Fit:\nmean = %4.1f  %s" % (p1[1],  units)
    if int(colorkey) < 7:
        color = color_dict[int(colorkey) + 1]
    else:
        color = color_dict[1]
    figure.axes[subfigure].plot(plottingpoints, fitfunc(p1, plottingpoints), '-%s' % color, linewidth=3, label=legend_str)
    if show_legend:
        if legend_location is not None:
            pl.legend(loc=legend_location)
        else:
            pl.legend()
    return {"figure": figure, "mean": p1[1], "fit": (p1, success)}

if __name__ == "__main__":
    print "-- Testing histogauss --"
    mean = 5.
    std = 1.
    data = np.random.normal(5., 1., 1000)
    hist = histogauss(data, bins=20, range=(0, 10))
    hist['figure'].suptitle('Test Gaussian - Input mean %4.1f. Input std %4.1f' % (mean, std))
    hist['figure'].get_axes()[subfigure].set_xlabel('Arbitrary')
    hist['figure'].get_axes()[subfigure].set_ylabel('Counts')
    pl.show()
