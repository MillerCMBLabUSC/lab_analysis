import pylab as pl
import leap.lib.numerical.wrapping as wrapping


def from_healpy_to_galactic(phi_rad, theta_rad):
    """
    Converts the healpy coordinates in galactic longitude and latitude.

    phi_rad is [0 to 2pi]
    theta_rad is [0 to pi]

    galactic_longitude is [-pi to pi]
    galactic_latitude is [-pi/2 to pi/2]
    """
    galactic_lon = wrapping.wrap_around_value(phi_rad, 0., 2.*pl.pi)
    galactic_lat = pl.pi/2. - theta_rad
    return galactic_lon, galactic_lat


def from_galactic_to_healpy(galactic_lon, galactic_lat):
    """
    Converts galactic longitude and latitude in the healpy coordinates.

    galactic_longitude is [-pi to pi]
    galactic_latitude is [-pi/2 to pi/2]

    phi_rad is [0 to 2pi]
    theta_rad is [0 to pi]
    """
    phi_rad = wrapping.wrap_around_value(galactic_lon, pl.pi, 2.*pl.pi)
    theta_rad = pl.pi/2. - galactic_lat
    return phi_rad, theta_rad
