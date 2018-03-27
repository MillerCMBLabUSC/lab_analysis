import numpy as np
import ephem
import datetime

class SimulatorSettings:
	def __init__(self):
		#telescope location parameters
		self.telescope = ephem.Observer()
		self.telescope.lon = -67.7875   #degrees
		self.telescope.lat = -22.9586   #degrees
		self.telescope.elevation = 5190  #meters
		self.obs_date = ephem.Date('2018')
		self.telescope.date = self.obs_date.datetime()
		
		#scan and simulation parameters
		#self.az_0 = 216.28
		#self.el_0 = -27.0
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
		
		#HWP and HWPSS settings
		self.f_hwp = 2 #Hz
		self.num_bolos = 1
		
		#operational settings
		self.conduct_test = True 
