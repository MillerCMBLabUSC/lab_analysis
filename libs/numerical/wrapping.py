#! /usr/bin/python2
import pylab as pl
import scipy.stats


def wrap_around_value(array, value, range_):
    #makes sure array is a numpy array
    type_in = type(array)
    if type_in == pl.ndarray:
        pass
    elif type_in == list:
        array = pl.array(array)
    elif type_in == float or type_in == int or type_in == pl.float64:
        array = pl.array([array])
    else:
        print("wrap_around_value() : unknown type -> pdb")
        pdb.set_trace()

    min_value = value-range_/2.0
    max_value = value+range_/2.0
    wrapped_array = wrap(array, min_value, max_value)

    #returns proper type
    if type_in == pl.ndarray:
        return wrapped_array
    elif type_in == list:
        return list(wrapped_array)
    elif type_in == float or type_in == pl.float64:
        return float(wrapped_array[0])
    elif type_in == int:
        return int(wrapped_array[0])


def unwrap(xs, min_value, max_value, in_place=False, jump_fraction=0.5):
    range_ = max_value - min_value
    jump_threshold = range_ * jump_fraction
    diffs = pl.diff(xs)
    octave_diffs = pl.zeros(len(xs)-1, dtype=pl.int64)
    octave_diffs[diffs > jump_threshold] = -1
    octave_diffs[diffs < -jump_threshold] = 1
    octaves = pl.append(0, pl.cumsum(octave_diffs))
    if in_place:
        xs += octaves * range_
    else:
        return xs + octaves * range_

def unwrap_inverse(xs, min_value, max_value, in_place=False, jump_fraction=0.5):
    range_ = max_value - min_value
    jump_threshold = range_ * jump_fraction
    diffs = pl.diff(xs)
    octave_diffs = pl.zeros(len(xs)-1, dtype=pl.int64)
    octave_diffs[diffs > jump_threshold] = 1
    octave_diffs[diffs < -jump_threshold] = -1
    octaves = pl.append(0, pl.cumsum(octave_diffs))
    if in_place:
        xs += octaves * range_
    else:
        return xs + octaves * range_


def wrap(xs, min_value, max_value):
    return (xs - min_value) % (max_value - min_value) + min_value


def _test_unwrap():
    pl.seed(1)
    xs = pl.cumsum(scipy.stats.norm.rvs(scale=1000, size=10000))
    axes = pl.subplot(411)
    pl.plot(xs)
    xs %= 2**16
    pl.subplot(412, sharex=axes)
    pl.plot(xs)
    in_place = False
    if in_place:
        pl.subplot(413, sharex=axes)
        unwrap(xs, 0, 2**16, True)
        pl.plot(xs)
        pl.subplot(414, sharex=axes)
        pl.plot(xs)
    else:
        pl.subplot(413, sharex=axes)
        pl.plot(unwrap(xs, 0, 2**16))
        pl.subplot(414, sharex=axes)
        pl.plot(xs)
    pl.show()


def _test_wrap():
    print wrap(10, 0, 360)
    print wrap(370, 0, 360)
    print wrap(-10, 0, 360)
    print wrap(721, 0, 360)
    print wrap(-10, -180, 180)
    print wrap(-10, -180, 0)


if __name__ == "__main__":
    _test_unwrap()
    _test_wrap()
