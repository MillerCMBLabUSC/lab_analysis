# -*- coding: utf-8 -*-
"""
x       - input signal (vector of real numbers)
qResol  - Resolution in dBs
qResid  - Residual energy 
step   - Gradient step size (normally is set to 1, can take values 0-1) 
"""

import numpy as np
from scipy.interpolate import interp1d
import math


def splineEMD(x,Resol,Resid,step):
    
    sig = x                                 #get copy of original signal
    t = np.linspace(0,len(sig),len(sig)+1)                    
    Px = np.norm(x)**2                      #Original signal energy
    siglen = len(sig)                       #Signal length
    
    #now we are ready to decompose the signal into IMFs
    
    imfs = []                       #empty matrix of IMFs and residue
    funccount = 0
    iResid = 0                 #equal energies @ start are zero
    number = osc(sig)               
    
    while iResid < Resid and number > 2: #while the signal has some energy and oscillates
        iImf = sig
        (dMin,dMax) = dminmax(iImf)
        (pMin,pMax) = extrap(iImf,dMin,dMax)
        if (abs(len(pMin)-len(pMax)) > 2):
            print('Min/Max count is off')
        topenv = interp1d(pMax[:,0],pMax[:,1], kind='cubic')
        botenv = interp1d(pMin[:,0],pMin[:,1], kind='cubic')
        mean = (topenv + botenv)/2
        while True:
            PImf = np.norm(iImf)**2
            PMean = np.norm(mean)**2
            if PMean > 0:
                res = 10*np.log10(PImf/PMean)
            if res>Resol:
                break #Resolution reached
            #Resolution not reached
            iImf = iImf - step*mean
            (dMin,dMax) = dminmax(iImf)
            (pMin,pMax) = extrap(iImf,dMin,dMax)
            topenv = interp1d(pMax[:,0],pMax[:,1], kind='cubic')
            botenv = interp1d(pMin[:,0],pMin[:,1], kind='cubic')
            mean = (topenv + botenv)/2
            
        imfs.append([iImf])                  #store IMF in list
        sig = sig - iImf                     #subtract IMF from signal
        Psig = np.norm(sig)**2
        if Psig > 0:
            iResid = 10*np.log10(Px/Psig)
        else:
            iRed = math.inf
           
        if Psig/Px > 0: #or some really small positive number, might change later
            sig = residual
            imfs.append([residual])
    
        imfs = np.array(imfs) #place all imfs and residual into matrix (array)
          

