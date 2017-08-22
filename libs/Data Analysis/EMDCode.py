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


def splineEMD(x,resolution,inputResidual,step):
    """ produces a spline interpolated minimum and maximum envelope, and does the 
    EMD decomposition until the resolution requirement is met and then until the residual 
    energy is sufficiently small
    """
    
    signal = x                                      #get copy of original signal
    t = np.linspace(0,len(signal)-1,len(signal))                    
    pX = np.norm(x)**2                              #Original signal energy
    siglen = len(signal)                            #Signal length
    
    #now we are ready to decompose the signal into IMFs
    
    imfs = []                       #empty matrix of IMFs and residue
    iniResidual = 0                 #signal has not been sifted and so energies are equal
    #number = osc(signal)               
    
    while iniResidual < inputResidual:    #while the signal has some energy (assuming signal oscillates)
        iImf = signal
        (discreteMin,discreteMax) = discreteMinMax(iImf)
        (parabolicMin,parabolicMax) = extrap(iImf,discreteMin,discreteMax)
        if (abs(len(parabolicMin)-len(parabolicMax)) > 2):
            print('Min/Max count is off')
        topenv = interp1d(parabolicMax[:,0],parabolicMax[:,1], kind='cubic')    #interpolation function for top envelope
        botenv = interp1d(parabolicMin[:,0],parabolicMin[:,1], kind='cubic')    #interpolation function for bottom envelope
        mean = (topenv + botenv)/2                              #take average of top and bottom signals
        while True:
            pImf = np.norm(iImf)**2                             # IMF energy
            pMean = np.norm(mean)**2                            # Mean energy
            if pMean > 0:
                res = 10*np.log10(pImf/pMean)                   
            if res>resolution:
                break                   #Resolution reached
            #Resolution not reached
            iImf = iImf - step*mean(t)
            (discreteMin,discreteMax) = discreteMinMax(iImf)
            (parabolicMin,parabolicMax) = extrap(iImf,discreteMin,discreteMax)
            topenv = interp1d(parabolicMax[:,0],parabolicMax[:,1], kind='cubic')
            botenv = interp1d(parabolicMin[:,0],parabolicMin[:,1], kind='cubic')
            mean = (topenv + botenv)/2
            
        imfs.append([iImf])                                     #store IMF in list
        signal = signal - iImf                                  #subtract IMF from signal
        pSig = np.norm(signal)**2
        if pSig > 0:                         #if the signal isn't a residual, calculate the power of the residual
            iniResidual = 10*np.log10(pX/pSig)
        else:
            iniResidual = math.inf
           
        if pSig/pX > 0: #or some really small positive number (might change later)
            residual = signal
            imfs.append([residual])
    
        imfs = np.array(imfs) #array with imfs and residual in last row
        
    return imfs
   

def discreteMinMax(x):
    

    """gets locations of discrete minimums and maximums"""
 
    #initialize empty lists for storing x and y values for min/max
    top = False
    down = False
    discreteMin = []
    discreteMax = []

    for i in range(1,len(x)-1):
        if x[i-1] < x[i] and x[i] > x[i+1]: #Maximum
            discreteMax.append([i,x[i]])
            
        if x[i-1] > x[i] and x[i] < x[i+1]: #Minimum
            discreteMin.append([i,x[i]])
            
        #this is to handle the off chance of us sampling two minimums of equal 
        #magnitude next to each other
        if x[i-1] > x[i] and x[i] == x[i+1]: 
            top = False 
            down = True
        if x[i-1] == x[i] and x[i] > x[i+1]:
            if down :
                discreteMin.append([i,x[i]])
            down = False
        
        #this is to handle the off chance of us sampling to maximums of equal
        #magnitude next to each other
        if x[i-1] < x[i] and x[i] == x[i+1]:
            top = True
            down = False
        if x[i-1] == x[i] and x[i] < x[i+1]:
            if top:
                discreteMax.append([i,x[i]])
            down = False
        
    discreteMax = np.array(discreteMax)
    discreteMin = np.array(discreteMin)
    
    return (discreteMax,discreteMin)

