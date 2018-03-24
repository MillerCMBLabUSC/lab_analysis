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
from lab_analysis.apps.simulation import new_pointing
from lab_analysis.libs.units.angles import *
#from lab_analysis.libs.noise import simulate


#class Simulator(lab_app.App):
class Simulator(object):
		
	def run(self):
		self.settings = default_settings.SimulatorSettings()
		self.create_pointing = new_pointing.CreatePointing()
		self.num_data_pts = 2650
		times = np.linspace(0., self.settings.t_end, num = self.num_data_pts)
		if self.settings.conduct_test:
		#if I want to conduct a test and scan the galactic center, I would generate a test
		#pointing, write coordinates and times to file, and annotate the graph with relevant
		#values. Otherwise, I would proceed as usual.
			boresight_pointing = self.use_test_pointing(times)
			self.write_coords_to_file(times, boresight_pointing)
		if not self.settings.conduct_test:
		#if I'm not conducting a test, I am proceeding with the usual scan strategy
			boresight_pointing = self.create_pointing.make_boresight_pointing()
			times = np.linspace(0., self.settings.t_end, num = int(self.create_pointing.num_data_points))
		self.map_name = 'sevem_1024_full'
		maps = healpy.read_map(self.load_map(self.map_name), field = (0, 1, 2))
		for bolo in range(0, self.settings.num_bolos):
			self.run_one_bolo(bolo, boresight_pointing, maps, times)
		plt.show()
	
	def run_one_bolo(self, bolo, boresight_pointing, maps, times):
		detector_pointing = self.rotate_boresight_pointing(boresight_pointing, bolo)
		lat, lon = coordinates.eq_to_gal(detector_pointing[0], detector_pointing[1])
		bolo_i = healpy.get_interp_val(maps[0], pl.pi/2.0-lat, lon)
		bolo_i_test = healpy.get_interp_val(maps[0], lat, lon)
		bolo_q = healpy.get_interp_val(maps[1], pl.pi/2.0-lat, lon)
		bolo_u = healpy.get_interp_val(maps[2], pl.pi/2.0-lat, lon)
		bolo_alpha = 1/2. * pl.arctan2(bolo_u, bolo_q)
		bolo_p = pl.sqrt(bolo_q**2 + bolo_u**2)/bolo_i
		#hwp_angle = np.sin(2*pl.pi * self.settings.f_hwp * self.hwp_angles)
		#hwp_angle = 2*pl.pi * self.settings.f_hwp * self.hwp_rotation()
		data = 1/2.* (bolo_i + bolo_p * pl.cos(4*self.hwp_rotation() - 2*bolo_alpha))
		#data = self.add_hwpss(times, data, self.hwp_rotation())
		#data = self.add_nonlinearity(data)
		#data = self.add_noise(data)
		self.plot_data(times, bolo_i_test)
		#self.make_map(data, detector_pointing, lat, lon)
		
	
	def rotate_boresight_pointing(self, boresight_pointing, bolo_number):
		'''
		#this is a basic rotation function. the three bolos are arranged in a triangle with base 0.005 (~50m) & height 0.005 (~50m)
		#if a fourth bolo is added, it will be at the center of the triangle (the boresight pointing)
		#a little clunky but I can turn this into a dict later with diff. adjustments depending on the number/arrangement of bolos
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
		'''
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
	'''
		
	def add_noise(self, signal, alpha = 1.0, f_knee = 0.1, add_white_noise = False, add_1f_noise = False):
		#still need to determine what "frequencies" parameter is!!
		if add_white_noise:
			white_noise_sigma = self.settings.NET / pl.sqrt(self.settings.dt)
			white_noise = simulate.simulate_noise(alpha, white_noise_sigma, signal.size, f_knee, self.settings.dt)
		else:
			white_noise = np.zeros
		
		if add_1f_noise:
			1f_noise = one_over_f(frequencies, alpha, f_knee)
		else:
			1f_noise = np.zeros
		
		return signal + white_noise + 1f_noise
	
	'''

	def hwp_rotation(self):
		period_length = self.settings.f_data/self.settings.f_hwp
		period = np.linspace(0., 2*pl.pi, num = period_length)
		hwp_angle_array = np.resize(period, int(self.num_data_pts))
		return coordinates.wrap_to_2pi(hwp_angle_array)
	
	def add_hwpss(self, times, signal, hwp_angle):
		#approximation we are using for now: A1 = 50mK, A2 = 100, A4 = 200. All other coeffs = 0.
		hwpss = 0.05*pl.cos(hwp_angle) + 0.1*pl.cos(2*hwp_angle) + 0.2*pl.cos(4*hwp_angle)
		return signal + hwpss
	
	def plot_data(self, times, data_to_plot):
		plt.axhline(linewidth = 0.5, color = 'k')
		plt.plot(times, data_to_plot, markersize = 1.5)
		#plt.plot(times, data_to_plot,'.', markersize = 1.5)
		if self.settings.conduct_test:
			self.print_local_min_max(data_to_plot, 0.00000001, x = times)
		plt.xlabel('Time (s)')
		plt.ylabel('K_cmb')
		plt.title(self.map_name)
	
	def make_map(self, data, detector_pointing, lat, lon):
		detector_pointing = list(detector_pointing)
		nside = 1024
		npix = healpy.nside2npix(nside)
		indices = healpy.ang2pix(nside, lon, lat, lonlat = True)
		hpmap = np.zeros(npix, dtype = np.float)
		hpmap[indices] += data[indices]
		healpy.mollview(hpmap)
		
	def write_coords_to_file(self, times, coords):
	#this is only relevant if I am conducting a test and want to make a list of times and coordinates
	#so I can compare to the Healpy map values via mollzoom
		lats = list(coords[0])
		lons = list(coords[1])
		with open('/home/rashmi/maps/coords.txt', 'w') as f:
			f.write('times\tlat\tlon\n')
			for i in np.arange(len(times)):
				f.write('\n{}\t{:.3e}\t{:.3e}'.format(times[i], lats[i], lons[i]))
	
	def use_test_pointing(self, times):
	#this is only relevant if I am conducting a test and only want to scan the galactic center
	#in order to compare to the Healpy map values via mollzoom
		lats = from_degrees(np.arange(0, times.size)*4.0/times.size-2.0)
		lons = np.zeros(times.size)
		test_pointing = lats, lons
		return test_pointing
	
	def print_local_min_max(self, v, delta, x = None):
	#this is only relevant if I am conducting a test and want to print the local minima and 
	#maxima on the chart to compare to the Healpy map values via mollzoom
		import sys
		np.set_printoptions(precision = 4)
		#maxtab = []
    		#mintab = []
		mxpos_tab = []
		mnpos_tab = []
		mx_tab = []
		mn_tab = []
		if x is None:
			x = np.arange(len(v))
			v = np.asarray(v)
		
		if len(v) != len(x):
			sys.exit('Input vectors v and x must have same length')
		
		if not np.isscalar(delta):
			sys.exit('Input argument delta must be a scalar')
		
		if delta <= 0:
			sys.exit('Input argument delta must be positive')
		
		mn, mx = np.Inf, -np.Inf
		mnpos, mxpos = np.NaN, np.NaN
		
		lookformax = True
		
		for i in np.arange(len(v)):
			this = v[i]
			if this > mx:
				mx = this
				mxpos = x[i]
			if this < mn:
				mn = this
				mnpos = x[i]

			if lookformax:
				if this < mx-delta:
					#maxtab = np.column_stack((mxpos, mx))
					mxpos_tab = np.append(mxpos_tab, mxpos)
					mx_tab = np.append(mx_tab, mx)
					mn = this
					mnpos = x[i]
					lookformax = False
			else:
				if this > mn+delta:
					#mintab = np.column_stack((mnpos, mn))
					mnpos_tab = np.append(mnpos_tab, mnpos)
					mn_tab = np.append(mn_tab, mn)
					mx = this
					mxpos = x[i]
					lookformax = True
		
		#plt.scatter(np.array(maxtab)[:,0], np.array(maxtab)[:,1], color='blue')
		#plt.scatter(np.array(mintab)[:,0], np.array(mintab)[:,1], color='red')
		plt.scatter(mxpos_tab, mx_tab, color='blue')
		plt.scatter(mnpos_tab, mn_tab, color='red')
		for i in np.arange(len(mx_tab)-1):
			plt.annotate('({:.3f}, {:.3e})'.format(mxpos_tab[i], mx_tab[i]), xy = (mxpos_tab[i], mx_tab[i]), \
				xytext = (mxpos_tab[i], mx_tab[i] + 0.000005))
			plt.annotate('({:.3f}, {:.3e})'.format(mnpos_tab[i], mn_tab[i]), xy = (mnpos_tab[i], mn_tab[i]), \
				xytext = (mnpos_tab[i], mn_tab[i] - 0.00001))
		

if __name__ == "__main__":
	simulator = Simulator()
	simulator.run()
	#simulator.end()
