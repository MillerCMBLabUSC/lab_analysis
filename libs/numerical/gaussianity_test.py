from scipy import stats
import numpy as np


def run_gaussianity_test(input_data, mean=None, sigma=None, verbose=False):
    '''
    This method runs the Komogorov-Smirnov Test on the data pre and post processing to test
    for gaussianity
    '''
    if mean is None:
        mean = np.mean(input_data)
    if sigma is None:
        sigma = np.std(input_data)
    kstest_results = stats.kstest(input_data, 'norm', args=(mean, sigma))
    p_val = kstest_results[1]
    if verbose:
        if p_val < 0.05:
            print '\nFound that the disttribution is not Gaussian\n'
        print
        print mean, sigma, kstest_results
        print
    return kstest_results

if __name__ == '__main__':
    data_vector = stats.norm.rvs(size=1000, loc=20, scale=2)
    mean_ = np.mean(data_vector)
    std_ = np.std(data_vector)
    for i in range(10):
        kstest = stats.kstest(data_vector, 'norm', args=(mean_, std_))
        print kstest

