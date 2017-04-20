import numpy as np

def compute_discrete_derivative(x_vector, y_vector):
    '''
    Approximates the derivative of a function numericall
    '''
    derivative = np.zeros(len(y_vector))
    x_h = x_vector[1] - x_vector[0]
    denominator = 12 * x_h
    denominator = 12 * 1.0
    for i in range(0, len(derivative)):
        if i <= 1:
            np.put(derivative, i, np.nan)
        elif len(derivative) - 3 <= i < len(derivative):
            np.put(derivative, i, derivative[len(derivative) - 4])
        else:
            numerator = -y_vector[i + 2] + 8 * y_vector[i + 1] - 8 * y_vector[i - 1] + y_vector[i - 2]
            derivative_val = numerator / denominator
            np.put(derivative, i, derivative_val)
    np.put(derivative, 0, derivative[2])
    np.put(derivative, 1, derivative[2])
    return derivative

