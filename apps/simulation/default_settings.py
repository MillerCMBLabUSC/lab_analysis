import numpy as np
import ephem
import datetime

class SimulatorSettings:
	'''
	Class: SimulatorSettings
	
	Purpose: to house the various settings/parameters needed for simulation
	
	Attributes: too many to list, see code below.
	
	Notes:
	-> inputs are given in terms of azimuth/elevation angle (az/el) and are later 
		converted to right ascension/declination (ra/dec)
	-> the location and properties of our mock telescope are accessed using an 
		ephem Observer object. Ephem Observers store location/elevation/datetime/etc
		info and can perform calculations/conversions, so they come in handy here
	-> the noise equivalent temperature (NET) was taken from POLARBEAR
	
	'''
	def __init__(self):
		#telescope location parameters
		self.telescope = ephem.Observer()
		self.telescope.lon = -67.7875   #degrees
		self.telescope.lat = -22.9586   #degrees
		self.telescope.elevation = 5190  #meters
		self.obs_date = ephem.Date('2018')
		self.telescope.date = self.obs_date.datetime()
		
		#input parameters for scan
		self.az_0 = 0.
		self.el_0 = 90.
		self.az_rng = 0.5 
		self.el_rng = 0.5
		self.el_stp = 0.01 
		self.dt = 0.01 #data time interval
		self.f_data = 1./self.dt 
		self.t_end = 3600.0 #seconds
		
		#NET and noise settings
		self.NET = 480e-6 #K*sqrt(s) This is the NET value from POLARBEAR
		self.add_white_noise = False
		self.add_1f_noise = False	
		
		#HWP and HWPSS settings
		self.f_hwp = 2 #Hz
		self.num_bolos = 1
		
		#operational settings
		self.conduct_test = False
		
		#map settings
		map_dict = {'commander':'/home/rashmi/maps/planck_commander_1024_full_test.fits',
				'nilc':'/home/rashmi/maps/planck_nilc_1024_full_test.fits',
				'sevem':'/home/rashmi/maps/planck_sevem_1024_full_test.fits',
				'smica':'/home/rashmi/maps/planck_smica_1024_full_test.fits'}
		self.map_name = 'commander'  #can change this to any of the four keys in the map_dict
		self.map_filename = map_dict.get(self.map_name)


