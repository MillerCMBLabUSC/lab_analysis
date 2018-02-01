#! /usr/bin/env python3
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt

import numpy as np
from lab_analysis.libs.noise import simulate
import sys


alpha = 1.0
white_noise_sigma = 1.0
f_knee = 2.0
sample_rate = 100.0

class Correlate:

	def __init__(self,correlations,original):
		#create noise sample that is a union of all to be correlated samples
		self.noise = (simulate.simulate_noise(alpha,white_noise_sigma,original + correlations + 1,f_knee,sample_rate))
		self.correlations = correlations
		self.orig = original
		self.copies = []
		self.correlation = None

	def fcorrelate(self):
		"""This function correlates a 1/f timestream forward in time by 1 second"""


		self.correlation = 'Foward' # set correlation

		#create a cover of extended noise sample
		for i in range(0,self.correlations):
			self.copies.append(self.noise[i:i+self.orig])

		#flatten the list of lists
		self.copies = [item for sublist in self.copies for item in sublist]


	def bcorrelate(self):
		"""This function correlates a 1/f time stream backward in time by 1 second"""


		self.correlation = 'Backward' #set correlation

		#create a cover of extended the extended noise sample
		for i in range(0,self.correlations):
			self.copies.append(self.noise[-(i+self.orig):-i])

		#flatten the lists of lists
		self.copies = [item for sublist in self.copies for item in sublist]





