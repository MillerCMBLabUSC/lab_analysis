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
az_data = np.empty(int(t_end/dt))
el_data = np.empty(int(t_end/dt))


#scan sequence
for i in range (0, n_stp):
	if i == 0:
	#first step of the scan: makes sure we're not appending to an empty array
		az_data = np.linspace(a_min, a_max, a_thr/dt)
		el_data = np.repeat(e_min, a_thr/dt)
		az_data = np.append(az_data, np.repeat(a_max, e_stp/dt))
		el_data = np.append(el_data, np.linspace(e_min, e_min + e_stp, e_stp/dt))
		flag = 1
		continue
	
	if flag == 1:   
                az_data = np.append(az_data, np.linspace(a_max, a_min, a_thr/dt))
                el_data = np.append(el_data, np.repeat(e_min + i * e_stp, a_thr/dt))
		if (e_min + (i+1) * e_stp) > e_max:
		#stops if this step will exceed e_max
			break
                else:           
                        az_data = np.append(az_data, np.repeat(a_min, e_stp/dt))
                        el_data = np.append(el_data, np.linspace(e_min + i * e_stp, e_min + (i+1) * e_stp, e_stp/dt))
                        flag = 0
                        continue

	else:
		az_data = np.append(az_data, np.linspace(a_min, a_max, a_thr/dt))
		el_data = np.append(el_data, np.repeat(e_min + i * e_stp, a_thr/dt))
		if (e_min + (i+1) * e_stp) > e_max:
		#stops if this step will exceed e_max
			break
		else:
			az_data = np.append(az_data, np.repeat(a_max, e_stp/dt))
			el_data = np.append(el_data, np.linspace(e_min + i * e_stp, e_min + (i+1) * e_stp, e_stp/dt))
			flag = 1
			continue


usc = ephem.Observer()
usc.date = datetime.utcnow()
usc.lon = -118.286926
usc.lat = 34.019579

ra, dec = crd.hor_to_eq(az_data, el_data, usc.lat, usc.sidereal_time())

print ra

print dec




