#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 20 20:41:02 2017

@author: jacoblashner
"""

import numpy as np
import matplotlib.pyplot as plt

ae = lambda nu : 1.47*10**(-7) * nu**(2.2)
ao = lambda nu : 8.7*10**(-5)*nu+3.1*10**(-7)*nu**2 + 3.0*10**(-10)*nu**3



d = .3 #cm

ee = lambda nu : (1 - np.exp(ae(nu) * d))
eo = lambda nu : (1 - np.exp(ao(nu) * d))


freqs = np.linspace(60, 240)
plt.plot(freqs, map(ae, freqs))
plt.plot(freqs, map(ao, freqs))
plt.show()

plt.plot(freqs, map(ee, freqs))
plt.plot(freqs, map(eo, freqs))
plt.show()
print "ae: ", ae(145)
print "ao: ", ao(145)
print "eps_pol: ", .5*(ee(145)**2 - eo(145)**2)

