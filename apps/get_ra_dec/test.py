import numpy as np
import matplotlib.pyplot as plt
import ephem
from lab_analysis.libs.geometry import coordinates as crd
#from lab_analysis.libs import lab_app
from datetime import datetime
from lab_analysis.apps.get_ra_dec import get_ra_dec
np.set_printoptions(edgeitems = 50)


#class Simulator(lab_app.App):
#def run(self)


#establishing the location of our observer (USC in this case)
tokyo = ephem.city("Tokyo")
#usc.lon = '-118.286926'
#usc.lat = '34.019579'

#scan parameters
scan = get_ra_dec.ScanParameters()
#producing ra and dec arrays with given scan parameters and observer location
r, d = scan.run_scan()

plt.plot(r, d, 'b')
plt.show()

'''
#ra and dec to galactic lon and lat
l, b = crd.eq_to_gal(r, d)








#plot to make sure things went as planned
plt.plot(l, b, 'b')
plt.show()
'''
