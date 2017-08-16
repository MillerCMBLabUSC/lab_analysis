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
#gets locations of oscillations based on the discrete samples
    
    top = False
    bottom = False
    minmax = 
    osc = np.zeros(len(x)-2,2)

    for i in range(1,length(x)-1):
        if x[i-1] < x[i] and x[i] > x[i+1]: #Maximum
            osc[i-1,0] = x[i]
            osc[i-1,1] = 'max'
            
        if x[i-1] > x[i] and x[i] < x[i+1]: #Minimum
            osc[i-1,0] = x[i]
            osc[i-1,1] = 'min'
            
        #this is to handle the off chance of us sampling two minimums of equal 
        #magnitude next to each other
        if x[i-1] > x[i] and x[i] == x[i+1]: 
            top = False 
            down = True
        if x[i-1] == x[i] and x[i] > x[i+1]:
            if down :
                osc[i-1,0] = x[i]
                osc[i-1,1] = 'min'
            down = False
        
        #this is to handle the off chance of us sampling to maximums of equal
        #magnitude next to each other
        if x[i-1] < x[i] and x[i] == x[i+1]:
            top = True
            down = False
        if x[i-1] == x[i] and x[i] < x[i+1]:
            if top:
                osc[i-1,0] = x[i]
                osc[i-1,1] = 'max'
            down = False
    
    return osc

def interp = interp(x):
#gets locations of the oscillations based on parabolic interpolation

    ocount = 0
    forcount = 0
    
    tvalues = np.zeros((len(x)-2,3))
    cmat = np.zeros((len(x))-2,3)
    
    for i in range(1,len(x)-1):
        for j in range(0,3):
            tvalues[i-1,j]=i+j-1
        count = count + 1
        if count == 3
            A = np.matrix(tvalues[range(i-1,i+2)]**2)
            b = np.array([x[i-1],x[i],x[i+1]])
            coeff = np.linalg.solve(A,b)
            count = 0;
            cmat[i] = coeff
    
    #get the interpolated min/max
    #vertex of parabola located @ t = -b/2a
    
    interpolated = np.zeros(len(x)-2)
    interp = np.zeros(len(x)-2,2)
    
    for i in range(1,len(x)-1):
        a = coeff[i-1,0]
        b = coeff[i-1,1]
        c = coeff[i-1,2]
        interpolated[i] = a*(b**2)/(4*(a**2)) - (b**2)/(4*a) + c
        if a > 0:
            interp[i-1,0] = interpolated[i]
            interp[i-1,1] = 'min'
        if a < 0: 
            interp[i-1,0] = interpolated[i]
            interp[i-1,1] = 'max'
        if a == 0:
            interp[i-1,0] = interpolated[i]
            interp[i-1,1] = 'saddle'
            
    ''' add code to 
    interpolate end points 
    using ghost cells
    '''
    
        
    return interp
        
           
            
            

def 
            