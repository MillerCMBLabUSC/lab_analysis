# -*- coding: utf-8 -*-
"""
x       - input signal (vector of real numbers)
resolution  - Resolution in dBs
inputResidual  - Residual energy
step   - Gradient step size (normally is set to 1, can take values 0-1) 
"""

import numpy as np
from scipy.interpolate import CubicSpline
from scipy.interpolate import interp1d
import math
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridpsec



def splineEMD(x,resolution,inputResidual,step):
    """ produces a spline interpolated minimum and maximum envelope, and does the 
    EMD decomposition until the resolution requirement is met and then until the residual 
    is close enough to the original signal energy
    """
    
    signal = x                                                       #get copy of original signal
    t = np.linspace(0,len(signal)-1,len(signal))                    
    pX = np.linalg.norm(x)**2                                        #Original signal energy
    siglen = len(signal)                                             #Signal length
    #now we are ready to decompose the signal into IMFs

    imfs = []                                                        #empty matrix of IMFs and residue
    iniResidual = 0                                                #signal has not been sifted and so energies are equal
    count = 1
    osc = math.inf
    textrema = []
    yextrema = []
    #plt.figure()
    #plt.plot(t,signal)
    #plt.xlabel('time')
    #plt.ylabel('Amplitude')
    #plt.title('Original signal')
    #plt.show()
    while iniResidual < inputResidual and osc > 4:
        #while the signal has some energy
        iImf = signal
        pSig = np.linalg.norm(signal)**2
        (discreteMin,discreteMax) = discreteMinMax(iImf)
        if len(discreteMin) < 2 or len(discreteMax) < 2:           #if signal has no extrema, you are done
            break
        (parabolicMin,parabolicMax) = interp(iImf,discreteMin,discreteMax)
        (parabolicMin,parabolicMax) = extrap(iImf,parabolicMin,parabolicMax)
        if (abs(len(parabolicMin)-len(parabolicMax)) > 2):
            print('Min/Max count is off')
        #print(parabolicMin)  
        #print(parabolicMax)  
        topenv = interp1d(parabolicMax[:,0],parabolicMax[:,1],kind = 'slinear')    #interpolation function for top envelope
        botenv = interp1d(parabolicMin[:,0],parabolicMin[:,1],kind = 'slinear')    #interpolation function for bottom envelope
        osc = len(discreteMax) + len(discreteMin)
        mean = (topenv(t) + botenv(t))/2                             #take average of top and bottom signals
        while True:
            pImf = np.linalg.norm(iImf)**2                           # IMF energy
            pMean = np.linalg.norm(mean)**2                          # Mean energy
            if pMean > 0:
                res = 10*np.log10(pImf/pMean)                   
            if res>resolution:
                break                                                #Resolution reached
            #Resolution not reached, so repeat process
            iImf = iImf - step*mean
            (discreteMin,discreteMax) = discreteMinMax(iImf)
            discreteMin = np.around(discreteMin,3)
            discreteMax = np.around(discreteMax,3)
            (parabolicMin,parabolicMax) = interp(iImf,discreteMin,discreteMax)
            (parabolicMin,parabolicMax) = extrap(iImf,discreteMin,discreteMax)
            #print(parabolicMax)
            #print(parabolicMin)
            topenv = interp1d(parabolicMax[:,0],parabolicMax[:,1],kind = 'slinear')
            botenv = interp1d(parabolicMin[:,0],parabolicMin[:,1],kind = 'slinear')
            mean = (topenv(t) + botenv(t))/2
        textrema.append(discreteMax[:,0])
        yextrema.append(discreteMax[:,1])
        #plt.figure()
        #plt.plot(t,botenv(t),t,-botenv(t),t,iImf,t,mean)
        #plt.scatter(parabolicMin[:,0],parabolicMin[:,1])
        #plt.scatter(parabolicMax[:,0],parabolicMax[:,1])
        #plt.xlabel('time')
        #plt.ylabel('Amplitude')
        #plt.title('IMF %s' %count)
        #plt.show()
        iImf = np.array(iImf)
        imfs = np.append(imfs,iImf,axis=0)                           #store IMF in list
        count = count + 1
        signal = signal - iImf                                       #subtract IMF from signal
        pSig = np.linalg.norm(signal)**2
        osc = len(discreteMax) + len(discreteMin)
        if pSig > 0:
            #print(10*np.log10(pX/pSig))                         #if the signal isn't a residual, calculate the power of the residual
            iniResidual = 10*np.log10(pX/pSig)
        else:
            iniResidual = math.inf
    if pSig/pX > 0:                                           #or some really small positive number (might change later)
        residual = signal
        imfs = np.append(imfs, np.array(residual),axis=0)
        count = count + 1
    imfs = np.array(imfs)                                           #array with imfs and residual in last row
    imfs = imfs.reshape(count-1,int(len(x)))
    #extrema.append(discreteMax)
    #plt.figure()
    #plt.plot(t,residual)
    #plt.xlabel('time')
    #plt.ylabel('Amplitude')
    #plt.title('Residual')
    #plt.show()
    recon = np.zeros((siglen,))                                     #create empty reconstruction matrix
    for i in range(len(imfs)):
        recon = recon + imfs[i]                                     #add the IMFs and residual together and plot

    pRecon = np.linalg.norm(recon)**2
    #print(10*np.log10(pRecon/pX))
    #print(yextrema)
    #print(x)
    return textrema,yextrema
   

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
            
        '''this is to handle the off chance of us sampling several minimums of equal 
        magnitude next to each other'''
        
        #begin by marking the index of a repeated minimum and set down to True
        if x[i - 1] > x[i] and x[i] == x[i + 1]:
            mark_min = i
            top = False #top denotes a maximum
            down = True #down denotes a minimum

        #now, this block is for every index after the marked index that is repeated. 
        #check when the segment ends, then append each element to the minima list
        if (x[i - 1] == x[i] and x[i] < x[i + 1]):
            if down:
                for j in range(mark_min,i+1):
                    discreteMin.append([j, x[j]])
            if x[i+1] == x[i]:
                down = True
            else:
                down = False    
                             
        #this is to handle the off chance of us sampling several maximums of equal
        #magnitude next to each other
        if x[i - 1] < x[i] and x[i] == x[i + 1]:
            mark_max = i
            top = True
            down = False
        if x[i - 1] == x[i] and x[i] > x[i + 1]:
            if top:
                for k in range(mark_max,i+1):
                    discreteMax.append([k, x[k]])
            if x[i+1] == x[i]:
                top = True
            else:
                top = False

    discreteMax = np.array(discreteMax)
    discreteMin = np.array(discreteMin)
    #print(discreteMax)
    #print(discreteMin)    
    return (discreteMin,discreteMax)

