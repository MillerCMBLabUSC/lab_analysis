"""
x - input signal of real numbers
discreteMin - locations of discrete minima
discreteMax - locations of discrete maxima
"""

import numpy as np
import find_duplicates
def interp(x, discreteMin, discreteMax):
    """
    takes as input the locations of the discrete minimums and maximums, interpolates to
    gain a more precise picture of where the mins and maxs are, then outputs those locations
    """

    [tMin, tMax] = [discreteMin[:, 0], discreteMax[:, 0]]
    [tMin_dup, tMax_dup] = find_duplicates.find_duplicates(discreteMin,discreteMax)
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
            [parabolicMin[count + len(tMin),0] , parabolicMin[count + len(tMin),1]] = [i,x[int(i)]] 
            count = count + 1
    
    count = 0
    for i in discreteMax[:,0]:
        if np.isin(i,tMax_dup):
            [parabolicMax[count + len(tMax),0] , parabolicMax[count + len(tMax),1]] = [i,x[int(i)]]
    # these conditionals tell us whether or not we could extrapolate the
    # beginning and end points as mins or maxs
    parabolicMin = np.sort(parabolicMin,axis=0)
    parabolicMax = np.sort(parabolicMax,axis=0)
    return (parabolicMin, parabolicMax) 

if __name__ == "__main__":
    import discreteMinMax
    noise = open('69.txt','r').read().split('\n')[0:100]
    noise = [float(i) for i in noise]
    [discreteMin,discreteMax] = discreteMinMax.discreteMinMax(noise)
    interp(noise,discreteMin,discreteMax)
