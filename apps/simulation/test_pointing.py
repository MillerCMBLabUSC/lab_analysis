import numpy as np
import matplotlib.pyplot as plt
from lab_analysis.libs.units.angles import *

'''
File: test_pointing

Purpose: provide a series of specialized functions/parameters/pointing scheme to test
	the simulation code. This group of functions is only called when the conduct_test
	parameter in the default_settings file is set to True. 

Functions:
-> write_coords_to_file
-> use_test_pointing
-> print_local_min_max
'''

def write_coords_to_file(times, coords):
	'''
	Function: write_coords_to_file
	
	Purpose: writes the times and coordinates (galactic lats/lons) to a text file. When testing the
		simulation code, it is helpful to have a list of times/coords to reference
	
	Inputs:
	-> times (float): an array of times
	-> coords (float): an array of coords (galactic lats/lons) from the pointing scheme used

	Outputs:
	-> /home/rashmi/maps/test_coords.txt: text file containing list of times/coords 
	'''
	
	lats = list(coords[0])
	lons = list(coords[1])
	with open('/home/rashmi/maps/test_coords.txt', 'w') as f:
		f.write('times\tlat\tlon\n')
		for i in np.arange(len(times)):
			f.write('\n{}\t{:.3e}\t{:.3e}'.format(times[i], lats[i], lons[i]))


def use_test_pointing(times):
	'''
	Function: use_test_pointing
	
	Purpose: creating a fake test pointing. This pointing scans the galactic center at lon = 0.
		When testing the simulation code, it is helpful to scan the galactic center and compare the
		intensity values to the readings from the fits map itself. If we don't add noise/non-linearity/
		HWPSS/etc, then the input map should match the output of the function (especially at
		the galactic center)
	
	Inputs:
	-> times (float): an array of times
	
	Outputs:
	-> test_pointing (float): an array of coords (galactic lats/lons) representing the fake pointing
				along the galactic center (lon = 0)
	'''
	
	lats = from_degrees(np.arange(0, times.size)*4.0/times.size-2.0)
	lons = np.zeros(times.size)
	test_pointing = lats, lons
	return test_pointing


def print_local_min_max(v, delta, x = None):
	'''
	Function: print_local_min_max
	
	Purpose: printing the local minima and maxima on the output chart produced by simulation. When 
		testing the simulation code, it helps to have a list of minima and maxima to compare
		to the input fits map. This function prints those values as (time, value) at each
		of the local extrema
	
	Inputs:
	-> v (float): an array with the input function containing the minima and maxima; the y-values
	-> delta (float): the error margin to distinguish the minima and maxima (eg. low "delta"s 
			will allow you to detect minima/maxima, while large "delta"s will screen for
			the most extreme local extrema
	-> x (float): an array with the x-values. If none is provided (default), x is 1,2,3...
	
	Outputs: annotations on the pyplot figure at the local extrema as (x, y)
	
	Note: this was taken from Stack Overflow. The user who provided this code stated that it was open source
		and could be used without citation.
	
	'''
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



