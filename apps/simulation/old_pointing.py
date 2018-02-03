import ephem
import datetime
import numpy as np
from lab_analysis.apps.simulation import default_settings
from lab_analysis.apps.simulation import datetimes
np.set_printoptions(edgeitems = 50)

class CreatePointing(default_settings.SimulatorSettings):
	def make_boresight_pointing(self):
		self.scan_setup()
		self.scan_seq()
		return np.resize(self.az_data, int(self.num_data_points)), np.resize(self.el_data, int(self.num_data_points))
		
	def scan_setup(self):
		#defining a few useful values
		self.n_stp = int(self.el_rng/self.el_stp) + 1 #number of steps
		l = self.az_rng*(self.n_stp) + self.el_rng*2 #total length of path of scan
		self.num_data_points = self.t_end/self.dt
		self.dt_obs = float(l)/self.num_data_points 
		#print self.dt_obs
		#print self.num_data_points
		self.az_min = self.ra_0 - (self.ra_rng/2) #min ra
		self.az_max = self.ra_0 + (self.ra_rng/2) #max ra
		self.el_min = self.dec_0 - (self.dec_rng/2) #min dec
		self.dec_max = self.dec_0 + (self.dec_rng/2) #max dec
	
	def scan_seq(self):
		#scan sequence
		#first step of the scan: declaring and initializing data arrays
		self.az_data = np.linspace(self.az_min, self.az_max, abs(self.az_max - self.az_min)/self.dt_obs)
		self.el_data = np.repeat(self.el_min, abs(self.az_max - self.az_min)/self.dt_obs)
		self.az_data = np.append(self.az_data, np.repeat(self.az_max, self.el_stp/self.dt_obs))
		self.el_data = np.append(self.el_data, np.linspace(self.el_min, self.el_min + self.el_stp, self.el_stp/self.dt_obs))
		flag = 1 #flag helps to establish zig zag pattern
		i = 0 #counter for below while loop
		while self.az_data.size < self.num_data_points:
			if flag == 1:
				i += 1
				self.az_data = np.append(self.az_data, np.linspace(self.az_max, self.az_min, abs(self.az_max - self.az_min)/self.dt_obs))
				self.el_data = np.append(self.el_data, np.repeat(self.el_min + i*self.el_stp, abs(self.az_max - self.az_min)/self.dt_obs))
				#print self.az_data.size
				self.az_data = np.append(self.az_data, np.repeat(self.az_min, self.el_stp/self.dt_obs))
				self.el_data = np.append(self.el_data, np.linspace(self.el_min + i*self.el_stp, self.el_min + (i+1)*self.el_stp, self.el_stp/self.dt_obs))
				#print self.az_data.size
				flag = 0
				continue
		
			else:
				i += 1
				self.az_data = np.append(self.az_data, np.linspace(self.az_min, self.az_max, abs(self.az_max - self.az_min)/self.dt_obs))
				self.el_data = np.append(self.el_data, np.repeat(self.el_min + i*self.el_stp, abs(self.az_max - self.az_min)/self.dt_obs))
				#print self.az_data.size
				self.az_data = np.append(self.az_data, np.repeat(self.az_max, self.el_stp/self.dt_obs))
				self.el_data = np.append(self.el_data, np.linspace(self.el_min + i*self.el_stp, self.el_min + (i+1)*self.el_stp, self.el_stp/self.dt_obs))
				#print self.az_data.size
				flag = 1
				continue

		#print self.az_data.size, self.el_data.size
		return self.az_data, self.el_data
