import numpy as np
import thermo as th
import OpticalElement as opt
import Detector as dt
import propSpectrum as ps
import matplotlib.pyplot as plt
import glob as gb
from scipy import interpolate
import scipy.integrate as intg


# Units and Constants
GHz = 1.e9 # GHz -> Hz
pW = 1.e12 # W -> pW



## Calculates A2 and a2 for optical setup
def f2Model(expDir, writeFile = False):
	channelFile = expDir + "channels.txt"
	cameraFile = expDir + "camera.txt"
	opticsFile = expDir + "opticalChain.txt"
	atmFile = "Atacama_1000um_60deg.txt"

	outFile = expDir + "2f_out.txt"

	hwpIndex = 9




	outString = ""
	outString +=  "bid\tf\t\tHWP_f\ta2 Ave\t\tA2\t\t\tA2\n"
	outString +=  "[]\t[GHz]\t[GHz]\t[]\t\t\t[pW]\t\t[Kcmb]\n"
	outString +=  "-"*40 + "\n"


	for bandID in [1]:#,2]:

		#Imports detector data 
		det = dt.Detector(channelFile, cameraFile, bandID)

		elements = [] #List of optical elements

		#CMB optical element
		elements.append(opt.OpticalElement("CMB", 2.725, 1, 1))
		#Atm optical element
		elements.append(opt.loadAtm(atmFile))
		# Loads elements from Optical Chain file
		elements += opt.loadOpticalChain(opticsFile, det)
		## Detector element
		elements.append(opt.OpticalElement("Detector", .1, 1 - det.det_eff, det.det_eff))


		## Get closest hwp frequency to the band center
		bc = det.band_center/GHz
		posFreqs = [30,40,90,150,220,230,280]
		hwpFreq = reduce(lambda x, y: (x if (abs(x - bc) < abs(y - bc)) else y), posFreqs)
		# Import mueller data file
		muellerDir = "Mueller_AR/"
		muellerFile = muellerDir +  "Mueller_V2_nu%.1f_no3p068_ne3p402_ARcoat_thetain0.0.txt"%(hwpFreq)

		f, r = np.loadtxt(muellerFile, dtype=np.float, unpack=True, usecols=[0, 2])


		#Interpolates a2 from data
		rho = interpolate.interp1d(f, r,kind = "linear")
		x = np.linspace(det.flo, det.fhi, 400)
		y = rho(x)

		#Saves plot of rho (or a2) in bandwidth
		if writeFile:
			plt.plot(x/GHz, y)
			plt.savefig(expDir + "%.1fGHz_a2.pdf"%(det.band_center/GHz))
			plt.clf()

		# Gets average a2 value
		a2Ave = intg.simps(y, x=x)/(det.fhi - det.flo)

		#Inserts HWP at hwpIndex
		elements.insert(hwpIndex, opt.OpticalElement("HWP", elements[hwpIndex - 1].temp, 0, 1))


		pW_per_Kcmb = th.dPdT(elements, det)*pW


		freqs, UPspecs, _, _ = ps.propSpec(elements, det, hwpIndex)


		effs = lambda f : map(lambda x : x.eff(f), elements[hwpIndex+1:])
		cumEff = lambda f : reduce((lambda x, y: x*y), effs(f))

		# Incident power on the HWP
		hwpInc = UPspecs[hwpIndex]
		detIp = UPspecs[hwpIndex] * rho(freqs) * cumEff(freqs)

		hwpEmis = -th.weightedSpec(freqs,elements[hwpIndex].temp, rho) * cumEff(freqs)

		#2f power at the detector
		det2FPow = detIp + hwpEmis
		#Total A2 (W)
		A2 = np.trapz(det2FPow, freqs)




		outString +=  "%d\t%.1f\t%.1f\t%.2e\t%.3e\t%.3f\n"%(det.bid, det.band_center/GHz, hwpFreq, a2Ave, A2*pW, A2*pW/pW_per_Kcmb)
	print outString

	if writeFile:

		f = open(outFile, 'w')
		f.write(outString)
		f.close()





if __name__=="__main__":
	f2Model("Experiments/V2_dichroic/HF_45cm_3waf_silicon/LargeTelescope/" , True)
	
	# fileDir = "Experiments/V2_dichroic"	
	# expDirs  = [sorted(gb.glob(x+'/*')) for x in sorted(gb.glob(fileDir))]
	
	# for e in expDirs[0]:
	# 	wf = True

	# 	f2Model(e + "/LargeTelescope/", writeFile = wf)
	# 	print  "*"*50 + "\n"

