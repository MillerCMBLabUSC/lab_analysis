# -*- coding: utf-8 -*-
"""
x       - input signal (vector of real numbers)
qResol  - Resolution in dBs
qResid  - Residual energy 
step   - Gradient step size (normally is set to 1, can take values 0-1) 
"""

import numpy as np
from scipy.interpolate import CubicSpline
import math
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt


def splineEMD(x,resolution,inputResidual,step):
    """ produces a spline interpolated minimum and maximum envelope, and does the 
    EMD decomposition until the resolution requirement is met and then until the residual 
    energy is sufficiently small
    """
    
    signal = x                                      #get copy of original signal
    t = np.linspace(0,len(signal)-1,len(signal))                    
    pX = np.linalg.norm(x)**2                              #Original signal energy
    siglen = len(signal)                        #Signal length
    
    #now we are ready to decompose the signal into IMFs
    
    imfs = []                       #empty matrix of IMFs and residue
    iniResidual = 0                 #signal has not been sifted and so energies are equal
    #number = osc(signal)               
    count = 0
    osc = math.inf
    while iniResidual < inputResidual and osc > 4:
        #while the signal has some energy 
        iImf = signal        
        (discreteMin,discreteMax) = discreteMinMax(iImf)
        (parabolicMin,parabolicMax) = interp(iImf,discreteMin,discreteMax)
        (parabolicMin,parabolicMax) = extrap(iImf,parabolicMin,parabolicMax)
        if (abs(len(parabolicMin)-len(parabolicMax)) > 2):
            print('Min/Max count is off')
        topenv = CubicSpline(parabolicMax[:,0],parabolicMax[:,1])    #interpolation function for top envelope
        botenv = CubicSpline(parabolicMin[:,0],parabolicMin[:,1])    #interpolation function for bottom envelope
        osc = len(discreteMax) + len(discreteMin)
        mean = (topenv(t) + botenv(t))/2                                              #take average of top and bottom signals
        while True:
            pImf = np.linalg.norm(iImf)**2                                      # IMF energy
            pMean = np.linalg.norm(mean)**2                                     # Mean energy
            if pMean > 0:
                res = 10*np.log10(pImf/pMean)                   
            if res>resolution:
                break                   #Resolution reached
            #Resolution not reached
            iImf = iImf - step*mean
            (discreteMin,discreteMax) = discreteMinMax(iImf)
            (parabolicMin,parabolicMax) = interp(iImf,discreteMin,discreteMax)
            (parabolicMin,parabolicMax) = extrap(iImf,discreteMin,discreteMax)
            topenv = CubicSpline(parabolicMax[:,0],parabolicMax[:,1])
            botenv = CubicSpline(parabolicMin[:,0],parabolicMin[:,1])
            mean = (topenv(t) + botenv(t))/2

        plt.figure()
        plt.plot(t,botenv,t,-botenv,t,iImf)
        iImf = np.array(iImf)
        imfs = np.append(imfs,iImf,axis=0)
        count = count + 1
        #store IMF in list
        signal = signal - iImf                                  #subtract IMF from signal
        pSig = np.linalg.norm(signal)**2
        if pSig > 0:
            print(pSig/pX)                                            #if the signal isn't a residual, calculate the power of the residual
            iniResidual = 10*np.log10(pX/pSig)
        else:
            iniResidual = math.inf      
    if pSig/pX > 0: #or some really small positive number (might change later)
        #print('residual')
        residual = signal
        imfs = np.append(imfs, np.array(residual),axis=0)
        count = count + 1
    imfs = np.array(imfs) #array with imfs and residual in last row
    imfs = imfs.reshape(count,int(len(x)))
    
    recon = np.zeros((100,))            #create empty reconstructed matrix
    for i in range(len(imfs)):
        recon = recon + imfs[i]         #add the Imfs and residual together
        #plt.plot(t,imfs[i])
        
    #plt.figure()
    #plt.plot(t,recon-x)                 #plot the difference between the reconstructed signal minus the input signal
    #plt.show()

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
    
    return (discreteMin,discreteMax)

