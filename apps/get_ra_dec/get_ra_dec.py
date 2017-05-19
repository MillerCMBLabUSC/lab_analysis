import numpy as np
import matplotlib.pyplot as plt
import ephem
from lab_analysis.libs.geometry import coordinates as crd
from datetime import datetime
np.set_printoptions(edgeitems = 50)

#parameters (either user input or default)
response = raw_input('For default values, enter d. For custom values, enter c. ')
if response == 'd':
	az_0 = 50
	el_0 = 50
	a_thr = 100
	e_rng = 100
	e_stp = 1
	dt_scn = 1
	print('Default values:\n  az_0 = 50 deg \n  el_0 = 50 deg \n  az throw = 100 deg \n  el range = 100 deg \n  el step size = 1 deg \n  scan speed = 1 deg/sec')
if response == 'c':
	az_0 = float(input('az_0= '))
	el_0 = float(input('el_0= '))
	a_thr = float(input('Enter the azimuth throw: '))
	e_rng = float(input('Enter the elevation range: '))
	e_stp = float(input('Enter the elevation step size: '))
	dt_scn = float(input('Enter the scan speed in degrees/sec: '))


usc = ephem.Observer()
usc.date = datetime.utcnow()
usc.lon = -118.286926
usc.lat = 34.019579


#defining a few useful values
n_stp = int(e_rng/e_stp) + 1 #number of steps
l = a_thr*(n_stp) + e_rng*2 #total length of path of scan
t_end = l/dt_scn #total scan time
dt = 0.01 #data time interval
a_min = az_0 - (a_thr/2) #min az
a_max = az_0 + (a_thr/2) #max az
e_min = el_0 - (e_rng/2) #min el
e_max = el_0 + (e_rng/2) #max el
flag = 0 #flag helps to establish zig zag pattern


#arrays that the data will be in
t = np.linspace(0., t_end, t_end/dt)
ra_data = np.empty(int(t_end/dt))
dec_data = np.empty(int(t_end/dt))


#scan sequence
for i in range (0, n_stp):
	if i == 0:
	#first step of the scan: makes sure we're not appending to an empty array
		ra_min, dec_min = crd.hor_to_eq(a_min, e_min, usc.lat(), usc.sidereal_time())
		ra_max, dec_max = crd.hor_to_eq(a_max, e_max, usc.lat(), usc.sidereal_time())
		dec_stp = (dec_max - dec_min)/n_stp - 1
		ra_data = np.linspace(ra_min, ra_max, (ra_max - ra_min)/dt)
		dec_data = np.repeat(dec_min, (ra_max - ra_min)/dt)
		ra_data = np.append(ra_data, np.repeat(ra_max, dec_stp/dt))
		dec_data = np.append(dec_data, np.linspace(dec_min, dec_min + dec_stp, dec_stp/dt))
		flag = 1
		continue
	
	if flag == 1:
		ra_min, dec_min = crd.hor_to_eq(a_min, e_min, usc.lat(), usc.sidereal_time())
		ra_max, dec_max = crd.hor_to_eq(a_max, e_max, usc.lat(), usc.sidereal_time())
		dec_stp = (dec_max - dec_min)/n_stp - 1
   
                ra_data = np.append(ra_data, np.linspace(ra_max, ra_min, (ra_max - ra_min)/dt))
                dec_data = np.append(dec_data, np.repeat(dec_min + i * dec_stp, (ra_max - ra_min)/dt))
		if (e_min + (i+1) * e_stp) > e_max:
		#stops if this step will exceed e_max
			break
                else:           
                        ra_data = np.append(ra_data, np.repeat(ra_min, dec_stp/dt))
                        dec_data = np.append(dec_data, np.linspace(dec_min + i * dec_stp, dec_min + (i+1) * dec_stp, dec_stp/dt))
                        flag = 0
                        continue

	else:
		ra_min, dec_min = crd.hor_to_eq(a_min, e_min, usc.lat(), usc.sidereal_time())
		ra_max, dec_max = crd.hor_to_eq(a_max, e_max, usc.lat(), usc.sidereal_time())
		dec_stp = (dec_max - dec_min)/n_stp - 1

		ra_data = np.append(ra_data, np.linspace(ra_min, ra_max, (ra_max - ra_min)/dt))
		dec_data = np.append(dec_data, np.repeat(dec_min + i * dec_stp, (ra_max - ra_min)/dt))
		if (e_min + (i+1) * e_stp) > e_max:
		#stops if this step will exceed e_max
			break
		else:
			ra_data = np.append(ra_data, np.repeat(ra_max, dec_stp/dt))
			dec_data = np.append(dec_data, np.linspace(dec_min + i * dec_stp, dec_min + (i+1) * dec_stp, dec_stp/dt))
			flag = 1
			continue



print ra_data

print dec_data


plt.plot(ra_data, dec_data, 'b')
plt.show()

