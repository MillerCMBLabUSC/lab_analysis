import numpy as np
import thermo as th
import OpticalElement as opt
import Detector as dt
import propSpectrum as ps
import matplotlib.pyplot as plt
import glob as gb

#########################################################
#   Input Data 											
#########################################################


def runModel(expDir, bandID, writeFile = False):
	channelFile = expDir + "channels.txt"
	cameraFile = expDir + "camera.txt"
	opticsFile = expDir + "opticalChain.txt"
	atmFile = "Atacama_1000um_60deg.txt"




	# Units and Constants
	GHz = 1.e9 # GHz -> Hz
	pW = 1.e12 # W -> pW

	#Imports detector data 
	det = dt.Detector(channelFile, cameraFile, bandID)

	elements = [] #List of optical elements

	#CMB optical element
	elements.append(opt.OpticalElement("CMB", 2.725, 1, 1))



	#Atmosphere optical element
	fs, ts = np.loadtxt(atmFile, dtype=np.float, unpack=True, usecols=[0, 3]) #frequency/efficiency pairs from input file
	fs*=GHz # [Hz]

	elements.append(opt.OpticalElement("Atm", 273., .0, 0))
	elements[-1].eff = lambda x :  np.interp(x,fs,ts) 
	elements[-1].emis = lambda x : 1 -  np.interp(x,fs,ts) 



	# Loads elements from Optical Chain file
	elements += opt.loadOpticalChain(opticsFile, det)


	#Inserts HWP at desired position
	hwpIndex = 10     #-----SO
	# hwpIndex = 10     #-----Ebex
	# hwpIndex = 3       #-----pb


	elements.insert(hwpIndex, opt.OpticalElement("HWP", elements[hwpIndex - 1].temp, 0, 1))


	## Detector element
	elements.append(opt.OpticalElement("Detector", .1, 1 - det.det_eff, det.det_eff))


	freqs, UPspecs, PPspecs, outPowers =  ps.propSpec(elements, det, hwpIndex)


	incUP = map(lambda x : th.powFromSpec(freqs, x), UPspecs)
	incPP = map(lambda x : 2*th.powFromSpec(freqs, x), PPspecs)


	########################################################
	#  Print table
	########################################################
	print "bandID: %d \t freq: %.2f GHz"%(det.bid, det.band_center/GHz)
	print "Name\t\t\tOutput power(pW)\tIncident UP (pW) \tIncident PP (pW)"
	print "-"*70

	for i in range(len(elements)):
		print "%-8s\t\t%e\t\t%e\t\t%e"%(elements[i].name, outPowers[i]*pW, incUP[i]*pW, incPP[i]*pW)

	print "\nFinal output up:\t%e pW"%(incUP[-1]*pW)
	print "Final output pp:\t%e pW"%(incPP[-1]*pW)

	if writeFile:
		fname = expDir + "%dGHz_opticalPowerTable.txt"%(det.band_center/GHz)
		f = open(fname, 'w')

		f.write( "bandID: %d \t freq: %.2f GHz\n"%(det.bid, det.band_center/GHz))
		f.write( "Name\t\t\tOutput power(pW)\tIncident UP (pW) \tIncident PP (pW)\n")
		f.write( "-"*70 + "\n")

		for i in range(len(elements)):
			f.write( "%-8s\t\t%e\t\t%e\t\t%e\n"%(elements[i].name, outPowers[i]*pW, incUP[i]*pW, incPP[i]*pW))

		f.write( "\nFinal output up:\t%e pW\n"%(incUP[-1]*pW))
		f.write( "Final output pp:\t%e pW"%(incPP[-1]*pW))


		f.close()


if __name__=="__main__":
	runModel("Experiments/V2_dichroic/MF_45cm_3waf_silicon/LargeTelescope/", 1 , False)
	# fileDir = "Experiments/V2_dichroic"
	# expDirs  = [sorted(gb.glob(x+'/*')) for x in sorted(gb.glob(fileDir))]
	
	# for e in expDirs[0]:
	# 	wf = False

	# 	runModel(e + "/LargeTelescope/", 1, writeFile = wf)
	# 	runModel(e + "/LargeTelescope/", 2, writeFile = wf)





	