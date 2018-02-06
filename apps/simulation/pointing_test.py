import ephem
import datetime
import numpy as np
from lab_analysis.apps.simulation import default_settings
from lab_analysis.apps.simulation import datetimes
from lab_analysis.libs.geometry import coordinates

np.set_printoptions(edgeitems = 50)

class CreatePointing(default_settings.SimulatorSettings):
	def make_boresight_pointing(self):
		self.scan_setup()
		self.scan_seq()
		return np.resize(self.ra_data, int(self.num_data_points)), np.resize(self.dec_data, int(self.num_data_points))
		
	def scan_setup(self):
		#defining a few useful values
		self.n_stp = int(self.el_rng/self.el_stp) + 1 #number of steps
		l = self.az_rng*(self.n_stp) + self.el_rng*2 #total length of path of scan
		self.num_data_points = self.t_end/self.dt
		self.dt_obs = float(l)/self.num_data_points 
		self.datetimes = datetimes.generate_datetimes()
		#print self.dt_obs
		#print self.num_data_points
		self.az_min = self.az_0 - (self.az_rng/2) #min az
		self.az_max = self.az_0 + (self.az_rng/2) #max az
		self.el_min = self.el_0 - (self.el_rng/2) #min el
		self.el_max = self.el_0 + (self.el_rng/2) #max el
		
	
	def scan_seq(self):
		#scan sequence
		#first step of the scan: declaring and initializing data arrays
		self.ra_data = np.empty(0)
		ra_min, dec_min, ra_max, dec_max, dec_step = self.transform_coords()
		self.ra_data = np.linspace(self.ra_min, self.ra_max, abs(self.ra_max - self.ra_min)/self.dt_obs)
		self.dec_data = np.repeat(self.dec_min, abs(self.ra_max - self.ra_min)/self.dt_obs)
		ra_min, dec_min, ra_max, dec_max, dec_step = self.transform_coords()
		self.ra_data = np.append(self.ra_data, np.repeat(self.ra_max, self.dec_step/self.dt_obs))
		self.dec_data = np.append(self.dec_data, np.linspace(self.dec_min, self.dec_min + self.dec_step, self.dec_step/self.dt_obs))
		flag = 1 #flag helps to establish zig zag pattern
		i = 0 #counter for below while loop
		while self.ra_data.size < self.num_data_points:
			if flag == 1:
				i += 1
				ra_min, dec_min, ra_max, dec_max, dec_step = self.transform_coords()
				self.ra_data = np.append(self.ra_data, np.linspace(self.ra_max, self.ra_min, abs(self.ra_max - self.ra_min)/self.dt_obs))
				self.dec_data = np.append(self.dec_data, np.repeat(self.dec_min + i*self.dec_step, abs(self.ra_max - self.ra_min)/self.dt_obs))
				#print self.ra_data.size
				ra_min, dec_min, ra_max, dec_max, dec_step = self.transform_coords()
				self.ra_data = np.append(self.ra_data, np.repeat(self.ra_min, self.dec_step/self.dt_obs))
				self.dec_data = np.append(self.dec_data, np.linspace(self.dec_min + i*self.dec_step, self.dec_min + (i+1)*self.dec_step, self.dec_step/self.dt_obs))
				#print self.ra_data.size
				flag = 0
				continue
		
			else:
				i += 1
				ra_min, dec_min, ra_max, dec_max, dec_step = self.transform_coords()
				self.ra_data = np.append(self.ra_data, np.linspace(self.ra_min, self.ra_max, abs(self.ra_max - self.ra_min)/self.dt_obs))
				self.dec_data = np.append(self.dec_data, np.repeat(self.dec_min + i*self.dec_step, abs(self.ra_max - self.ra_min)/self.dt_obs))
				#print self.ra_data.size
				ra_min, dec_min, ra_max, dec_max, dec_step = self.transform_coords()
				self.ra_data = np.append(self.ra_data, np.repeat(self.ra_max, self.dec_step/self.dt_obs))
				self.dec_data = np.append(self.dec_data, np.linspace(self.dec_min + i*self.dec_step, self.dec_min + (i+1)*self.dec_step, self.dec_step/self.dt_obs))
				#print self.ra_data.size
				flag = 1
				continue

		#print self.ra_data.size, self.dec_data.size
		return self.ra_data, self.dec_data


	def transform_coords(self):
		datetime_index = np.floor(self.ra_data.size * self.dt_obs)
		self.telescope.date = self.datetimes[int(datetime_index)]
		ra_min, dec_min = coordinates.hor_to_eq(self.az_min, self.el_min, float(self.telescope.lat), self.telescope.sidereal_time())
		ra_max, dec_max = coordinates.hor_to_eq(self.az_max, self.el_max, float(self.telescope.lat), self.telescope.sidereal_time())
		ra, dec_step = coordinates.hor_to_eq(self.az_min, self.el_min + self.el_stp, float(self.telescope.lat), self.telescope.sidereal_time())
		return ra_min, dec_min, ra_max, dec_max, dec_step


if __name__ == "__main__":
	pointing = CreatePointing()
	pointing.scan_seq


