import numpy as np
import datetime
import ephem
from lab_analysis.apps.simulation import default_settings 

np.set_printoptions(edgeitems = 50)


def generate_datetimes():
	'''
	Function: generate_datetimes()
	Purpose: to generate an array of datetimes in a specified time range. Default is for one hour starting at 1/1/2018
	Inputs: none
	Outputs: datetime_array (array of datetimes)
	'''
	settings = default_settings.SimulatorSettings()
	datetime_start = datetime.datetime(2018, 1, 1)
	#will increment in seconds, so range has to be number of seconds in one day
	num_secs_per_hour = 24 * 3600
	datetime_array = np.zeros(1)
	datetime_range = num_secs_per_hour
	for i in range (0, datetime_range):
		datetime_array = np.append(datetime_array, (datetime_start + datetime.timedelta(seconds = i)))
	
	return np.delete(datetime_array, 0)
	#for some reason, I wasn't able to generate the array without initializing it with at least one value
	#so I initialized the array as one "zero", and in the np.delete line, I'm deleting that first bogus entry
	#before returning the array

if __name__ == "__main__":
	arr = generate_datetimes()
	print arr	
	