def interp(x,discreteMin,discreteMax):
    """
    takes as input the locations of the discrete minimums and maximums, interpolates to 
    gain a more precise picture of where the mins and maxs are, then outputs those locations
    """
       
    [tMin,tMax] = [discreteMin[:,0],discreteMax[:,0]]
        
    [mincoeff,maxcoeff] = [[],[]]
    #get parabolic mins
    lengths = []
    for i in tMin:
        lengths.append(i)
        #get values on opposite sides of the minimum
        [y1,y2,y3] = [x[int(i)-1],x[int(i)],x[int(i)+1]]
        A = []; 
        #setup a solve linear equation for coefficients of parabola
        A.append([(i-1)**2,i-1,1])
        A.append([i**2,i,1])
        A.append([(i+1)**2,i+1,1])
        A = np.array(A); b = np.array([y1,y2,y3]); mincoeff.append(np.linalg.solve(A,b))
        #print(len(mincoeff),len(lengths))
    mincoeff = np.vstack([mincoeff[0:len(mincoeff)]])
    
    
    #get parabolic maxs
    lengths = []
    for i in tMax:
        lengths.append(i)
        #get values on opposite sides of the maximum
        [y1,y2,y3] = [x[int(i)-1],x[int(i)],x[int(i)+1]]
        A = []; 
        #setup a solve linear equation for coefficients of parabola
        A.append([(i-1)**2,i-1,1])
        A.append([(i)**2,i,1])
        A.append([(i+1)**2,i+1,1])
        A = np.array(A); b = np.array([y1,y2,y3]); maxcoeff.append(np.linalg.solve(A,b))
    maxcoeff = np.vstack([maxcoeff[0:len(maxcoeff)]])

    parabolicMax = np.zeros([len(discreteMax),2]); parabolicMin = np.zeros([len(discreteMin),2])
    #use t = -b/2a to get values of parabolic maxes 
    for i in range(len(mincoeff)):
        #m denotes minimum coefficient and upper case M denotes maximum coefficient
        [am,bm,cm] = [mincoeff[i,0],mincoeff[i,1],mincoeff[i,2]]
        [parabolicMin[i,0],parabolicMin[i,1]] = [-bm/(2*am),-((bm**2)/(4*am))+cm]
    for i in range(len(maxcoeff)):
        #M denotes maximum coefficient
        [aM,bM,cM] = [maxcoeff[i,0],maxcoeff[i,1],maxcoeff[i,2]]
        [parabolicMax[i,0],parabolicMax[i,1]] = [-bM/(2*aM),-((bM**2)/(4*aM))+cM]
        
    #these conditionals tell us whether or not we could extrapolate the 
    #beginning and end points as mins or maxs
    
    return (parabolicMin, parabolicMax)
            

def extrap(x,discreteMin,discreteMax):
    """
    produces two ghost cells on both side of the signal that contain a min and max
    value equal to the first min and max of the signal and the last min and max of 
    the signal in order to better extrapolate the first and last points of the signal
    """
    
    if len(discreteMax) > 0:
        if x[0] >= discreteMax[0,1]:
            #print('first point is maximum')
            discreteMax = np.flip(discreteMax,0); 
            discreteMax = np.append(discreteMax,[[0,x[0]]],axis=0);
            discreteMax = np.flip(discreteMax,0)
        if x[-1] >= discreteMax[-1,1]: 
            #print('end point is maximum')
            discreteMax= np.append(discreteMax,[[len(x)-1,x[-1]]],axis=0)   
                           
    if len(discreteMin) > 0: 
        if x[0] <= discreteMin[0,1]:
            #print('first point is minimum')
            discreteMin = np.flip(discreteMin,0); 
            discreteMin = np.append(discreteMin,[[0,x[0]]],axis=0);
            discreteMin = np.flip(discreteMin,0)
            #print(discreteMin)
        if x[-1] <= discreteMin[-1,1]:
            #print('end point is maximum')
            discreteMin= np.append(discreteMin,[[len(x)-1,x[-1]]],axis=0)  
            
    #extrapolating beginning of signal
    
    if discreteMin[0,0] == 0 and discreteMax[0,0] == 0 :
        print("First point is both a min or max!") #IMF is zero at the ends
    else:
        reflectedMin = [-discreteMax[0,0],discreteMin[0,1]]
        discreteMin = np.flip(discreteMin,0)
        discreteMin = np.append(discreteMin,[reflectedMin],axis=0)
        discreteMin = np.flip(discreteMin,0)
        
        reflectedMax = [-discreteMin[1,0],discreteMax[0,1]]
        discreteMax = np.flip(discreteMax,0)
        discreteMax = np.append(discreteMax,[reflectedMax],axis=0)
        discreteMax = np.flip(discreteMax,0)
        
        
    #extrapolating end of signal
    if discreteMin[-1,0] == len(x)-1 and discreteMax[-1,0] == len(x)-1 :
        print("First point is both a min or max!") #IMF is zero at the ends
    else:
        discreteMin = np.append(discreteMin,[[2*(len(x) - 1) - discreteMax[-1,0],discreteMin[-1,1]]],axis=0)
        discreteMax = np.append(discreteMax,[[2*(len(x) - 1) - discreteMin[-2,0],discreteMax[-1,1]]],axis=0)
            
    return (discreteMin,discreteMax)

if __name__ == "__main__":
    from lab_analysis.libs.noise import simulate
    alpha = 1.0
    white_noise_sigma = 1.0
    length_ts = 500
    f_knee = 2.0
    sample_rate = 100.0
    noise = simulate.simulate_noise(alpha, white_noise_sigma,length_ts, f_knee, sample_rate)
    vec = splineEMD(noise,50,40,1)
    


    
    

    
        
        
    
    
    
    
        
        
            