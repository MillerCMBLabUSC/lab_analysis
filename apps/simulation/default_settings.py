import numpy as np
import ephem


class SimulatorSettings:
	def __init__(self):
		#establishing scan parameters
		self.az_0 = 70 #degrees
		self.el_0 = 45 #degrees
		self.a_thr = 5 #degrees
		self.e_rng = 5 #degrees
		self.e_stp = 0.1 #degrees default was .2
		#self.dt_scn = 0.0736 #degrees/sec default was .1
		#self.dt = 0.01 #data time interval default was .01
		self.t_end = 3600.0 #seconds
		#establishing detector parameters
		self.num_bolos = 2 #number of bolometers
		#each bolo is an ephem observer, making certain calculations easier
		self.bolo1 = ephem.Observer() #this one is currently set to USC
		self.bolo1.lat = "34.019579"
		self.bolo1.lon = "-118.286926"
		
		self.bolo2 = ephem.Observer() #this one is currently set to 2km away from bolo1
		self.bolo2.lat = "34.019579"
		self.bolo2.lon = "-118.27"
		
		
		
		
