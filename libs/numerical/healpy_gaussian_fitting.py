#! /usr/bin/python2

import pylab
import healpy
import scipy.stats
from scipy.optimize import curve_fit
from leap.lib.geometry import coordinates
from leap.lib.units import angles


def fit_map(hit_map, signal_map, guess_center, guess_fwhm):
    radius = guess_fwhm*3.0
    nside = healpy.npix2nside(hit_map.size)
    mask = hit_map == 0
    mask |= pylab.isnan(signal_map)
    indices = _get_close_pixels(guess_center, radius, nside, mask)[0]
    p0 = guess_center + [1.0, guess_fwhm]
    def _model(indices, *params):
        center_lon, center_lat, scale, fwhm = params
        thetas, lons = healpy.pix2ang(nside, indices)
        lats = pylab.pi/2.0 - thetas
        dxs = (lons - center_lon) * pylab.cos(lats)
        dxs = (dxs + pylab.pi) % (2.0*pylab.pi) - pylab.pi
        dys = lats - center_lat
        return normal_2d(dxs, dys, scale, fwhm=fwhm)
    fit = curve_fit(_model, indices, signal_map[indices], p0=p0)
    return fit


def fit_string(fit):
    popt, pcov = fit
    if type(pcov) is float and pcov == pylab.inf:
        return "no fit"
    center = popt[0:2]
    scale, fwhm = popt[2:4]
    center_error = pylab.mean([pylab.sqrt(pcov[0][0]), pylab.sqrt(pcov[1][1])])
    fwhm_error = pylab.sqrt(pcov[3][3])
    s = "center: %.2f %.2f degrees" % tuple(map(angles.to_degrees, center))
    s += ", fwhm: %.2f arcmin" % angles.to_arcmin(fwhm)
    s += ", center error: %.2f degrees" % angles.to_degrees(center_error)
    s += ", fwhm error: %.2f arcmin" % angles.to_arcmin(fwhm_error)
    return s


def normal_2d(dx, dy, scale, fwhm=None, sigma=None):
    # not yet bivariate
    if fwhm is None and sigma is None:
        raise Exception("must specify fwhm or sigma")
    if fwhm is not None and sigma is not None:
        raise Exception("can't specify both fwhm and sigma")
    if fwhm is not None and sigma is None:
        sigma = fwhm / (2.0*pylab.sqrt(2.0*pylab.log(2.0)))
    return scale*pylab.exp(-(dx*dx+dy*dy)/(2.0*sigma*sigma))


def _get_close_pixels(center, radius, nside, additional_mask=None):
    npix = healpy.nside2npix(nside)
    indices = pylab.arange(npix)
    thetas, lons = healpy.pix2ang(nside, indices)
    lats = pylab.pi/2.0 - thetas
    distances = coordinates.angular_distance(lons, lats, center[0], center[1])
    mask = distances > radius
    if additional_mask is not None:
        mask |= additional_mask
    close_indices = indices[~mask]
    close_dxs = pylab.fabs(lons[close_indices] - center[0]) * pylab.cos(lats[close_indices])
    close_dxs = (close_dxs + pylab.pi) % (2.0*pylab.pi) - pylab.pi
    close_dys = lats[close_indices] - center[1]
    return close_indices, close_dxs, close_dys


def _generate_beam_map(nside, center, scale, fwhm, radius):
    npix = healpy.nside2npix(nside)
    hit_map = pylab.zeros(npix, pylab.uint64)
    signal_map = pylab.zeros(npix, pylab.float64)
    indices, dxs, dys = _get_close_pixels(center, radius, nside)
    hit_map[indices] += 1
    signal_map[indices] += normal_2d(dxs, dys, scale, fwhm=fwhm)
    signal_map[indices] += scipy.stats.norm.rvs(scale=scale*0.01, size=indices.size)
    signal_map[hit_map > 0]
    return hit_map, signal_map


def run_test():
    nside = 512
    center = map(angles.from_degrees, [-92.0, -1.0])
    scale = 1.0
    fwhm = angles.from_arcmin(16.0)
    radius = angles.from_degrees(3.0)
    hit_map, signal_map = _generate_beam_map(nside, center, scale, fwhm, radius)

    guess_center = map(angles.from_degrees, [-91.5, -1.1])
    guess_fwhm = angles.from_arcmin(24.0)
    fit = fit_map(hit_map, signal_map, guess_center, guess_fwhm)
    print fit_string(fit)

    signal_map[hit_map == 0] = pylab.nan
    xsize = 1000
    reso_arcmin = angles.to_arcmin(radius*2.5) / float(xsize)
    #healpy.mollview(signal_map)
    healpy.gnomview(signal_map, rot=map(angles.to_degrees, center), xsize=xsize, reso=reso_arcmin)
    pylab.show()


if __name__ == "__main__":
    run_test()
