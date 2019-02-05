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
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridpsec
import interpolate
import extrapolate
import pickle
import makewav
import wavio
from scipy.interpolate import BarycentricInterpolator 
def reconstruct(x,tmaximas,ymaximas,originalimf):
    """produces new IMFs that are 24-bit ints"""  
    
    signal = x
    signal = [math.floor(i) for i in signal]
    imfs = []
    tarrays = []
    yarrays = []
    parabolicMin = []
    parabolixMax = []
    t = np.linspace(0,len(x)-1,len(x))
    count = 0
    for tarray,yarray in zip(tmaximas[0:-1],ymaximas[0:-1]):
        plt.figure()
        plt.plot(t,signal)
        plt.show()
        tdiff = np.diff(tarray)
        tmin = (np.min(tdiff)/2)        
        yarray = np.array([np.floor(x) for x in yarray])
        if len(yarray) > 1:
            topenv = CubicSpline(tarray,yarray)
        else:
            print('one minima')
            topenv = np.array([ymaxima for x in yarray])
        tminima = tarray - tmin
        yminima = -topenv(tminima)
        yminima = np.array([np.floor(x) for x in yminima])
        parabolicMax = np.stack((tarray,yarray),axis=-1)
        parabolicMin = np.stack((tminima,yminima),axis=-1)
        extrema = np.concatenate((parabolicMin,parabolicMax),axis=0)
        extrema = extrema[extrema[:,0].argsort()]
        #print(extrema)
        reconimf = np.interp(t,extrema[:,0],extrema[:,1])
        reconimf1 = np.array([np.floor(x) for x in reconimf])
        imfs.append(reconimf1)
        signal = signal - reconimf1
        #print(reconimf)
        #print(signal)
        #fig = plt.figure()
        #plt.plot(t,reconimf,t,reconimf1)
        #plt.scatter(extrema[:,0],extrema[:,1])
        #plt.savefig('count%s' %count, dpi=fig.dpi)
        count += 1
            
    imfs.append(signal)
    #print(imfs)
    #print(originalimf)
    reconstructed = np.zeros((len(x),))
    for i in range(len(imfs)):
        fig = plt.figure()
        plt.plot(t,imfs[i],'-',t,originalimf[i],'--')
        plt.savefig('%sth Imf' %i,dpi = fig.dpi)

    for func in imfs: 
       reconstructed =  reconstructed + func
    #print(reconstructed)
    #print(x) 
    return imfs



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
    while iniResidual < inputResidual and osc > 4: # monotone(signal) == False:
        #while the signal has some energy
        iImf = signal
        pSig = np.linalg.norm(signal)**2
        (discreteMin,discreteMax) = discreteMinMax(iImf)
        if len(discreteMin) < 1 and len(discreteMax) < 1:           #if signal has no extrema, you are done
            print('ending...')
            break
        (parabolicMin,parabolicMax) = interpolate.interp(iImf,discreteMin,discreteMax)
        (parabolicMin,parabolicMax) = extrap(iImf,parabolicMin,parabolicMax)
        topenv = CubicSpline(parabolicMax[:,0],parabolicMax[:,1])
        botenv = CubicSpline(parabolicMin[:,0],parabolicMin[:,1])
        mean = (botenv(t) + topenv(t))/2                             #take average of top and bottom of signals
        
        while True:          
            pImf = np.linalg.norm(iImf)**2                           # IMF energy
            pMean = np.linalg.norm(mean)**2                          # Mean energy
            if pMean == 0:
                break
            i  pMean > 0:
                res = 10*np.log10(pImf/pMean)                                   
            if res>resolution:
                break                                                #Resolution reached
            #Resolution not reached, so repeat process
            iImf = iImf - step*mean
            #print(mean)
            (discreteMin,discreteMax) = discreteMinMax(iImf)   
            (parabolicMin,parabolicMin) = interp(iImf, discreteMin, discreteMax) 
            (parabolicMin,parabolicMax) = extrap(iImf,discreteMin,discreteMax)
            #print(parabolicMin)
            #print(parabolicMax)
            topenv = CubicSpline(parabolicMax[:,0],parabolicMax[:,1])
            botenv = CubicSpline(parabolicMin[:,0],parabolicMin[:,1])
            mean = (topenv(t) + botenv(t))/2    
        
            
        textrema.append(parabolicMax[:,0])
        yextrema.append(parabolicMax[:,1])        
        fig = plt.figure()
        plt.plot(t,botenv(t),t,topenv(t),t,iImf,t,mean)
        plt.scatter(parabolicMin[:,0],parabolicMin[:,1])
        plt.scatter(parabolicMax[:,0],parabolicMax[:,1])
        plt.xlabel('time')
        plt.ylabel('Amplitude')
        plt.title('IMF %s' %count)
        plt.savefig('IMF %s' %count, dpi = fig.dpi)
        #iImf = [math.floor(x) for x in iImf]
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
    #yextrema.append(residual)
    imfs = np.array(imfs)                                           #array with imfs and residual in last row
    imfs = imfs.reshape(count-1,int(len(x))) 
    fig = plt.figure()
    plt.plot(t,signal)
    plt.xlabel('time')
    plt.ylabel('Amplitude')
    plt.title('Residual')
    plt.savefig('residual',dpi = fig.dpi)
    recon = np.zeros((siglen,))                                     #create empty reconstruction matrix
    for i in range(len(imfs)):
        recon = recon + imfs[i]                                     #add the IMFs and residual together and plot

    pRecon = np.linalg.norm(recon)**2
    print(10*np.log10(pRecon/pX))
    #print(yextrema)
    #print(iImf)
    for i in range(len(recon)):
        recon[i] = int(round(recon[i]))

    #print(recon)
    print(abs(x-recon))
    np.savetxt('residual.txt',np.array(signal))
    pickle.dump(x,open('samp10.bin','wb'))
    #pickle.dump(residual,open('residual.bin','wb'))
    return textrema,yextrema,imfs

