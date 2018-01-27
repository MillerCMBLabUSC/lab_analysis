import numpy as np
import ephem
import datetime

class SimulatorSettings:
	def __init__(self):
		#telescope location parameters
		telescope = ephem.Observer()
		telescope.lon = -67.7875   #degrees
		telescope.lat = -22.9586   #degrees
		telescope.altitude = 5190  #meters
		obs_date = ephem.Date('2018')
		telescope.date = obs_date.datetime()
		
		#scan and simulation parameters
		self.az_0 = 0
		self.el_0 = 90 
		self.az_rng = 1 
		self.el_rng = 1 
		self.el_stp = 0.02 
		self.dt = 0.1 #data time interval 
		self.t_end = 3600.0 #seconds
		
		#NET and noise settings
		self.NET_from_POLARBEAR1 = 480e-6 #K*sqrt(s)
		self.NET_from_POLARBEAR2 = 4.1e-6 #K*sqrt(s)
		self.NET_from_ACT = 6e-6 #K*sqrt(s)
		self.NET_dict = {'POLARBEAR1': self.NET_from_POLARBEAR1,
				'POLARBEAR2': self.NET_from_POLARBEAR2,
				'ACT': self.NET_from_ACT}  #can add more NET values to dict
		
		self.NET_from = 'POLARBEAR1' #can change to 'POLARBEAR' 'ACT' etc.
		#only using POLARBEAR1 value for now; the other two are for entire array. NET per detector needed.
		self.NET = self.NET_dict.get(self.NET_from)
		
		#HWP and HWPSS settings
		self.f_hwp = 2 #Hz
		self.num_bolos = 1 
