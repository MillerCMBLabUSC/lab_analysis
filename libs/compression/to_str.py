import numpy as np

def to_str(var):
    if type(var) is list:
        return str(var)[1:-1]
    if type(var) is np.ndarray:
        try:
            return str(list(var[0]))[1:-1]
        except TypeError:
            return str(list(var))[1:-1]
    return str(var)