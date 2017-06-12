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


	outputString = ""

	#Imports detector data 
	det = dt.Detector(channelFile, cameraFile, bandID)

	elements = [] #List of optical elements

	#CMB optical element
	elements.append(opt.OpticalElement("CMB", 2.725, 1, 1))

	#Atm optical element
	elements.append(opt.loadAtm(atmFile))

	# Loads elements from Optical Chain file
	elements += opt.loadOpticalChain(opticsFile, det)

	#Inserts HWP at desired position
	hwpIndex = 8    	#-----SO
	# hwpIndex = 10    	#-----Ebex
	# hwpIndex = 3 		#-----pb


	elements.insert(hwpIndex, opt.OpticalElement("HWP", elements[hwpIndex - 1].temp, 0, 1))


	## Detector element
	elements.append(opt.OpticalElement("Detector", .1, 1 - det.det_eff, det.det_eff))


	freqs, UPspecs, UPout, PPout = ps.A4Prop(elements, det ,hwpIndex)

	incPow = map(lambda x : th.powFromSpec(freqs, x), UPspecs)

	pW_per_Kcmb = th.dPdT(elements, det)*pW


	#######################################################
	## Print table
	#######################################################
	outputString +=  "bandID: %d \t freq: %.2f GHz\n"%(det.bid, det.band_center/GHz)
	outputString +=  "Name\t\t\tIncident UP(pW)\t\tUP Output (pW) \t\tPP Output (pW)\n"
	outputString +=  "-"*70 + "\n"

	for i in range(len(elements)):
		outputString +=  "%-8s\t\t%e\t\t%e\t\t%e\n"%(elements[i].name, incPow[i]*pW, UPout[i]*pW, PPout[i]*pW)

	outputString +=  "\n%e pW / Kcmb\n"%pW_per_Kcmb
	outputString +=  "\nFinal output up:\t%e pW \t %e Kcmb\n"%(sum(UPout)*pW, sum(UPout)*pW / pW_per_Kcmb)
	outputString +=  "Final output pp:\t%e pW \t %e Kcmb\n" %(sum(PPout)*pW,  sum(PPout)*pW / pW_per_Kcmb)

	print outputString

	if writeFile:
		fname = expDir + "%dGHz_opticalPowerTable.txt"%(det.band_center/GHz)
		f = open(fname, 'w')
		f.write( outputString)
		f.close()

	return None


if __name__=="__main__":
	# runModel("Experiments/V2_dichroic/HF_45cm_3waf_silicon/LargeTelescope/", 1 , False)
	fileDir = "Experiments/V2_dichroic/45cm"
	expDirs  = [sorted(gb.glob(x+'/*')) for x in sorted(gb.glob(fileDir))]
	
	for e in expDirs[0]:
		wf = True
		print e
		runModel(e + "/LargeTelescope/", 1, writeFile = wf)
		runModel(e + "/LargeTelescope/", 2, writeFile = wf)
		print "*" * 80





	