def find_duplicates(discreteMin,discreteMax):

    '''This code finds the indices of the duplicated elements in discreteMin and discreteMax'''
    
    #find the difference between time values of dMin and dMax as a marker for repeated extrema
    diff_Min = np.diff(discreteMin[:,0])
    diff_Max = np.diff(discreteMax[:,0])
    #insert the first element of dMin and dMax to make the lengths of the two lists the same
    #(we will delete it later if it's not a repeated extrema)
    diff_Min = np.insert(diff_Min,0,discreteMin[:,0][0])
    diff_Max = np.insert(diff_Max,0,discreteMax[:,0][0])
    dup_Min = []
    dup_Max = []
    #print(len(diff_Min))
    #print(len(discreteMin))
    for i in range(len(discreteMin)):
        if i == len(discreteMin) - 1:
            if discreteMin[:,0][i] == discreteMin[:,0][i-1]:
                dup_Min = np.append(dup_Min,discreteMin[:,0][int(i)])
            break

        if diff_Min[i] == 1 and int(i-1) > 0:
            dup_Min = np.append(dup_Min,discreteMin[:,0][int(i)])
            if diff_Min[i-1] != 1:
                dup_Min = np.append(dup_Min,discreteMin[:,0][int(i-1)])

    for i in range(len(discreteMax)):
        if i == len(discreteMax) - 1:
            if discreteMax[:,0][i] == discreteMax[:,0][i-1]:
                dup_Max = np.append(dup_Max,discreteMax[:,0][int(i)])
            break

        if diff_Max[i] == 1 and int(i-1) > 0:
            dup_Max = np.append(dup_Max,discreteMax[:,0][int(i)])
            if diff_Max[i-1] != 1:
                dup_Max = np.append(dup_Max,discreteMax[:,0][int(i-1)])
    
    if diff_Min[1] != 1 and len(dup_Min) > 2 and len(diff_Min) > 1:
        #print(dup_Min)
        #print(diff_Min)
        dup_Min = np.delete(dup_Min,0,0)

    if diff_Max[1] != 1 and len(dup_Max) > 2 and len(diff_Max) > 1:
       
        dup_Max = np.delete(dup_Max,0,0)

    return(dup_Min,dup_Max)


