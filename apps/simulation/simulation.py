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

np.set_printoptions(edgeitems = 50)

#class Simulator(lab_app.App):
class Simulator(object):
		
	def run(self):
		bolos = 1
		t_end = 1800.  #seconds
		dt = 0.5       #seconds
		f_hwp = 2      #Hz
		times = np.linspace(0, t_end, t_end/dt)
		maps = healpy.read_map(self.load_map('commander_1024_full'), field = (0, 1, 2))
		create_pointing = pointing.CreatePointing()
		#boresight_pointing = create_pointing.make_boresight_pointing()
		lats = from_degrees(np.arange(0, times.size)*4.0/times.size-2.0)
		lons = np.zeros(times.size)
		boresight_pointing = (lats, lons)
		#self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1)
		for bolo in range(0, bolos):
			detector_pointing = self.rotate_boresight_pointing(boresight_pointing, bolo)
			lat, lon = coordinates.eq_to_gal(detector_pointing[0], detector_pointing[1])
			bolo_i = healpy.get_interp_val(maps[0], pl.pi/2.0-lat, lon)
			self.plot_data(bolo, times, bolo_i)
			bolo_q = healpy.get_interp_val(maps[1], pl.pi/2.0-lat, lon)
			bolo_u = healpy.get_interp_val(maps[2], pl.pi/2.0-lat, lon)
			bolo_alpha = 1/2. * pl.arctan2(bolo_u, bolo_q)
			bolo_p = pl.sqrt(bolo_q**2 + bolo_u**2)/bolo_i
			#hwp_angle = np.sin(4 * pl.pi * coordinates.wrap_to_2pi(times))
			hwp_angle = np.sin(2*pl.pi * f_hwp * times)
			bolo_alpha_resize = np.resize(bolo_alpha, np.shape(times))
			bolo_i_resize = np.resize(bolo_i, np.shape(times))
			bolo_p_resize = np.resize(bolo_p, np.shape(times))
			data = 1/2.* (bolo_i_resize + bolo_p_resize * pl.cos(4*hwp_angle - 2*bolo_alpha_resize))
			#data = self.add_hwpss(data)
			#data = self.add_nonlinearity(data)
			#data = self.add_noise(data)
			
			
		plt.show()	
		
	def rotate_boresight_pointing(self, boresight_pointing, bolo_number):
		#this is a basic rotation function. the three bolos are arranged in a triangle with base 0.02 (~2km) and height 0.02 (~2km)
		#if a fourth bolo is added, it will be at the center of the triangle (the boresight pointing)
		#a little clunky but I can turn this into a dictionary later with diff. adjustments depending on the number/arrangement of bolos
		boresight_pointing = list(boresight_pointing)
		if bolo_number == 0:
			boresight_pointing[1] += 0.01
		elif bolo_number == 1:
			boresight_pointing[0] += 0.01
			boresight_pointing[1] -= 0.01
		elif bolo_number == 2:
			boresight_pointing[0] -= 0.01
			boresight_pointing[1] -= 0.01
		boresight_pointing = tuple(boresight_pointing)
		return boresight_pointing
	
	def unlink_wrap(self, dat, lims=[0, 2*pl.pi], thresh = 0.95):
		#this makes sure that when data wraps from 2pi to 0, it does not create horizontal streaks across the graph
		#only necessary when plotting data with lines
		jump = np.nonzero(np.abs(np.diff(dat)) > ((lims[1] - lims[0]) * thresh))[0]
		lasti = 0
		for ind in jump:
			yield slice(lasti, ind + 1)
			lasti = ind + 1
		yield slice(lasti, len(dat))
	
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
		noise = scipy.stats.norm.rvs(scale = np.std(signal), size = signal.size)
		return signal + noise
	
	def plot_data(self, bolo_num, times, data_to_plot):
		#the below is only necessary when plotting data with lines
		#lims = [0, times[-1]]
		#for slc in self.unlink_wrap(times, lims):
		#	plt.plot(times[slc], data_to_plot[slc], 'g,')
		plt.axhline(linewidth = 0.5, color = 'k')
		plt.plot(times, data_to_plot,'.', markersize = 1.5)
	
	#def make_map(self, data, detector_pointing):
		
		

if __name__ == "__main__":
	simulator = Simulator()
	simulator.run()
	#simulator.end()