def interp(x,discreteMax,discreteMin):
    """
    takes as input the locations of the discrete minimums and maximums, interpolates to 
    gain a more precise picture of where the mins and maxs are, then outputs those locations
    """
        
    [tMin,tMax] = [discreteMin[:,0],discreteMin[:,0]]
    
    #get parabolic mins
    for i in range(0,len(discreteMin)):
        #get values on opposite sides of the minimum
        [y1,y2,y3] = x[tMin[i]-1:tMin[i]+1]
        A = []; mincoeff = []
        #setup a solve linear equation for coefficients of parabola
        for j in range(0,3):
            A.append([(tMin[i]-1)**2,tMin[i],1])
        A = np.array(A); b = np.array(y1,y2,y3); mincoeff.append([np.linalg.solve(A,b)])
    
    mincoeff = np.array(mincoeff)
    
    #get parabolic maxs
    for i in range(0,len(discreteMax)):
        #get values on opposite sides of the maximum
        [y1,y2,y3] = x[tMin[i]-1:tMin[i]+1]
        A = []; maxcoeff = []
        #setup a solve linear equation for coefficients of parabola
        for j in range(0,3):
            A.append([(tMax[i]-1)**2,tMax[i],1])
        A = np.array(A); b = np.array(y1,y2,y3); maxcoeff.append([np.linalg.solve(A,b)])
    
    parabolicMax = np.zeros(len(discreteMax),2); parabolicMin = np.zeros(len(discreteMin),2)
    
    for i in range(0,len(discreteMax)):
        #m denotes minimum coefficient and upper case M denotes maximum coefficient
        [am,bm,cm] = [mincoeff[i,0],mincoeff[i,1],mincoeff[i,2]]
        [aM,bM,cM] = [maxcoeff[i,0],maxcoeff[i,1],maxcoeff[i,2]]
        #use t = -b/2a to get values of parabolic maxes  
        [parabolicMin[i,0],parabolicMin[i,1]] = [-bm/(2*am),-((bm**2)/(4*am))+cm]
        [parabolicMax[i,0],parabolicMax[i,1]] = [-bM/(2*aM),-((bM**2)/(4*aM))+cM]
    #these conditionals tell us whether or not we could extrapolate the 
    #beginning and end points as mins or maxs
    if len(discreteMax) > 0:
        if x[0] >= discreteMax[0]: 
            parabolicMax.reverse(); parabolicMax.append(0,x[0]); parabolicMax.reverse()
        if x[-1] >= discreteMax[-1]: 
            parabolicMax.append(len(x)-1,x[-1])
        
    if len(discreteMin) > 0: 
        if x[0] <= discreteMin[0]: 
            parabolicMin.reverse(); parabolicMin.append(0,x[0]); parabolicMin.reverse()
        if x[-1] <= discreteMin[-1]: 
            parabolicMin.append(len(x)-1,x[-1])        
    """
    we might need to add two more conditionals for when doing analysis on the 
    residues because they may not have mins and maxs, but the current x(t)
    still needs to have its first and last points extrapolated
    """   
    return (parabolicMin, parabolicMax)
            

def extrap(x,parabolicMin,parabolicMax):
    """
    produces two ghost cells on both side of the signal that contain a min and max
    value equal to the first min and max of the signal and the last min and max of 
    the signal in order to better extrapolate the first and last points of the signal
    """
      
    #extrapolating beginning of signal
    if parabolicMin[0,0] == 0 and parabolicMax[0,0] == 0 :
        print("First point is both a min or max!") #IMF is zero at the ends
    else:
        parabolicMin.reverse()
        parabolicMin.append(-parabolicMax[0,0],parabolicMin[0,1])
        parabolicMin.reverse()
        parabolicMax.reverse()
        parabolicMax.append(-parabolicMin[0,0],parabolicMax[0,1])
        parabolicMin.reverse()
        
    #extrapolating end of signal
    if parabolicMin[-1,0] == len(x)-1 and parabolicMax[-1,0] == len(x)-1 :
        print("First point is both a min or max!") #IMF is zero at the ends
    else:
        parabolicMin.append(-parabolicMax[-1,0],parabolicMin[-1,1])
        parabolicMax.append(-parabolicMin[-1,0],parabolicMax[-1,1])
        
    return (parabolicMin,parabolicMax)


    
    

    
        
        
    
    
    
    
        
        
            