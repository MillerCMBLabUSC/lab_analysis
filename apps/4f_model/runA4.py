5#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 17 20:02:32 2017

@author: jacoblashner
"""

import src.Telescope as tp
import src.thermo as th
import numpy as np
import matplotlib.pyplot as plt

pW = 10 ** 12
GHz = 10**9

#fexpDir = "Experiments/small_aperture/LargeTelescope/"    
expDir = "Experiments/small_aperture/WarmHWP/"
atmFile = "src/Atacama_1000um_60deg.txt"

theta = 20
hwpFile = "HWP_Mueller/Mueller_AR/Mueller_V2_nu150.0_no3p068_ne3p402_ARcoat_thetain%d.0.txt"%theta
bid = 2

opts = {'theta': np.deg2rad(theta)}

tel = tp.Telescope(expDir, atmFile, hwpFile, bid, **opts)

hwp = tel.elements[tel.hwpIndex]

print "A2 (KRJ)", tel.A2 /tel.cumEff(0, tel.det.band_center)  /th.kB / (tel.det.band_center * tel.det.fbw)
print "A4 (KRJ)", tel.A4 /tel.cumEff(0, tel.det.band_center)  /th.kB / (tel.det.band_center * tel.det.fbw)
print "Tel Efficiency", tel.cumEff(0, tel.det.band_center)





