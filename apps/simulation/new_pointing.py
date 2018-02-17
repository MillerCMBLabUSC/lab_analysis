import ephem
import datetime
import numpy as np
import matplotlib.pyplot as plt
from lab_analysis.apps.simulation import default_settings
from lab_analysis.apps.simulation import datetimes
from lab_analysis.libs.geometry import coordinates

np.set_printoptions(edgeitems = 50)

class CreatePointing(default_settings.SimulatorSettings):
	def make_boresight_pointing(self):
		self.scan_setup()
		self.scan_sequence()
		return self.ra_data, self.dec_data, self.horiz_roll

	def scan_setup(self):
		#defining a few useful values
		self.n_stp = int(self.el_rng/self.el_stp) + 1 #number of steps
		l = self.az_rng*(self.n_stp) + self.el_rng*2 #total length of path of scan
		self.num_data_points = float(l)/self.dt
		#self.num_data_points = self.t_end/self.dt
		#self.dt_obs = float(l)/self.num_data_points 
		self.datetimes = datetimes.generate_datetimes()
		#print self.dt_obs
		#print self.num_data_points
		self.az_min = self.az_0 - (self.az_rng/2) #min az
		self.az_max = self.az_0 + (self.az_rng/2) #max az
		self.el_min = self.el_0 - (self.el_rng/2) #min el
		self.el_max = self.el_0 + (self.el_rng/2) #max el
	
	def scan_sequence(self):
		self.horiz_roll = np.zeros(int(self.num_data_points))
		self.ra_data = np.zeros(1)
		self.dec_data = np.zeros(1)
		current_az = self.az_min
		current_el = self.el_min
		self.ra_data[0], self.dec_data[0] = self.transform_coords(current_az, current_el)
		j = 0
		while self.ra_data.size < self.num_data_points:
			for i in range (1, self.num_data_points):
				if flag == 0:
					if current_az != self.az_max:
						current_az += self.az_rng * self.dt
						current_el = self.el_min + j * self.el_stp
						self.ra_data[i], self.dec_data[i] = self.transform_coords(current_az, current_el)
					elif current_az == self.az_max:
						current_el += self.el_stp * self.dt
						self.ra_data[i], self.dec_data[i] = self.transform_coords(current_az, current_el)
						if current_el == self.el_min + (j+1) * self.el_stp:
							j += 1
							flag = 1
				
				elif flag == 1:
					if current_az != self.az_min:
						current_az -= self.az_rng * self.dt
						current_el = self.el_min + j * self.el_stp
						self.ra_data[i], self.dec_data[i] = self.transform_coords(current_az, current_el)
					elif current_az == self.az_min:
						current_el += self.el_stp * self.dt
						self.ra_data[i], self.dec_data[i] = self.transform_coords(current_az, current_el)
						if current_el == self.el_min + (j+1) * self.el_stp:
							j += 1
							flag = 0
	
	def transform_coords(self, az, el):
		datetime_index = np.floor(self.ra_data.size * self.dt)
                self.telescope.date = self.datetimes[int(datetime_index)]
                ra, dec = coordinates.hor_to_eq(az, el, float(self.telescope.lat), self.telescope.sidereal_time())
	

if __name__ == "__main__":
	pointing = CreatePointing()
	ra, dec, roll = pointing.make_boresight_pointing()
	plt.plot(ra, dec, '.', markersize = 1.5)
	plt.show()

