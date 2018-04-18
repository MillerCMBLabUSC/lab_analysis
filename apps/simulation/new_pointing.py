import ephem
import datetime
import numpy as np
import matplotlib.pyplot as plt

from lab_analysis.apps.simulation import default_settings
from lab_analysis.apps.simulation import datetimes
from lab_analysis.libs.geometry import coordinates

np.set_printoptions(edgeitems = 50)

class CreatePointing(default_settings.SimulatorSettings):
	'''
	Class: CreatePointing
	
	Purpose: set of functions to generate a set up a scan strategy and generate a list of coordinates
	
	Attributes: inheriting from SimulatorSettings class from default_settings file
	
	'''
	
	def make_boresight_pointing(self):
		'''
		Function: make_boresight_pointing
		
		Purpose: creates a pointing scheme and generates an array of coordinates. The simulation code
			calls this function to generate pointing.
		
		Inputs: none
		
		Outputs:
		-> ra_data (float): array of right ascension (ra) coordinates
		-> dec_data (float): array of declination (dec) coordinates
		-> horiz_roll (float): array of horizontal roll values
		
		'''
		
		self.scan_setup()
		self.scan_sequence()
		return self.ra_data, self.dec_data, self.horiz_roll

	def scan_setup(self):
		'''
		Function: scan_setup
		
		Purpose: defining some useful values based on the inputs from default_settings file.
			eg: number of steps, number of data points, azimuth/elevation mins/maxs, etc.
			Also generates an array of datetimes 
		
		Inputs: none
		
		Outputs: none
		
		'''
		
		self.n_stp = int(self.el_rng/self.el_stp) + 1 #number of steps
		l = self.az_rng*(self.n_stp) + self.el_rng*2 #total length of path of scan
		self.num_data_points = float(l)/self.dt  #defining number of data points
		#print self.num_data_points
		self.datetimes = datetimes.generate_datetimes() #generating array of datetimes to use for conversion
		#establishing boundary of scan
		self.az_min = self.az_0 - (self.az_rng/2) #min az
		self.az_max = self.az_0 + (self.az_rng/2) #max az
		self.el_min = self.el_0 - (self.el_rng/2) #min el
		self.el_max = self.el_0 + (self.el_rng/2) #max el
	
	def scan_sequence(self):
		'''
		Function: scan_sequence
		
		Purpose: generates the array of coordinates according to the scan strategy. In this case, it is a
			zig-zag pattern with incremental steps in elevation.
		
		'''
		
		self.horiz_roll = np.zeros(int(self.num_data_points)) #setting horizontal roll to zero
		#first step of scan; initializing data arrays
		self.ra_data = np.zeros(0)
		self.dec_data = np.zeros(0)
		self.az_data = np.zeros(0)
		self.el_data = np.zeros(0)
		#starting out at az_min, el_min
		current_az = self.az_min
		current_el = self.el_min
		self.az_data = np.append(self.az_data, current_az)
		self.el_data = np.append(self.el_data, current_el)
		current_ra, current_dec = self.transform_coords(current_az, current_el)
		self.ra_data = np.append(self.ra_data, current_ra)
		self.dec_data = np.append(self.dec_data, current_dec)
		j = 0 #parameter to keep track of elevation increments
		flag = 0 #parameter to establish zigzag pattern
		for i in range (1, int(self.num_data_points)): #starts from 1 because we already did 1st step of scan
                        if flag == 0:
                                if current_az < self.az_max:
                                        #current_az moves from az_min to az_max while el stays the same
                                        current_az += self.az_rng * self.dt
                                        current_el = self.el_min + j * self.el_stp
					self.az_data = np.append(self.az_data, current_az)
					self.el_data = np.append(self.el_data, current_el)
                                        current_ra, current_dec = self.transform_coords(current_az, current_el)
                                        self.ra_data = np.append(self.ra_data, current_ra)
                                        self.dec_data = np.append(self.dec_data, current_dec)
                                elif current_az >= self.az_max:
                                        #once current_az reaches az_max, it stays there while el increases
                                        current_el += self.el_stp * self.dt
					self.az_data = np.append(self.az_data, current_az)
					self.el_data = np.append(self.el_data, current_el)
                                        current_ra, current_dec = self.transform_coords(current_az, current_el)
                                        self.ra_data = np.append(self.ra_data, current_ra)
                                        self.dec_data = np.append(self.dec_data, current_dec)
                                        if current_el >= self.el_min + (j+1) * self.el_stp:
                                        #if current_el is done incrementing, increase step# and switch flag
                                                j += 1
                                                flag = 1
			
			elif flag == 1:
				if current_az > self.az_min:
					#current_az moves from az_max to az_min while el stays the same
					current_az -= self.az_rng * self.dt
					current_el = self.el_min + j * self.el_stp
					self.az_data = np.append(self.az_data, current_az)
					self.el_data = np.append(self.el_data, current_el)
					current_ra, current_dec = self.transform_coords(current_az, current_el)
					self.ra_data = np.append(self.ra_data, current_ra)
					self.dec_data = np.append(self.dec_data, current_dec)
				elif current_az <= self.az_min:
					#once current_az reaches az_min, it stays there while el increases
					current_el += self.el_stp * self.dt
					self.az_data = np.append(self.az_data, current_az)
					self.el_data = np.append(self.el_data, current_el)
					current_ra, current_dec = self.transform_coords(current_az, current_el)
					self.ra_data = np.append(self.ra_data, current_ra)
					self.dec_data = np.append(self.dec_data, current_dec)
					if current_el >= self.el_min + (j+1) * self.el_stp:
					#if current_el is done incrementing, increase step# and switch flag
						j += 1
						flag = 0


	def transform_coords(self, az, el):
		datetime_index = np.floor(self.ra_data.size * self.dt)
                self.telescope.date = self.datetimes[int(datetime_index)]
                ra, dec = coordinates.hor_to_eq(az, el, float(self.telescope.lat), self.telescope.sidereal_time())
		return ra, dec

if __name__ == "__main__":
	pointing = CreatePointing()
	ra, dec, roll = pointing.make_boresight_pointing()
	plt.plot(ra, dec, '.', markersize = 1.5)
	plt.show()

