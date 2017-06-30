import numpy as np
import ephem


class SimulatorSettings:
	def __init__(self):
		#establishing scan parameters
		self.az_0 = 25 #degrees
		self.el_0 = 45 #degrees
		self.a_thr = 5 #degrees
		self.e_rng = 5 #degrees
		self.e_stp = .2 #degrees
		self.dt_scn = .1 #degrees/sec
		self.dt = 0.01 #data time interval
		
		#default observer location is at USC
		self.default_loc = ephem.Observer()
		self.default_loc.lon = "-118.286926"
		self.default_loc.lat = "34.019579"
		
