import numpy as np
from lab_analysis.apps.simulation import default_settings
np.set_printoptions(edgeitems = 50)

class CreatePointing(default_settings.SimulatorSettings):
	def make_boresight_pointing(self):
		self.scan_setup()
		self.scan_seq()
		return np.resize(self.ra_data, int(self.num_data_points)), np.resize(self.dec_data, int(self.num_data_points))
		
	def scan_setup(self):
		#defining a few useful values
		self.n_stp = int(self.dec_rng/self.dec_stp) + 1 #number of steps
		l = self.ra_rng*(self.n_stp) + self.dec_rng*2 #total length of path of scan
		self.num_data_points = self.t_end/self.dt
		self.dt_obs = float(l)/self.num_data_points 
		#print self.dt_obs
		#print self.num_data_points
		self.ra_min = self.ra_0 - (self.ra_rng/2) #min ra
		self.ra_max = self.ra_0 + (self.ra_rng/2) #max ra
		self.dec_min = self.dec_0 - (self.dec_rng/2) #min dec
		self.dec_max = self.dec_0 + (self.dec_rng/2) #max dec
	
	def scan_seq(self):
		#scan sequence
		#first step of the scan: declaring and initializing data arrays
		self.ra_data = np.linspace(self.ra_min, self.ra_max, abs(self.ra_max - self.ra_min)/self.dt_obs)
		self.dec_data = np.repeat(self.dec_min, abs(self.ra_max - self.ra_min)/self.dt_obs)
		self.ra_data = np.append(self.ra_data, np.repeat(self.ra_max, self.dec_stp/self.dt_obs))
		self.dec_data = np.append(self.dec_data, np.linspace(self.dec_min, self.dec_min + self.dec_stp, self.dec_stp/self.dt_obs))
		flag = 1 #flag helps to establish zig zag pattern
		i = 0 #counter for below while loop
		while self.ra_data.size < self.num_data_points:
			if flag == 1:
				i += 1
				self.ra_data = np.append(self.ra_data, np.linspace(self.ra_max, self.ra_min, abs(self.ra_max - self.ra_min)/self.dt_obs))
				self.dec_data = np.append(self.dec_data, np.repeat(self.dec_min + i*self.dec_stp, abs(self.ra_max - self.ra_min)/self.dt_obs))
				#print self.ra_data.size
				self.ra_data = np.append(self.ra_data, np.repeat(self.ra_min, self.dec_stp/self.dt_obs))
				self.dec_data = np.append(self.dec_data, np.linspace(self.dec_min + i*self.dec_stp, self.dec_min + (i+1)*self.dec_stp, self.dec_stp/self.dt_obs))
				#print self.ra_data.size
				flag = 0
				continue
		
			else:
				i += 1
				self.ra_data = np.append(self.ra_data, np.linspace(self.ra_min, self.ra_max, abs(self.ra_max - self.ra_min)/self.dt_obs))
				self.dec_data = np.append(self.dec_data, np.repeat(self.dec_min + i*self.dec_stp, abs(self.ra_max - self.ra_min)/self.dt_obs))
				#print self.ra_data.size
				self.ra_data = np.append(self.ra_data, np.repeat(self.ra_max, self.dec_stp/self.dt_obs))
				self.dec_data = np.append(self.dec_data, np.linspace(self.dec_min + i*self.dec_stp, self.dec_min + (i+1)*self.dec_stp, self.dec_stp/self.dt_obs))
				#print self.ra_data.size
				flag = 1
				continue

		#print self.ra_data.size, self.dec_data.size
		return self.ra_data, self.dec_data
