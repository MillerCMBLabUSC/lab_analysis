import numpy as np
import matplotlib.pyplot as plt
import ephem
from lab_analysis.libs.geometry import coordinates as crd
#from lab_analysis.libs import lab_app
from datetime import datetime
from lab_analysis.apps.simulation import get_ra_dec
np.set_printoptions(edgeitems = 50)


#class Simulator(lab_app.App):
#	def run(self):
#		initialize everything
#		self.get_l_b()
#		load maps
#		get timestreams
#		save to file
#		end

#	def get_l_b(self):
scan = get_ra_dec.CreatePointing()

if scan.num_bolos == 1:
	r, d = scan.run_scan()
	l, b = crd.eq_to_gal(r, d)
	
	plt.plot(l, b, 'r')
	plt.show()
	
	#print l, b
	#return l, b

if scan.num_bolos == 2:
	r1, d1, r2, d2 = scan.run_scan()
	l1, b1 = crd.eq_to_gal(r1, d1)
	l2, b2 = crd.eq_to_gal(r2, d2)
	
	plt.plot(l1, b1, 'b')
	plt.plot(l2, b2, 'g')
	plt.show()
	
	#print l1, b1, '\n', l2, b2
	#return l1, b1, l2, b2
	print r1.size









