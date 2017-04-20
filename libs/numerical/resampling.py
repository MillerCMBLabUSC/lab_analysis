import pylab


def resample(target_frequency, source_frequency, data):
    source_period = 1.0 / source_frequency
    stop = len(data) * source_period
    source_xs = pylab.arange(0.0, stop, source_period)
    target_period = 1.0 / target_frequency
    target_xs = pylab.arange(0.0, stop, target_period)
    if len(source_xs) > len(data):
        source_xs = source_xs[:-1]
    return pylab.interp(target_xs, source_xs, data)
