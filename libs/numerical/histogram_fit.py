#! /usr/bin/python2

import pylab
import scipy.stats


def histogram_and_fit(distribution_name, points, bins=10, units="", **fit_kwargs):
    histogram = pylab.hist(points, bins)
    bins = histogram[1]
    bin_step = pylab.median(pylab.diff(bins))
    distribution = _get_distribution(distribution_name)
    fit = distribution.fit(points, **fit_kwargs)
    xs = pylab.linspace(min(bins), max(bins), 1000)
    ys = distribution.pdf(xs, *fit)
    label = _get_label(distribution_name, fit, units)
    pylab.plot(xs, ys*len(points)*bin_step, 'r', label=label)
    pylab.legend()
    return fit


def _get_distribution(distribution_name):
    if distribution_name in ["gaussian", "normal"]:
        return scipy.stats.norm
    if distribution_name == "rayleigh":
        return scipy.stats.rayleigh


def _get_label(distribution_name, fit, units):
    if distribution_name in ["gaussian", "normal"]:
        s = "best fit mean: %.1f %s" % (fit[0], units)
        s += "\nbest fit sigma: %.1f %s" % (fit[1], units)
        return s
    if distribution_name == "rayleigh":
        return "best fit $\sigma$ = %.1f %s" % (fit[1], units)
    return ""


def _generate_random_points(distribution_name, num_points, **kwargs):
    distribution = _get_distribution(distribution_name)
    return distribution.rvs(size=num_points, **kwargs)


if __name__ == "__main__":
    pylab.seed(0)
    num_points = 10000
    pylab.subplot(211)
    bins = pylab.arange(0.0, 15.0, 0.2)
    points = _generate_random_points("rayleigh", num_points, scale=3.0)
    fit = histogram_and_fit("rayleigh", points, bins, "arcmin", **{"floc": 0})
    print "returned fit", fit
    pylab.subplot(212)
    bins = pylab.arange(-10.0, 10.0, 0.2)
    points = _generate_random_points("gaussian", num_points, scale=3.0)
    fit = histogram_and_fit("gaussian", points, bins, "arcsec")
    print "returned fit", fit
    pylab.show()
