# -*- coding: utf-8 -*-
"""
x       - input signal (vector of real numbers)
qResol  - Resolution in dBs
qResid  - Residual energy 
step   - Gradient step size (normally is set to 1, can take values 0-1) 
"""

import numpy as np


def splineEMD = splineEMD(x,Resol,Resid,step):
    
    sig = x                         #get copy of signal
    Psig = np.norm(x)**2            #Original signal energy
    siglen = len(sig)               #Signal length
    
    #now we are ready to decompose the signal into IMFs
    
    imfs = []                       #empty matrix of IMFs and residue
    funccount = 0
    iResid = 0                 #equal energies @ start are zero
    number = osc(sig)               
    
    while iResid < Resid and number > 2 #while the signal has some energy and oscillates
        iImf = sig
        """code 
        for
        getting
        IMFs
        """

def osc = osc(x):
#gets the oscillation count and locations of oscillations
    
    ocount = 0
    top = False
    bottom = False

    for i in range(1,length(x)-1):
        if x[i-1] < x[i] and x[i] > x[i+1]: #Maximum
            ocount = ocount + 1
            
        if x[i-1] > x[i] and x[i] < x[i+1]: #Minimum
            ocount = ocount + 1
        
        #this is to handle the off chance of us sampling two minimums of equal magnitude next to each other
        if x[i-1] > x[i] and x[i] == x[i+1]: 
            top = False 
            down = True
        if x[i-1] == x[i] and x[i] > x[i+1]:
            if down :
                ocount = ocount + 1
            down = False
        
        #this is to handle the off chance of us sampling to maximums of equal magnitude next to each other
        if x[i-1] < x[i] and x[i] == x[i+1]:
            top = True
            down = False
        if x[i-1] == x[i] and x[i] < x[i+1]:
            if top:
                ocount = ocount + 1
            down = False
    
    return ocount


            

def 
            