import numpy as np
import datetime
import ephem
from lab_analysis.apps.simulation import default_settings 

np.set_printoptions(edgeitems = 50)


def generate_datetimes():
	settings = default_settings.SimulatorSettings()
	datetime_start = datetime.datetime(2018, 1, 1)
	#will increment in seconds, so range has to be number of seconds in one day
	num_secs_per_hour = 24 * 3600
	datetime_array = np.zeros(1)
	#datetime_range = int(settings.t_end / settings.dt)
	datetime_range = num_secs_per_hour
	for i in range (0, datetime_range):
		datetime_array = np.append(datetime_array, (datetime_start + datetime.timedelta(seconds = i)))
	
	#print datetime_array
	return np.delete(datetime_array, 0)

if __name__ == "__main__":
	arr = generate_datetimes()
	print arr	
	
