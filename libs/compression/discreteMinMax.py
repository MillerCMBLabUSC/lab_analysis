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
            top = False
            down = True
        if x[i - 1] == x[i] and x[i] > x[i + 1]:
            if down:
                discreteMin.append([i, x[i]])
            down = False

        # this is to handle the off chance of us sampling to maximums of equal
        # magnitude next to each other
        if x[i - 1] < x[i] and x[i] == x[i + 1]:
            top = True
            down = False
        if x[i - 1] == x[i] and x[i] < x[i + 1]:
            if top:
                discreteMax.append([i, x[i]])
            down = False

    discreteMax = np.array(discreteMax)
    discreteMin = np.array(discreteMin)

    return (discreteMin, discreteMax)