def interp(x, discreteMin, discreteMax):
    
    '''takes as input the locations of the discrete minimums and maximums, interpolates to
    gain a more precise picture of where the mins and maxs are, then outputs those locations
    '''
     
    [tMin, tMax] = [discreteMin[:, 0], discreteMax[:, 0]]
    [tMin_dup, tMax_dup] = find_duplicates(discreteMin,discreteMax)
    [tMin, tMax] = [list(set(tMin) - set(tMin_dup)), list(set(tMax) - set(tMax_dup))]
    #print(discreteMin[:,0])
    #print(tMin_dup)
    #print(tMin)
    [mincoeff, maxcoeff] = [[], []]
    # get parabolic mins
    lengths = []
    for i in tMin:
        lengths.append(i)
        # get values on opposite sides of the minimum
        [y1, y2, y3] = [x[int(i) - 1], x[int(i)], x[int(i) + 1]]
        A = [];
        # setup a solve linear equation for coefficients of parabola
        A.append([(i - 1) ** 2, i - 1, 1])
        A.append([i ** 2, i, 1])
        A.append([(i + 1) ** 2, i + 1, 1])
        A = np.array(A);
        b = np.array([y1, y2, y3]);
        mincoeff.append(np.linalg.solve(A, b))
        # print(len(mincoeff),len(lengths))
    #print(mincoeff)
    mincoeff = np.vstack([mincoeff[0:len(mincoeff)]])

    # get parabolic maxs
    lengths = []
    for i in tMax:
        lengths.append(i)
        # get values on opposite sides of the maximum
        [y1, y2, y3] = [x[int(i) - 1], x[int(i)], x[int(i) + 1]]
        A = [];
        # setup a solve linear equation for coefficients of parabola
        A.append([(i - 1) ** 2, i - 1, 1])
        A.append([(i) ** 2, i, 1])
        A.append([(i + 1) ** 2, i + 1, 1])
        A = np.array(A);
        b = np.array([y1, y2, y3]);
        maxcoeff.append(np.linalg.solve(A, b))
    #print(maxcoeff)
    maxcoeff = np.vstack([maxcoeff[0:len(maxcoeff)]])

    parabolicMax = np.zeros([len(discreteMax), 2]);
    parabolicMin = np.zeros([len(discreteMin), 2])
    # use t = -b/2a to get values of parabolic maxes
    for i in range(len(mincoeff)):
        # m denotes minimum coefficient and upper case M denotes maximum coefficient
        [am, bm, cm] = [mincoeff[i, 0], mincoeff[i, 1], mincoeff[i, 2]]
        [parabolicMin[i, 0], parabolicMin[i, 1]] = [-bm / (2 * am), -((bm ** 2) / (4 * am)) + cm]
    for i in range(len(maxcoeff)):
        # M denotes maximum coefficient
        [aM, bM, cM] = [maxcoeff[i, 0], maxcoeff[i, 1], maxcoeff[i, 2]]
        [parabolicMax[i, 0], parabolicMax[i, 1]] = [-bM / (2 * aM), -((bM ** 2) / (4 * aM)) + cM]

    count = 0
    for i in discreteMin[:,0]:
        if np.isin(i,tMin_dup):
            [parabolicMin[count + len(tMin),0] , parabolicMin[count + len(tMin),1]] = [i,x[int(i)]]
            count = count + 1

    count = 0
    for i in discreteMax[:,0]:
        if np.isin(i,tMax_dup):
            [parabolicMax[count + len(tMax),0] , parabolicMax[count + len(tMax),1]] = [i,x[int(i)]]
            count = count + 1
    parabolicMin = np.sort(parabolicMin,axis=0)
    parabolicMax = np.sort(parabolicMax,axis=0)
    # these conditionals tell us whether or not we could extrapolate the
    # beginning and end points as mins or maxs
 
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
    #from lab_analysis.libs.noise import simulate
    alpha = 1.0
    white_noise_sigma = 1.0
    length_ts = 50
    f_knee = 2.0
    sample_rate = 100.0
    noise = open('69.txt','r').read().split('\n')[0:50]
    noise = [float(i) for i in noise]
    #noise = simulate.simulate_noise(alpha, white_noise_sigma,length_ts, f_knee, sample_rate)
    vec = splineEMD(noise,30,10,1)
    


    
    

    
        
        
    
    
    
    
        
        
            
