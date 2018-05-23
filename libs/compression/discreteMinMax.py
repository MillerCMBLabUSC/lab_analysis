"""
x - input signal of real numbers
"""

import numpy as np

def discreteMinMax(x):

    """gets locations of discrete minimums and maximums"""

    # initialize empty lists for storing x and y values for min/max
    top = False
    down = False
    discreteMin = []
    discreteMax = []

    for i in range(1, len(x) - 1):
        if x[i - 1] < x[i] and x[i] > x[i + 1]:  # Maximum
            discreteMax.append([i, x[i]])

        if x[i - 1] > x[i] and x[i] < x[i + 1]:  # Minimum
            discreteMin.append([i, x[i]])

        # this is to handle the off chance of us sampling two minimums of equal
        # magnitude next to each other
        if x[i - 1] > x[i] and x[i] == x[i + 1]:
            mark_min = i
            top = False
            down = True
        if (x[i - 1] == x[i] and x[i] < x[i + 1]):
            if down:
                for j in range(mark_min,i+1):
                    discreteMin.append([j, x[j]])
            if x[i+1] == x[i]:
                down = True
            else:
                down = False

        # this is to handle the off chance of us sampling to maximums of equal
        # magnitude next to each other
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
    #print(discreteMin[:,0])
    discreteMax = np.array(discreteMax)
    discreteMin = np.array(discreteMin)
    #print(discreteMax[:,0])

    return discreteMin, discreteMax

if __name__ == "__main__":
    import test_duplicate
    noise = open('69.txt','r').read().split('\n')[0:100]
    noise = [float(i) for i in noise]
    #noise = np.linspace(0,10,5)
    [d_Min,d_Max] = discreteMinMax(noise)
    [dup_Min,dup_Max] = test_duplicate.test_duplicate(d_Min,d_Max)
    print([d_Min,d_Max])
    print([dup_Min,dup_Max])
