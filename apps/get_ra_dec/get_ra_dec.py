import numpy as np
import matplotlib.pyplot as plt
import ephem
from lab_analysis.apps.get_ra_dec import default_settings
from lab_analysis.libs.geometry import coordinates as crd
from datetime import datetime
np.set_printoptions(edgeitems = 50)

#loading scan parameters into a ScanParameters class
class ScanParameters(default_settings.SimulatorSettings):
	def run_scan(self, **kwargs):
		self.get_ra_dec(**kwargs)
		self.scan_seq(**kwargs)
		return self.ra_data, self.dec_data
	
	#function that produces ra and dec arrays based on the scan parameters and the observer's location
	def get_ra_dec(self, **kwargs):
		
		#defining a few useful values
		self.n_stp = int(self.e_rng/self.e_stp) + 1 #number of steps
		l = self.a_thr*(self.n_stp) + self.e_rng*2 #total length of path of scan
		self.t_end = l/self.dt_scn #total scan time
		self.a_min = self.az_0 - (self.a_thr/2) #min az
		self.a_max = self.az_0 + (self.a_thr/2) #max az
		self.e_min = self.el_0 - (self.e_rng/2) #min el
		self.e_max = self.el_0 + (self.e_rng/2) #max el
		
		self.telescope_loc = ephem.Observer()
		if 'obs' in kwargs:
			self.telescope_loc.lon = kwargs["obs"].lon
			self.telescope_loc.lat = kwargs["obs"].lat
		else:
			self.telescope_loc.lon = self.default_loc.lon
			self.telescope_loc.lat = self.default_loc.lat	
		
		#self.scan_seq()
		#return self.ra_data, self.dec_data

	def scan_seq(self, **kwargs):
		
		#arrays that the data will be in
		t = np.linspace(0., self.t_end, self.t_end/self.dt)
		self.ra_data = np.empty(int(self.t_end/self.dt))
		self.dec_data = np.empty(int(self.t_end/self.dt))
		
		#scan sequence
		flag = 0 #flag helps to establish zig zag pattern
		for i in range (0, self.n_stp):
			if i == 0:
			#first step of the scan: makes sure we're not appending to an empty array
				self.telescope_loc.date = datetime.utcnow()
				ra_min, dec_min = crd.hor_to_eq(self.a_min, self.e_min, float(self.telescope_loc.lat), self.telescope_loc.sidereal_time())
				ra_max, dec_max = crd.hor_to_eq(self.a_max, self.e_max, float(self.telescope_loc.lat), self.telescope_loc.sidereal_time())
				#print ra_min, ra_max
				#print dec_min, dec_max, '\n'
				dec_stp = abs(dec_max - dec_min)/(self.n_stp - 1)
				ra_data = np.linspace(ra_min, ra_max, abs(ra_max - ra_min)/self.dt)
				dec_data = np.repeat(dec_min, abs(ra_max - ra_min)/self.dt)
				ra_data = np.append(ra_data, np.repeat(ra_max, dec_stp/self.dt))
				dec_data = np.append(dec_data, np.linspace(dec_min, dec_min + dec_stp, dec_stp/self.dt))
				flag = 1
				continue
			
			if flag == 1:
				self.telescope_loc.date = datetime.utcnow()
				ra_min, dec_min = crd.hor_to_eq(self.a_min, self.e_min, float(self.telescope_loc.lat), self.telescope_loc.sidereal_time())
				ra_max, dec_max = crd.hor_to_eq(self.a_max, self.e_max, float(self.telescope_loc.lat), self.telescope_loc.sidereal_time())
				#print ra_min, ra_max
				#print dec_min, dec_max, '\n'
				dec_stp = abs(dec_max - dec_min)/(self.n_stp - 1)   
				ra_data = np.append(ra_data, np.linspace(ra_max, ra_min, abs(ra_max - ra_min)/self.dt))
				dec_data = np.append(dec_data, np.repeat(dec_min + i * dec_stp, abs(ra_max - ra_min)/self.dt))
				if (self.e_min + (i+1) * self.e_stp) > self.e_max:
				#stops if this step will exceed e_max
					break
				else:           
					ra_data = np.append(ra_data, np.repeat(ra_min, dec_stp/self.dt))
					dec_data = np.append(dec_data, np.linspace(dec_min + i * dec_stp, dec_min + (i+1) * dec_stp, dec_stp/self.dt))
					flag = 0
					continue
		
			else:
				self.telescope_loc.date = datetime.utcnow()
				ra_min, dec_min = crd.hor_to_eq(self.a_min, self.e_min, float(self.telescope_loc.lat), self.telescope_loc.sidereal_time())
				ra_max, dec_max = crd.hor_to_eq(self.a_max, self.e_max, float(self.telescope_loc.lat), self.telescope_loc.sidereal_time())
				#print ra_min, ra_max
				#print dec_min, dec_max, '\n'
				dec_stp = abs(dec_max - dec_min)/(self.n_stp - 1)
				ra_data = np.append(ra_data, np.linspace(ra_min, ra_max, abs(ra_max - ra_min)/self.dt))
				dec_data = np.append(dec_data, np.repeat(dec_min + i * dec_stp, abs(ra_max - ra_min)/self.dt))
				if (self.e_min + (i+1) * self.e_stp) > self.e_max:
				#stops if this step will exceed e_max
					break
				else:
					ra_data = np.append(ra_data, np.repeat(ra_max, dec_stp/self.dt))
					dec_data = np.append(dec_data, np.linspace(dec_min + i * dec_stp, dec_min + (i+1) * dec_stp, dec_stp/self.dt))
					flag = 1
					continue
		
		#return self.ra_data, self.dec_data
		
	
	
	
	if __name__ == "__main__":
		usc = ephem.Observer()
		usc.lat = '34.019579'
		usc.lon = '-118.286926'
		get_ra_dec(obs=usc)



