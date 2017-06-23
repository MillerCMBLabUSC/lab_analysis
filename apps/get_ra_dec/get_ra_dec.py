import numpy as np
import matplotlib.pyplot as plt
import ephem
from lab_analysis.libs.geometry import coordinates as crd
from datetime import datetime
np.set_printoptions(edgeitems = 50)

#loading scan parameters into a ScanParameters class
class ScanParameters():
	def __init__(self, az_0=50, el_0=50, a_thr=10, e_rng=10, e_stp=2, dt_scn=1, **kwargs):
		#all of these values must be floats except kwargs
		self.az_0 = az_0
		self.el_0 = el_0
		self.a_thr = a_thr
		self.e_rng = e_rng
		self.e_stp = e_stp
		self.dt_scn = dt_scn
		
		#defining a few useful values
		self.n_stp = int(self.e_rng/self.e_stp) + 1 #number of steps
		l = self.a_thr*(self.n_stp) + self.e_rng*2 #total length of path of scan
		self.t_end = l/self.dt_scn #total scan time
		self.dt = 0.01 #data time interval
		self.a_min = self.az_0 - (self.a_thr/2) #min az
		self.a_max = self.az_0 + (self.a_thr/2) #max az
		self.e_min = self.el_0 - (self.e_rng/2) #min el
		self.e_max = self.el_0 + (self.e_rng/2) #max el

		
	#function that produces ra and dec arrays based on the scan parameters and the observer's location
	def get_ra_dec(self, **kwargs):
		telescope_loc = ephem.Observer()
		if 'obs' in kwargs:
			#obs is an ephem.Observer() object
			telescope_loc.lon = kwargs["obs"].lon
			telescope_loc.lat = kwargs["obs"].lat
		else:
			#default location at USC
			telescope_loc.lon = '-118.286926'
			telescope_loc.lat = '34.019579'

		
		#arrays that the data will be in
		t = np.linspace(0., self.t_end, self.t_end/self.dt)
		ra_data = np.empty(int(self.t_end/self.dt))
		dec_data = np.empty(int(self.t_end/self.dt))

		flag = 0 #flag helps to establish zig zag pattern
		#scan sequence
		for i in range (0, self.n_stp):
			if i == 0:
			#first step of the scan: makes sure we're not appending to an empty array
				telescope_loc.date = datetime.utcnow()
				ra_min, dec_min = crd.hor_to_eq(self.a_min, self.e_min, float(telescope_loc.lat), telescope_loc.sidereal_time())
				ra_max, dec_max = crd.hor_to_eq(self.a_max, self.e_max, float(telescope_loc.lat), telescope_loc.sidereal_time())
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
				telescope_loc.date = datetime.utcnow()
				ra_min, dec_min = crd.hor_to_eq(self.a_min, self.e_min, float(telescope_loc.lat), telescope_loc.sidereal_time())
				ra_max, dec_max = crd.hor_to_eq(self.a_max, self.e_max, float(telescope_loc.lat), telescope_loc.sidereal_time())
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
				telescope_loc.date = datetime.utcnow()
				ra_min, dec_min = crd.hor_to_eq(self.a_min, self.e_min, float(telescope_loc.lat), telescope_loc.sidereal_time())
				ra_max, dec_max = crd.hor_to_eq(self.a_max, self.e_max, float(telescope_loc.lat), telescope_loc.sidereal_time())
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



		#plt.plot(ra_data, dec_data, 'b')
		#plt.show()
		
		return ra_data, dec_data


	if __name__ == "__main__":
		usc = ephem.Observer()
		usc.lat = '34.019579'
		usc.lon = '-118.286926'
		get_ra_dec(obs=usc)



