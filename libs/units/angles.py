import pylab as pl
from leap.lib.numerical.wrapping import wrap

# All functions in this code convert from/to RADIANS.
# Therefore "from_degrees" converts from degrees to radians. "to_degrees" converts from 
# radians to degrees.

def from_hour_min_sec(angle):
    '''
    Converts an angle from hours, minutes, seconds to 0-2pi
    input:
        angle - A tuple or list of tuples in the form (hour, min, sec)
    output:
        angle - Either a single value or numpy.array of angles in range 0 to 2 pi
    '''
    if type(angle) == list:
        angle = pl.array(angle)
        decimal_rep = angle[:, 0] + angle[:, 1] / 60. + angle[:, 2] / (60. * 60.)
    else:
        decimal_rep = angle[0] + angle[1] / 60. + angle[2] / (60. * 60.)
    return decimal_rep * pl.pi / 12.


def from_degree_arcmin_arcsec(angle):
    '''
    Converts an angle from degrees, arcmin, seconds to 0-2pi.
    input:
        angle - Either a tuple or list of tuples in the form (degree, armin, arcsec)
    output:
        angle - Either a single value or numpy.array of angles in range 0 to 2 pi
    WARNING - if degree is negative the whole value is assumed to be negative
    '''
    if type(angle) == list:
        angle = [(x[0], x[0] / abs(x[0]) * x[1], x[0] / abs(x[0]) * x[2]) for x in angle]
        angle = pl.array(angle)
        return from_degrees(angle[:, 0]) + from_arcmin(angle[:, 1]) + from_arcsec(angle[:, 2])
    else:
        if angle[0] < 0:
            angle = (angle[0], angle[0] / abs(angle[0]) * angle[1], angle[0] / abs(angle[0]) * angle[2])
        return from_degrees(angle[0]) + from_arcmin(angle[1]) + from_arcsec(angle[2])


def from_hours(angle):
    if type(angle) == list:
        angle = pl.array(angle)
    return angle * pl.pi / 12.


def to_hours(angle):
    if type(angle) == list:
        angle = pl.array(angle)
    return angle * 12. / pl.pi


def from_seconds(angle):
    if type(angle) == list:
        angle = pl.array(angle)
    return angle / 3600. * pl.pi / 12.


def to_seconds(angle):
    if type(angle) == list:
        angle = pl.array(angle)
    return angle * 12. * 3600. / pl.pi


def from_degrees(angle):
    if type(angle) == list:
        angle = pl.array(angle)
    return angle * pl.pi / 180.


def to_degrees(angle):
    if type(angle) == list:
        angle = pl.array(angle)
    return angle * 180. / pl.pi


def to_arcmin(angle):
    if type(angle) == list:
        angle = pl.array(angle)
    return angle * 180. / pl.pi * 60.


def from_arcmin(angle):
    if type(angle) == list:
        angle = pl.array(angle)
    return angle / 60. * pl.pi / 180.


def to_arcsec(angle):
    if type(angle) == list:
        angle = pl.array(angle)
    return angle * 180. / pl.pi * 3600.


def from_arcsec(angle):
    if type(angle) == list:
        angle = pl.array(angle)
    return angle / 3600. * pl.pi / 180.


def dddmmss_abs_rounded(angle):
    angle = abs(angle)
    angle_degrees = int(pl.floor(to_degrees(angle)))
    angle_arcmin = int(pl.floor(to_arcmin(angle - from_degrees(angle_degrees))))
    angle_arcsec = int(round(to_arcsec(angle - from_degrees(angle_degrees) - from_arcmin(angle_arcmin))))
    return angle_degrees, angle_arcmin, angle_arcsec

def to_degrees_minutes_seconds_string(angle):
    sign = pl.sign(angle)
    angle_in_degrees = to_degrees(abs(angle))
    integer_degrees = int(pl.floor(angle_in_degrees))
    remainder_in_minutes = (angle_in_degrees - integer_degrees)*60.0
    integer_minutes = int(pl.floor(remainder_in_minutes))
    remainder_in_seconds = (remainder_in_minutes - integer_minutes)*60.0
    return "%02i:%02i:%0.3f" % (sign*integer_degrees, integer_minutes, remainder_in_seconds)


def to_hours_minutes_seconds_string(angle):
    sign = pl.sign(angle)
    angle_in_hours = to_hours(abs(angle))
    integer_hours = int(pl.floor(angle_in_hours))
    remainder_in_minutes = (angle_in_hours - integer_hours)*60.0
    integer_minutes = int(pl.floor(remainder_in_minutes))
    remainder_in_seconds = (remainder_in_minutes - integer_minutes)*60.0
    return "%02i:%02i:%0.3f" % (sign*integer_hours, integer_minutes, remainder_in_seconds)


def wrapped_angle_distance(angle1, angle2, low=-pl.pi, high=pl.pi):
    angle1 = wrap(angle1, low, high)
    angle2 = wrap(angle2, low, high)
    max_angle = max(angle1, angle2)
    min_angle = min(angle1, angle2)
    distance1 = abs(max_angle-min_angle)
    distance2 = abs(high-max_angle) + abs(min_angle-low)
    return min(distance1, distance2)


if __name__ == "__main__":
    angle1 = from_degrees(179)
    angle2 = from_degrees(-179)
    print 'angle 1 is ', to_degrees(angle1), 'degrees'
    print 'angle 2 is ', to_degrees(angle2), 'degrees'
    print 'distance is', to_degrees(wrapped_angle_distance(angle1, angle2, low=0, high=2*pl.pi)), 'degrees'
