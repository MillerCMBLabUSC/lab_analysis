import numpy as np
import datetime
import ephem

np.set_printoptions(edgeitems = 50)


def generate_datetimes():
	datetime_start = datetime.datetime(2018, 1, 1)
	#will increment in seconds, so range has to be number of seconds in one day
	num_secs_per_day = 3600 * 24
	datetime_array = np.zeros(1)
	for i in range (0, num_secs_per_day):
		datetime_array = np.append(datetime_array, (datetime_start + datetime.timedelta(seconds=i)))
	
	#print datetime_array
	return np.delete(datetime_array, 0)

if __name__ == "__main__":
	arr = generate_datetimes()
	print arr	
	
