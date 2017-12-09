#! /usr/bin/python

import numpy as np
import pylab as pl
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import healpy
import scipy
from scipy import signal
from lab_analysis.libs.geometry import coordinates
from lab_analysis.apps.simulation import default_settings
from lab_analysis.apps.simulation import pointing
from lab_analysis.libs.units.angles import *


#class Simulator(lab_app.App):
class Simulator(object):
		
	def run(self):
		self.settings = default_settings.SimulatorSettings()
		times = np.linspace(0, self.settings.t_end, self.settings.t_end/self.settings.dt)
		maps = healpy.read_map(self.load_map('sevem_1024_full'), field = (0, 1, 2))
		create_pointing = pointing.CreatePointing()
		boresight_pointing = create_pointing.make_boresight_pointing()
		for bolo in range(0, self.settings.num_bolos):
			self.run_one_bolo(bolo, boresight_pointing, maps, times)
			
		plt.show()
	
	def run_one_bolo(self, bolo, boresight_pointing, maps, times):
		detector_pointing = self.rotate_boresight_pointing(boresight_pointing, bolo)
		lat, lon = coordinates.eq_to_gal(detector_pointing[0], detector_pointing[1])
		bolo_i = healpy.get_interp_val(maps[0], pl.pi/2.0-lat, lon)
		bolo_q = healpy.get_interp_val(maps[1], pl.pi/2.0-lat, lon)
		bolo_u = healpy.get_interp_val(maps[2], pl.pi/2.0-lat, lon)
		bolo_alpha = 1/2. * pl.arctan2(bolo_u, bolo_q)
		bolo_p = pl.sqrt(bolo_q**2 + bolo_u**2)/bolo_i
		hwp_angle = np.sin(2*pl.pi * self.settings.f_hwp * times)
		data = 1/2.* (bolo_i + bolo_p * pl.cos(4*hwp_angle - 2*bolo_alpha))
		data = self.add_hwpss(times, data, hwp_angle)
		data = self.add_nonlinearity(data)
		data = self.add_noise(data)
		self.plot_data(times, data)
		#self.make_map(data, detector_pointing, lat, lon)
	
	
	def rotate_boresight_pointing(self, boresight_pointing, bolo_number):
		#this is a basic rotation function. the three bolos are arranged in a triangle with base 0.005 (~50m) and height 0.005 (~50m)
		#if a fourth bolo is added, it will be at the center of the triangle (the boresight pointing)
		#a little clunky but I can turn this into a dictionary later with diff. adjustments depending on the number/arrangement of bolos
		boresight_pointing = list(boresight_pointing)
		if bolo_number == 0:
			boresight_pointing[1] += 0.0025
		elif bolo_number == 1:
			boresight_pointing[0] += 0.0025
			boresight_pointing[1] -= 0.0025
		elif bolo_number == 2:
			boresight_pointing[0] -= 0.0025
			boresight_pointing[1] -= 0.0025
		boresight_pointing = tuple(boresight_pointing)
		return boresight_pointing
	
	def load_map(self, map_name):
		dict = {'commander_1024_full':'/home/rashmi/maps/planck_commander_1024_full_test.fits',
			'nilc_1024_full':'/home/rashmi/maps/planck_nilc_1024_full_test.fits',
			'sevem_1024_full':'/home/rashmi/maps/planck_sevem_1024_full_test.fits',
			'smica_1024_full':'/home/rashmi/maps/planck_smica_1024_full_test.fits'}
		return dict.get(map_name)
	
	def add_nonlinearity(self, signal, signal_min=-0.2):
		#found this in the leap code
		signal -= signal_min
		compressed_signal = signal - 0.04*signal**2 + 0.001*signal**3
		return compressed_signal + signal_min
	
	def add_noise(self, signal):
		sigma = self.settings.NET / pl.sqrt(self.settings.dt)
		noise = scipy.stats.norm.rvs(scale = sigma, size = signal.size)
		return signal + noise
	
	def add_hwpss(self, times, signal, hwp_angle):
		#approximation we are using for now: A1 = 50mK, A2 = 100, A4 = 200. All other coeffs = 0.
		hwpss = 0.05*pl.cos(hwp_angle) + 0.1*pl.cos(2*hwp_angle) + 0.2*pl.cos(4*hwp_angle)
		return signal + hwpss
	
	def plot_data(self, times, data_to_plot):
		plt.axhline(linewidth = 0.5, color = 'k')
		#plt.plot(times, data_to_plot, markersize = 1.5)
		plt.plot(times, data_to_plot,'.', markersize = 1.5)
		plt.xlabel('Time (s)')
		plt.ylabel('K_cmb')
	
	def make_map(self, data, detector_pointing, lat, lon):
		detector_pointing = list(detector_pointing)
		nside = 1024
		npix = healpy.nside2npix(nside)
		indices = healpy.ang2pix(nside, lon, lat, lonlat = True)
		hpmap = np.zeros(npix, dtype = np.float)
		hpmap[indices] += data[indices]
		healpy.mollview(hpmap)


if __name__ == "__main__":
	simulator = Simulator()
	simulator.run()
	#simulator.end()
