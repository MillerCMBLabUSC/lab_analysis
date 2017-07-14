import numpy as np
import matplotlib.pyplot as plt
import ephem
from lab_analysis.apps.simulation import default_settings
from lab_analysis.libs.geometry import coordinates as crd
from datetime import datetime
np.set_printoptions(edgeitems = 50)

class CreatePointing(default_settings.SimulatorSettings):
	def run_scan(self, **kwargs):
		self.scan_setup(**kwargs)
		self.scan_seq(**kwargs)
		if self.num_bolos == 1:
			return self.ra1_data, self.dec1_data
		if self.num_bolos == 2:
			return self.ra1_data, self.dec1_data, self.ra2_data, self.dec2_data
	
	def scan_setup(self, **kwargs):
		#defining a few useful values
		self.n_stp = int(self.e_rng/self.e_stp) + 1 #number of steps
		l = self.a_thr*(self.n_stp) + self.e_rng*2 #total length of path of scan
		self.dt =float(l)/self.t_end #total scan time
		print self.dt
		self.a_min = self.az_0 - (self.a_thr/2) #min az
		self.a_max = self.az_0 + (self.a_thr/2) #max az
		self.e_min = self.el_0 - (self.e_rng/2) #min el
		self.e_max = self.el_0 + (self.e_rng/2) #max el
		
		#setting up arrays that the data will be in
		self.ra1_data = np.empty(int(self.t_end/self.dt))
		self.dec1_data = np.empty(int(self.t_end/self.dt))
		self.ra2_data = np.empty(int(self.t_end/self.dt))
		self.dec2_data = np.empty(int(self.t_end/self.dt))
	
	def scan_seq(self, **kwargs):
		#scan sequence
		flag = 0 #flag helps to establish zig zag pattern
		for i in range (0, self.n_stp):
			if i == 0:
			#first step of the scan: makes sure we're not appending to an empty array
				self.bolo1.date = datetime.utcnow()
				self.bolo2.date = datetime.utcnow()
				ra1_min, dec1_min = crd.hor_to_eq(self.a_min, self.e_min, float(self.bolo1.lat), self.bolo1.sidereal_time())
				ra1_max, dec1_max = crd.hor_to_eq(self.a_max, self.e_max, float(self.bolo1.lat), self.bolo1.sidereal_time())
				#print ra_min, ra_max
				#print dec_min, dec_max, '\n'
				dec1_stp = abs(dec1_max - dec1_min)/(self.n_stp - 1)
				self.ra1_data = np.linspace(ra1_min, ra1_max, abs(ra1_max - ra1_min)/self.dt)
				self.dec1_data = np.repeat(dec1_min, abs(ra1_max - ra1_min)/self.dt)
				self.ra1_data = np.append(self.ra1_data, np.repeat(ra1_max, dec1_stp/self.dt))
				self.dec1_data = np.append(self.dec1_data, np.linspace(dec1_min, dec1_min + dec1_stp, dec1_stp/self.dt))
				#if using 2 bolos, this portion puts data into second ra/dec arrays
				if self.num_bolos == 2:
					ra2_min, dec2_min = crd.hor_to_eq(self.a_min, self.e_min, float(self.bolo2.lat), self.bolo2.sidereal_time())
					ra2_max, dec2_max = crd.hor_to_eq(self.a_max, self.e_max, float(self.bolo2.lat), self.bolo2.sidereal_time())
					dec2_stp = abs(dec2_max - dec2_min)/(self.n_stp - 1)
					self.ra2_data = np.linspace(ra2_min, ra2_max, abs(ra2_max - ra2_min)/self.dt)
					self.dec2_data = np.repeat(dec2_min, abs(ra2_max - ra2_min)/self.dt)
					self.ra2_data = np.append(self.ra2_data, np.repeat(ra2_max, dec2_stp/self.dt))
					self.dec2_data = np.append(self.dec2_data, np.linspace(dec2_min, dec2_min + dec2_stp, dec2_stp/self.dt))
			
				flag = 1
				continue
			
			if flag == 1:
				self.bolo1.date = datetime.utcnow()
				self.bolo2.date = datetime.utcnow()
				ra1_min, dec1_min = crd.hor_to_eq(self.a_min, self.e_min, float(self.bolo1.lat), self.bolo1.sidereal_time())
				ra1_max, dec1_max = crd.hor_to_eq(self.a_max, self.e_max, float(self.bolo1.lat), self.bolo1.sidereal_time())
				#print ra_min, ra_max
				#print dec_min, dec_max, '\n'
				dec1_stp = abs(dec1_max - dec1_min)/(self.n_stp - 1)
				self.ra1_data = np.append(self.ra1_data, np.linspace(ra1_max, ra1_min, abs(ra1_max - ra1_min)/self.dt))
				self.dec1_data = np.append(self.dec1_data, np.repeat(dec1_min + i*dec1_stp, abs(ra1_max - ra1_min)/self.dt))
				if self.num_bolos == 2:
					ra2_min, dec2_min = crd.hor_to_eq(self.a_min, self.e_min, float(self.bolo2.lat), self.bolo2.sidereal_time())
					ra2_max, dec2_max = crd.hor_to_eq(self.a_max, self.e_max, float(self.bolo2.lat), self.bolo2.sidereal_time())
					dec2_stp = abs(dec2_max - dec2_min)/(self.n_stp - 1)   
					self.ra2_data = np.append(self.ra2_data, np.linspace(ra2_max, ra2_min, abs(ra2_max - ra2_min)/self.dt))
					self.dec2_data = np.append(self.dec2_data, np.repeat(dec2_min + i*dec2_stp, abs(ra2_max - ra2_min)/self.dt))
										
				if (self.e_min + (i+1)*self.e_stp) > self.e_max:
				#stops if this step will exceed e_max
					break
				else:           
					self.ra1_data = np.append(self.ra1_data, np.repeat(ra1_min, dec1_stp/self.dt))
					self.dec1_data = np.append(self.dec1_data, np.linspace(dec1_min + i*dec1_stp, dec1_min + (i+1)*dec1_stp, dec1_stp/self.dt))
					if self.num_bolos == 2:
						self.ra2_data = np.append(self.ra2_data, np.repeat(ra2_min, dec2_stp/self.dt))
						self.dec2_data = np.append(self.dec2_data, np.linspace(dec2_min + i*dec2_stp, dec2_min + (i+1)*dec2_stp, dec2_stp/self.dt))
					flag = 0
					continue
			
			else:
				self.bolo1.date = datetime.utcnow()
				self.bolo2.date = datetime.utcnow()
				ra1_min, dec1_min = crd.hor_to_eq(self.a_min, self.e_min, float(self.bolo1.lat), self.bolo1.sidereal_time())
				ra1_max, dec1_max = crd.hor_to_eq(self.a_max, self.e_max, float(self.bolo1.lat), self.bolo1.sidereal_time())
				#print ra_min, ra_max
				#print dec_min, dec_max, '\n'
				dec1_stp = abs(dec1_max - dec1_min)/(self.n_stp - 1)
				self.ra1_data = np.append(self.ra1_data, np.linspace(ra1_min, ra1_max, abs(ra1_max - ra1_min)/self.dt))
				self.dec1_data = np.append(self.dec1_data, np.repeat(dec1_min + i*dec1_stp, abs(ra1_max - ra1_min)/self.dt))
				if self.num_bolos == 2:
					ra2_min, dec2_min = crd.hor_to_eq(self.a_min, self.e_min, float(self.bolo2.lat), self.bolo2.sidereal_time())
					ra2_max, dec2_max = crd.hor_to_eq(self.a_max, self.e_max, float(self.bolo2.lat), self.bolo2.sidereal_time())
					dec2_stp = abs(dec2_max - dec2_min)/(self.n_stp - 1)
					self.ra2_data = np.append(self.ra2_data, np.linspace(ra2_min, ra2_max, abs(ra2_max - ra2_min)/self.dt))
					self.dec2_data = np.append(self.dec2_data, np.repeat(dec2_min + i*dec2_stp, abs(ra2_max - ra2_min)/self.dt))
				
				if (self.e_min + (i+1)*self.e_stp) > self.e_max:
				#stops if this step will exceed e_max
					break
				else:
					self.ra1_data = np.append(self.ra1_data, np.repeat(ra1_max, dec1_stp/self.dt))
					self.dec1_data = np.append(self.dec1_data, np.linspace(dec1_min + i*dec1_stp, dec1_min + (i+1)*dec1_stp, dec1_stp/self.dt))
					if self.num_bolos == 2:
						self.ra2_data = np.append(self.ra2_data, np.repeat(ra2_max, dec2_stp/self.dt))
						self.dec2_data = np.append(self.dec2_data, np.linspace(dec2_min + i*dec2_stp, dec2_min + (i+1)*dec2_stp, dec2_stp/self.dt))
					flag = 1
					continue
		
		if self.num_bolos == 1:
			return self.ra1_data, self.dec1_data
		if self.num_bolos == 2:
			return self.ra1_data, self.dec1_data, self.ra2_data, self.dec2_data
	
