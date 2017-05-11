#! /usr/bin/env python

import os
import time
import pylab
from pylab import cos, sin, pi, arccos, arcsin, arctan2, sqrt, array, floor
from numpy import ndarray
from math import floor
from leap.lib.units import angles
from leap.lib.geometry import point_picking
from leap.lib.geometry import mollweide
from leap.lib.geometry import ebex_quaternion


galactic_north_equatorial = (angles.from_degrees(192.85948), angles.from_degrees(27.12825))
galactic_center_equatorial = (angles.from_degrees(266.4049948010461), angles.from_degrees(-28.93617396013869))


def eq_to_gal_quaternions(ra, dec, roll):
    if False:
        quat = [-0.196253758775, -0.483210685419, 0.699229740143, 0.488947509127]
        rotation = ebex_quaternion.Quaternion(quat)
    if True:
        euler = [1.681402537745, -1.050488402394, 5.873385265060]
        rotation = ebex_quaternion.Quaternion(euler)
    attitude = ebex_quaternion.Quaternion([ra, dec, roll])
    attitude = rotation * attitude
    return attitude.equatorial

def gal_to_eq_quaternions(lon, lat, galactic_roll):
    if False:
        quat = [-0.196253758775, -0.483210685419, 0.699229740143, 0.488947509127]
        rotation = ebex_quaternion.Quaternion(quat)
    if True:
        euler = [1.681402537745, -1.050488402394, 5.873385265060]
        rotation = ebex_quaternion.Quaternion(euler)
    attitude = ebex_quaternion.Quaternion([lon, lat, galactic_roll])
    attitude = rotation.inv() * attitude
    return attitude.equatorial


def eq_to_gal(ra, dec):
    """
    expects dec between -pi/2 and pi/2
    compares to pyephem within 0.45 arcsec
    returns lon, lat in radians
    """
    alpha = galactic_north_equatorial[0]
    delta = galactic_north_equatorial[1]
    la = angles.from_degrees(122.932 - 90.0)
    b = arcsin(sin(dec) * sin(delta) + cos(dec) * cos(delta) * cos(ra - alpha))
    l = arctan2(sin(dec) * cos(delta) - cos(dec) * sin(delta) * cos(ra - alpha), cos(dec) * sin(ra - alpha)) + la
    l += 2.0 * pylab.pi * (l < 0)
    l = l % (2.0 * pylab.pi)
    return l, b


def gal_to_eq(l, b):
    """
    Inputs:
        l: galactic longitude
        b: galactic latitude
    Returns:
        ra, dec
    compares to pyephem within 0.45 arcsec
    """
    alpha = galactic_north_equatorial[0]
    delta = galactic_north_equatorial[1]
    la = angles.from_degrees(122.932 - 90.0)
    dec = arcsin(sin(b) * sin(delta) + cos(b) * cos(delta) * sin(l - la))
    ra = arctan2(cos(b) * cos(l - la), sin(b) * cos(delta) - cos(b) * sin(delta) * sin(l - la)) + alpha
    ra += 2.0 * pylab.pi * (ra < 0)
    ra = ra % (2.0 * pylab.pi)
    return ra, dec


def eq_to_hor(ra, dec, lat, lst):
    H = lst - ra
    el = arcsin(sin(dec) * sin(lat) + cos(dec) * cos(lat) * cos(H))
    az = arccos((sin(dec) - sin(lat) * sin(el)) / (cos(lat) * cos(el)))
    flag = sin(H) > 0
    if type(flag) is ndarray:
        az[flag] = 2.0 * pi - az[flag]
    elif flag:
        az = 2.0 * pi - az
    return az, el


def hor_to_eq(az, el, lat, lst):
    dec = arcsin(sin(el) * sin(lat) + cos(el) * cos(lat) * cos(az))
    argument = (sin(el) - sin(lat) * sin(dec)) / (cos(lat) * cos(dec))
    argument = pylab.clip(argument, -1.0, 1.0)
    H = arccos(argument)
    flag = sin(az) > 0
    if type(flag) is ndarray:
        H[flag] = 2.0*pi - H[flag]
    elif flag:
        H = 2.0 * pi - H
    ra = lst - H
    ra %= 2 * pi
    return ra, dec


def eq_to_hor_wikipedia(ra, dec, lat, lst):
    H = lst - ra
    sin_a = sin(lat) * sin(dec) + cos(lat) * cos(dec) * cos(H)
    cos_A_cos_a = cos(lat) * sin(dec) - sin(lat) * cos(dec) * cos(H)
    sin_A_cos_a = -cos(dec) * sin(H)
    az = arctan2(sin_A_cos_a, cos_A_cos_a)
    r = sqrt(sin_A_cos_a ** 2 + cos_A_cos_a ** 2)
    el = arctan2(sin_a, r)
    return az, el


def angular_distance(ra0, dec0, ra1, dec1):
    dra = ra1 - ra0
    numerator = sqrt(pow(cos(dec1) * sin(dra), 2.0)
                     + pow(cos(dec0) * sin(dec1) - sin(dec0) * cos(dec1) * cos(dra), 2.0))
    denomenator = sin(dec0) * sin(dec1) + cos(dec0) * cos(dec1) * cos(dra)
    return arctan2(numerator, denomenator)

def wrap_to_pi_over_two(angle):
    if type(angle) == list:
        angle = array(angle)
    angle %= pi
    if type(angle) == ndarray:
        angle[(angle > pi/2.0)] -= pi
        return angle
    else:
        if angle > pi/2.0:
            angle -= pi
        return angle


def wrap_to_pi(angle):
    if type(angle) == list:
        angle = array(angle)
    angle %= (2 * pi)
    if type(angle) == ndarray:
        valid = ~pylab.isnan(angle)
        out_of_bounds = pylab.zeros(angle.size, dtype=bool)
        out_of_bounds[valid] = (angle[valid] > pi)
        angle[out_of_bounds] -= (2 * pi)
        return angle
    else:
        if angle > pi:
            angle -= (2 * pi)
        return angle


def wrap_to_2pi(angle):
    if type(angle) == float or type(angle) == int:
        if (angle < 0) | (angle >= 2 * pi):
            angle %= (2 * pi)
        return angle
    valid = ~pylab.isnan(angle)
    if type(angle) == list:
        angle = array(angle)
    if type(angle) == ndarray:
        out_of_bounds = pylab.zeros(angle.size, dtype=bool)
        out_of_bounds[valid] = (angle[valid] < 0) | (angle[valid] >= 2 * pi) 
        angle[out_of_bounds] %= (2 * pi)
    else:
        if (angle[valid] < 0) | (angle[valid] >= 2 * pi):
            angle[valid] %= (2 * pi)
    return angle


def test_galactic_conversions():
    lon, lat = angles.from_degrees(067.4482), angles.from_degrees(19.2373)
    ra, dec = gal_to_eq(lon, lat)
    lon2, lat2 = eq_to_gal(ra, dec)
    print "vega galactic", angles.to_degrees(lon), angles.to_degrees(lat)
    print "vega equtorial", angles.to_degrees(ra), angles.to_degrees(dec)
    print "vega galactic", angles.to_degrees(lon2), angles.to_degrees(lat2)
    lon3, lat3 = eq_to_gal_quaternions(ra, dec)
    print "vega equtorial", angles.to_degrees(ra), angles.to_degrees(dec)
    print "vega galactic", angles.to_degrees(lon3), angles.to_degrees(lat3)


if __name__ == "__main__":
    test_galactic_conversions()
