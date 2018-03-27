import numpy as np
import matplotlib.pyplot as plt
from lab_analysis.libs.units.angles import *

def write_coords_to_file(times, coords):
	lats = list(coords[0])
	lons = list(coords[1])
	with open('/home/rashmi/maps/test_coords.txt', 'w') as f:
		f.write('times\tlat\tlon\n')
		for i in np.arange(len(times)):
			f.write('\n{}\t{:.3e}\t{:.3e}'.format(times[i], lats[i], lons[i]))


def use_test_pointing(times):
	lats = from_degrees(np.arange(0, times.size)*4.0/times.size-2.0)
	lons = np.zeros(times.size)
	test_pointing = lats, lons
	return test_pointing


def print_local_min_max(v, delta, x = None):
	import sys
	np.set_printoptions(precision = 4)
	mxpos_tab = []
	mnpos_tab = []
	mx_tab = []
	mn_tab = []
	if x is None:
		x = np.arange(len(v))
		v = np.asarray(v)
	
	if len(v) != len(x):
		sys.exit('Input vectors v and x must have same length')
	
	if not np.isscalar(delta):
		sys.exit('Input argument delta must be a scalar')
	
	if delta <= 0:
		sys.exit('Input argument delta must be positive')
	
	mn, mx = np.Inf, -np.Inf
	mnpos, mxpos = np.NaN, np.NaN
	
	lookformax = True
	
	for i in np.arange(len(v)):
		this = v[i]
		if this > mx:
			mx = this
			mxpos = x[i]
		if this < mn:
			mn = this
			mnpos = x[i]
		
		if lookformax:
			if this < mx - delta:
				mxpos_tab = np.append(mxpos_tab, mxpos)
				mx_tab = np.append(mx_tab, mx)
				mn = this
				mnpos = x[i]
				lookformax = False
		else:
			if this > mn + delta:
				mnpos_tab = np.append(mnpos_tab, mnpos)
				mn_tab = np.append(mn_tab, mn)
				mx = this
				mxpos = x[i]
				lookformax = True
	plt.scatter(mxpos_tab, mx_tab, color = 'blue')
	plt.scatter(mnpos_tab, mn_tab, color = 'red')
	for i in np.arange(len(mx_tab)-1):
		plt.annotate('({:.3f}, {:.3e})'.format(mxpos_tab[i], mx_tab[i]), xy = (mxpos_tab[i], mx_tab[i]), \
			xytext = (mxpos_tab[i], mx_tab[i] + 0.000005))
		plt.annotate('({:.3f}, {:.3e})'.format(mnpos_tab[i], mn_tab[i]), xy = (mnpos_tab[i], mn_tab[i]), \
			xytext = (mnpos_tab[i], mn_tab[i] - 0.00001))



