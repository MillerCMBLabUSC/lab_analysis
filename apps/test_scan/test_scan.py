import numpy as np

#user inputs parameters
az_0 = float(input('az_0= '))
el_0 = float(input('el_0= '))
a_thr = float(input('Enter the azimuth throw: '))
e_rng = float(input('Enter the elevation range: '))
e_stp = float(input('Enter the elevation step size: '))
dt_scn = float(input('Enter the scan speed in degrees/sec: '))

#defining a few useful values
n_stp = int(e_rng/e_stp) #number of steps
l = a_thr*(n_stp+1) + e_rng*2 #total length of path of scan
t_end = l/dt_scn #total scan time
dt = 0.01 #data time interval
a_min = az_0 - (a_thr/2) #min az
a_max = az_0 + (a_thr/2) #max az
e_min = el_0 - (e_rng/2) #min el
e_max = el_0 + (e_rng/2) #max el

t = np.linspace(0., t_end, t_end/dt)
az = np.zeros(int(t_end/dt))
el = np.zeros(int(t_end/dt))
flag = 1

for i in range (0, n_stp):
	if flag == 1:
		az = np.linspace(a_min, a_max, a_thr/dt)
		el = np.repeat(e_min + i*e_stp, a_thr/dt)
		print az, el
		el = np.linspace(e_min + i*e_stp, e_min + (i+1) * e_stp, e_stp/dt)
		az = np.repeat(a_max, e_stp/dt)
		print az, el
		flag = 0
	else:
		az = np.linspace(a_max, a_min, a_thr/dt)
		el = np.repeat(e_min + i*e_stp, a_thr/dt)
		print az, el
		el = np.linspace(e_min + i*e_stp, e_min + (i+1) * e_stp, e_stp/dt)
		az = np.repeat(a_min, e_stp/dt)
		print az, el
		flag = 1


#print t

#print az

#print el