def monotone(residual):
    
    """checks if residual function is monotone"""
    if type(residual) is np.ndarray:
        x = residual
    else:
        x = np.array(residual) 

    dx = np.diff(x)
    
    return np.all(dx <=0) or np.all(dx >= 0)
    

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
    
    if len(dup_Min) > 0 and len(diff_Min) > 1:
        if diff_Min[1] != 1:
            #print(dup_Min)
            #print(diff_Min)
            dup_Min = np.delete(dup_Min,0,0)

    if len(dup_Max) > 0 and len(diff_Max) > 1:
        if diff_Max[1] != 1:
            dup_Max = np.delete(dup_Max,0,0)

    return(dup_Min,dup_Max)


def interp(x, discreteMin, discreteMax):
    
    '''takes as input the locations of the discrete minimums and maximums, interpolates to
    gain a more precise picture of where the mins and maxs are, then outputs those locations
    '''
    #create two separate lists, one that contains all the indices (+1) of the duplicates and one that contains all the non-duplicates
    if len(discreteMin) < 1 or len(discreteMax) < 1: 
        return (discreteMin,discreteMax) 

    [tMin, tMax] = [discreteMin[:, 0], discreteMax[:, 0]]
    [tMin_dup, tMax_dup] = find_duplicates(discreteMin,discreteMax)
    [tMin, tMax] = [list(set(tMin) - set(tMin_dup)), list(set(tMax) - set(tMax_dup))]
    [mincoeff, maxcoeff] = [[], []]
 
    if len(tMin) < 1 or len(tMax) < 1:
        return (discreteMin,discreteMax)

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
            parabolicMin[count + len(tMin),0] = i
            parabolicMin[count + len(tMin),1] = x[int(i)]
            count = count + 1

    count = 0
    for i in discreteMax[:,0]:
        if np.isin(i,tMax_dup):
            parabolicMax[count + len(tMax),0] = i
            parabolicMax[count + len(tMax),1] = x[int(i)]
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
    begin_max = False
    begin_min = False
    end_min = False
    end_max = False    
    
    if len(discreteMin) == 0 or len(discreteMax) == 0:
        return (discreteMin, discreteMax)
 
    if len(discreteMax) > 0:
        if x[0] >= discreteMax[0,1]:
            begin_max = True
#           print('first point is maximum')
            discreteMax = np.flip(discreteMax,0); 
            discreteMax = np.append(discreteMax,[[0,x[0]]],axis=0);
            discreteMax = np.flip(discreteMax,0)
        if x[-1] >= discreteMax[-1,1]:
            end_max = True 
#            print('end point is maximum')
            discreteMax= np.append(discreteMax,[[len(x)-1,x[-1]]],axis=0)   

    if len(discreteMin) > 0:                      
        if x[0] <= discreteMin[0,1]:
#            print('first point is minimum')
            begin_min = True
            discreteMin = np.flip(discreteMin,0); 
            discreteMin = np.append(discreteMin,[[0,x[0]]],axis=0);
            discreteMin = np.flip(discreteMin,0)
            
        if x[-1] <= discreteMin[-1,1]:
