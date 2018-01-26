import matplotlib
import matplotlib.pyplot as plt
import numpy as np


#path to arrayfile
path = '~/so/lab_analysis/libs/compression'

filename = np.loadtxt('arrayfile.txt', unpack='False')
length = len(filename)

plt.hist(filename,bins='auto',histtype='bar')
plt.xlabel('compression ratio (%)')
plt.ylabel('blah')
plt.title('Histogram of %a compression ratios'%length)
plt.legend()
plt.show()
