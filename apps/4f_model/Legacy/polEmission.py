import numpy as np
import thermo as th
import scipy.integrate as intg

chi = np.deg2rad(32.5)
e0 = 8.81e-12
rho = 2.417e-8
nu = 145e9
Dnu = 10e9
e = lambda x : np.sqrt(4 * np.pi * e0 * x * rho)
e2 = (1 / np.cos(chi) - np.cos(chi))
fact = 1e12 * (1 / .18)

emisAtm = 3.34e-2

p1 = intg.quad(lambda x:  e2 * e(x) * th.weightedSpec(x, 273, 1) , nu - Dnu, nu + Dnu)[0]
p2 = intg.quad(lambda x:  e2 * e(x) * th.weightedSpec(x, 273, emisAtm) , nu - Dnu, nu + Dnu)[0]
print e2
# print p1*1e12
print  (p1 - p2)*fact