#           print('end point is minimum')
            end_min = True
            discreteMin= np.append(discreteMin,[[len(x)-1,x[-1]]],axis=0)  

    #elif len(discreteMin) == 0 or len(discreteMax) == 0:
    #    return (discreteMin, discreteMax)
 
    #else:
    #    return (discreteMin, discreteMax)        
    #extrapolating beginning of signal
    
    if discreteMin[0, 0] == 0 and discreteMax[0, 0] == 0:
        print("First point is both a min and max!")  # IMF is zero at the ends
    #if begin_max == True: #if first point is a maximum, create ghost point with second maximum
    #    reflectedMin = [-discreteMax[1, 0], discreteMin[0, 1]]
    #    discreteMin = np.flip(discreteMin, 0)
    #    discreteMin = np.append(discreteMin, [reflectedMin], axis=0)
    #    discreteMin = np.flip(discreteMin, 0)
    else: #otherwise, create ghost point with first maximum
        reflectedMin = [-discreteMax[0, 0], discreteMin[0, 1]]
        discreteMin = np.flip(discreteMin, 0)
        discreteMin = np.append(discreteMin, [reflectedMin], axis=0)
        discreteMin = np.flip(discreteMin, 0)
    #if begin_min == True: #here, discreteMin has already increased in size so we have to increase
                          #all indicies of discreteMin by 1
    #    reflectedMax = [-discreteMin[2, 0], discreteMax[0, 1]]
    #    discreteMax = np.flip(discreteMax, 0)
    #    discreteMax = np.append(discreteMax, [reflectedMax], axis=0)
    #    discreteMax = np.flip(discreteMax, 0)
    #else:
        reflectedMax = [-discreteMin[1, 0], discreteMax[0, 1]]
        discreteMax = np.flip(discreteMax, 0)
        discreteMax = np.append(discreteMax, [reflectedMax], axis=0)
        discreteMax = np.flip(discreteMax, 0)   
        
    #extrapolating end of signal
    if discreteMin[-1, 0] == len(x) - 1 and discreteMax[-1, 0] == len(x) - 1:
        print("First point is both a min and  max!")  # IMF is zero at the ends
    #we add a ghost point to the end of the discreteMin first, and then do the same to
    #discreteMax, accounting for the change in discreteMin
    #if end_max == True:
    #    discreteMin = np.append(discreteMin, [[2 * (len(x) - 1) - discreteMax[-2, 0], discreteMin[-1, 1]]], axis=0)
    else:
        discreteMin = np.append(discreteMin, [[2 * (len(x) - 1) - discreteMax[-1,0], discreteMin[-1,1]]], axis = 0)
    #if end_min == True and end_max == False:
    #    discreteMax = np.append(discreteMax, [[2 * (len(x) - 1) - discreteMin[-3, 0], discreteMax[-1, 1]]], axis=0)
    #else:
        discreteMax = np.append(discreteMax, [[2 * (len(x) - 1) - discreteMin[-2, 0], discreteMax[-1, 1]]], axis=0)      

    return (discreteMin,discreteMax)

if __name__ == "__main__":
#    from lab_analysis.libs.noise import simulate
    import scipy.io as io
    import simulate
    import makewav
    import numpy as np
    from scipy.signal import hilbert
    
    alpha = 1.0
    white_noise_sigma = 1
    length_ts = 600
    t = np.linspace(0, length_ts - 1, length_ts)
    f_knee = 2.0
    sample_rate = 100.0
    #scalednoise = simulate.simulate_noise(alpha, white_noise_sigma,length_ts, f_knee, sample_rate)
    #scalednoisee = makewav.floatToint24(scalednoise)
    '''
    for i in range(100):
        try:
            data = np.load('timestream%s.npy' %i)[:1400]
            vec = splineEMD(data,20,10,1)
            io.savemat('r%s.mat' %i, {'residual': vec[2][-1], 'signal': data})
        except:
            pass
    '''
    data = np.load('timestream18.npy')[:1400]
    
    #data = ts['y']
    
    vec = splineEMD(data,40,10,1)
    for i in range(len(vec[2])):
        io.savemat('imf%s.mat' %i, {'imf%s' %i : vec[2][i]})
    
    io.savemat('signal.mat', {'y': data})
    
    '''
    for i in range(100):
         intnoise = []
         scalednoise = simulate.simulate_noise(alpha, white_noise_sigma,length_ts, f_knee, sample_rate)
         scalednoisee = makewav.floatToint24(scalednoise)
         for k in range(len(scalednoisee)):
             intnoise.append(int(scalednoisee[k]))
         with open('samp%s.txt' %i, 'w') as f:
             for dx in range(len(intnoise)):
                 #f.write(intnoise[dx].to_bytes(4,byteorder='little',signed=True))
                 f.write("%s\n" &item)
  
     
    imf = vec[2][1]
    io.savemat('extrema.mat', {'t' : vec[0][0], 'y' : vec[1][0]})
    io.savemat('residual.mat',{'t' : t, 'y': vec[2][-1]})
    #recon = reconstruct(scalednoise,vec[0],vec[1],vec[2])
    analytical_signal = hilbert(imf)
    amp = np.abs(analytical_signal)
    phase = np.unwrap(np.angle(analytical_signal))
    io.savemat('imf.mat', {'t' : t, 'y' : imf})
    io.savemat('amp1.mat', {'t': t, 'y': amp})
    io.savemat('signal.mat', {'t': t, 'y': scalednoise})
    io.savemat('signal1.mat', {'t': t, 'y': scalednoisee}) 
    wavio.write("signal.wav", scalednoisee, sample_rate, sampwidth=3)
    ''' 
    
    

    
        
        
    
    
    
    
        
        
            
