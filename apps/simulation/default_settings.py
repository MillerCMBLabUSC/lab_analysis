import numpy as np


class SimulatorSettings:
	def __init__(self):
		#scan and simulation parameters
		self.ra_0 = 4.91
		self.dec_0 = 52.26 
		self.ra_rng = 5 
		self.dec_rng = 5 
		self.dec_stp = 0.1 
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
