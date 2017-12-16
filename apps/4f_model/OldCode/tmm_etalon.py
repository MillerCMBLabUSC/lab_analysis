#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 15 23:44:03 2017

@author: gteply
"""

from pylab import *
import tmm

lam0=2.5

n0=3.1

# frequencies
frequency=arange(1,300,1)

#gaps
a=arange(0.01,0.55,0.01)

ip100=[]
ip150=[]

d_gap=arange(0.1,30.0,0.05)

dd = 2.0

n=[]
d=[]
n.append(1.0)
d.append(inf)
n.append(n0**(1./3))
d.append(lam0/(4.0*real(n0)**(1./3)))
n.append(n0**(2./3))
d.append(lam0/(4.0*real(n0)**(2./3)))
n.append(n0)
d.append(2.0)
n.append(n0**(2./3))
d.append(lam0/(4.0*real(n0)**(2./3)))
n.append(n0**(1./3))
d.append(lam0/(4.0*real(n0)**(1./3)))
n.append(1.0)
d.append(dd)
n.append(n0**(1./3))
d.append(lam0/(4.0*real(n0)**(1./3)))
n.append(n0**(2./3))
d.append(lam0/(4.0*real(n0)**(2./3)))
n.append(n0)
d.append(2.0)
n.append(n0**(2./3))
d.append(lam0/(4.0*real(n0)**(2./3)))
n.append(n0**(1./3))
d.append(lam0/(4.0*real(n0)**(1./3)))
n.append(1.0)
d.append(inf)

ips = []

lam_vac=299.792458/150.
# p-wave
p=tmm.coh_tmm('p',n,d,deg2rad(12.5),lam_vac)
# s-wave
s=tmm.coh_tmm('s',n,d,deg2rad(12.5),lam_vac)

# ips += [(p['T']-s['T'])/2.0]

for f in frequency:
    lam_vac=299.792458/f
    # p-wave
    p=tmm.coh_tmm('p',n,d,deg2rad(12.5),lam_vac)
    # s-wave
    s=tmm.coh_tmm('s',n,d,deg2rad(12.5),lam_vac)

    ips += [(p['T']-s['T'])/(p['T']+s['T'])]

print(mean(ips[130:171]))


# # plot(d_gap,ip100)
# plot(d_gap,ip150)
# xlabel('Gap (mm)')
# ylabel('IP')
# legend(['75-105 GHz average','130-170 GHz average'])
# title('12.5 degrees')
# tight_layout()
# savefig('ip_vs_gap.png')
# clf()