def dminmax(x):
#gets locations discrete mins and maxes
 
    
    #initialize empty lists for storing x and y values for min/max
    top = False
    bottom = False
    dmin = []
    dmax = []

    for i in range(1,length(x)-1):
        if x[i-1] < x[i] and x[i] > x[i+1]: #Maximum
            dmax.append([i,x[i]])
            
        if x[i-1] > x[i] and x[i] < x[i+1]: #Minimum
            dmin.append([i,x[i]])
            
        #this is to handle the off chance of us sampling two minimums of equal 
        #magnitude next to each other
        if x[i-1] > x[i] and x[i] == x[i+1]: 
            top = False 
            down = True
        if x[i-1] == x[i] and x[i] > x[i+1]:
            if down :
                dmin.append([i,x[i]])
            down = False
        
        #this is to handle the off chance of us sampling to maximums of equal
        #magnitude next to each other
        if x[i-1] < x[i] and x[i] == x[i+1]:
            top = True
            down = False
        if x[i-1] == x[i] and x[i] < x[i+1]:
            if top:
                dmax.append([i,x[i]])
            down = False
        
    dmax = np.array(dmax)
    dmin = np.array(dmin)
        
    tmin = dmin[:,0]
    tmax = dmax[:,0]
    ymin = dmin[:,1]
    ymax = dmax[:,1]
    
    mincoeff = np.zeros((len(dmax),3))
    maxcoeff = np.zeros((len(dmax),3))
    #get parabolic mins
    
    for i in range(0,len(dmin)):
        #get values on opposite sides of the minimum
        y1 = x[tmin[i]-1]
        y2 = x[tmin[i]]
        y3 = x[tmin[i]+1]
        A = []
        #setup a solve linear equation for coefficients of parabola
        for j in range(0,3):
            A.append([(tmin[i]-1)**2,tmin[i],1])
        A = np.array(A)
        b = np.array([x[tmin[i]-1],x[tmin[i]],x[tmin[i]+1]])
        mincoeff[i] = np.linalg.solve(A,b)
    
    #get parabolic maxs
    
    for i in range(0,len(dmax)):
        #get values on opposite sides of the maximum
        y1 = x[tmin[i]-1]
        y2 = x[tmin[i]]
        y3 = x[tmin[i]+1]
        A = []
        #setup a solve linear equation for coefficients of parabola
        for j in range(0,3):
            A.append([(tmin[i]-1)**2,tmin[i],1])
        A = np.array(A)
        b = np.array([x[tmin[i]-1],x[tmin[i]],x[tmin[i]+1]])
        maxcoeff[i] = np.linalg.solve(A,b)
        
    #use t = -b/2a to get values of parabolic maxes  
    
    pMax = np.zeros(len(dmax),2)
    pMin = np.zeros(len(dmin),2)
    
    for i in range(0,len(dmax)):
        [amin,bmin,cmin] = [mincoeff[i,0],mincoeff[i,1],mincoeff[i,2]]
        [amax,bmax,cmax] = [maxcoeff[i,0],maxcoeff[i,1],maxcoeff[i,2]]
        
        [pMin[i,0],pMin[i,1]] = [-bmin/(2*amin),-((bmin**2)/(4*amin))+cmin]
        [pMax[i,0],pMax[i,1]] = [-bmax/(2*amax),-((bmax**2)/(4*amax))+cmax]
    """
    We have the parabolic minimums and maximums and their locations, we can 
    compare them to the discrete ones later if we'd like
    """
    #these conditionals tell us whether or not we could extrapolate the 
    #beginning and end points as mins or maxs
    if len(dmax) > 0:
        if x[0] >= dmax[0]: 
            pMax.reverse()
            pMax.append(0,x[0])
            pMax.reverse()
        if x[-1] >= dmax[-1]: 
            pMax.append(len(x)-1,x[-1])
        
    if len(dmin) > 0: 
        if x[0] <= dmin[0]: 
            pMin.reverse()
            pMin.append(0,x[0])
            pMin.reverse()
        if x[-1] <= dmin[-1]: 
            pMin.append(len(x)-1,x[-1])
        
    """
    we might need to add two more conditionals for when doing analysis on the 
    residues because they may not have mins and maxs, but the current x(t)
    still needs to have its first and last points extrapolated
    """
    
    return (pMin, pMax)
            

def extrap(x,pMin,pMax):
    """
produces two ghost cells on both side of the signal that contain a min and max
value equal to the first min and max of the signal and the last min and max of 
the signal in order to better extrapolate the first and last points of the signal
"""
      
    #extrapolating beginning of signal
    if pMin[0,0] == 0 and pMax[0,0] == 0 :
        print("First point is both a min or max!") #IMF is zero at the ends
    else:
        pMin.reverse()
        pMin.append(-pMax[0,0],pMin[0,1])
        pMin.reverse()
        pMax.reverse()
        pMax.append(-pMin[0,0],pMax[0,1])
        pMin.reverse()
        
    #extrapolating end of signal
    if pMin[-1,0] == len(x)-1 and pMax[-1,0] == len(x)-1 :
        print("First point is both a min or max!") #IMF is zero at the ends
    else:
        pMin.append(-pMax[-1,0],pMin[-1,1])
        pMax.append(-pMin[-1,0],pMax[-1,1])
        
    return (pMin,pMax)
        
        
    
    
    
    
        
        
            