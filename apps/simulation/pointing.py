import numpy as np
import matplotlib.pyplot as plt
import ephem
from lab_analysis.apps.simulation import default_settings
from lab_analysis.libs.geometry import coordinates as crd
from datetime import datetime
np.set_printoptions(edgeitems = 50)

class CreatePointing(default_settings.SimulatorSettings):
	def make_boresight_pointing(self):
		self.scan_setup()
		self.scan_seq()
		return self.ra_data, self.dec_data
		
	def scan_setup(self):
		#defining a few useful values
		self.n_stp = int(self.dec_rng/self.dec_stp) + 1 #number of steps
		l = self.ra_rng*(self.n_stp) + self.dec_rng*2 #total length of path of scan
		self.dt = float(l)/self.t_end #total scan time
		#print self.dt
		#print l
		self.ra_min = self.ra_0 - (self.ra_rng/2) #min az
		self.ra_max = self.ra_0 + (self.ra_rng/2) #max az
		self.dec_min = self.dec_0 - (self.dec_rng/2) #min el
		self.dec_max = self.dec_0 + (self.dec_rng/2) #max el
	
	def scan_seq(self):
		#scan sequence
		flag = 0 #flag helps to establish zig zag pattern
		for i in range (0, self.n_stp):
			if i == 0:
			#first step of the scan: declaring and initializing data arrays
				self.ra_data = np.linspace(self.ra_min, self.ra_max, abs(self.ra_max - self.ra_min)/self.dt)
				self.dec_data = np.repeat(self.dec_min, abs(self.ra_max - self.ra_min)/self.dt)
				self.ra_data = np.append(self.ra_data, np.repeat(self.ra_max, self.dec_stp/self.dt))
				self.dec_data = np.append(self.dec_data, np.linspace(self.dec_min, self.dec_min + self.dec_stp, self.dec_stp/self.dt))
				flag = 1
				continue
			
			if flag == 1:
				self.ra_data = np.append(self.ra_data, np.linspace(self.ra_max, self.ra_min, abs(self.ra_max - self.ra_min)/self.dt))
				self.dec_data = np.append(self.dec_data, np.repeat(self.dec_min + i*self.dec_stp, abs(self.ra_max - self.ra_min)/self.dt))				
				if (self.dec_min + (i+1)*self.dec_stp) > self.dec_max:
				#stops if this step will exceed dec_max
					break
				else:           
					self.ra_data = np.append(self.ra_data, np.repeat(self.ra_min, self.dec_stp/self.dt))
					self.dec_data = np.append(self.dec_data, np.linspace(self.dec_min + i*self.dec_stp, self.dec_min + (i+1)*self.dec_stp, self.dec_stp/self.dt))
					flag = 0
					continue
			
			else:
				self.ra_data = np.append(self.ra_data, np.linspace(self.ra_min, self.ra_max, abs(self.ra_max - self.ra_min)/self.dt))
				self.dec_data = np.append(self.dec_data, np.repeat(self.dec_min + i*self.dec_stp, abs(self.ra_max - self.ra_min)/self.dt))
				if (self.dec_min + (i+1)*self.dec_stp) > self.dec_max:
				#stops if this step will exceed dec_max
					break
				else:
					self.ra_data = np.append(self.ra_data, np.repeat(self.ra_max, self.dec_stp/self.dt))
					self.dec_data = np.append(self.dec_data, np.linspace(self.dec_min + i*self.dec_stp, self.dec_min + (i+1)*self.dec_stp, self.dec_stp/self.dt))
					flag = 1
					continue
		
		return self.ra_data, self.dec_data
