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

def geta2(elements, det):
	a2tot = 0
	for e in elements:
		if (e.name == "HWP"):
			break
		if (e.Ip(det.band_center) != 0):

			print "%s: %.3f %%"%(e.name, abs(e.Ip(det.band_center))*100)
			a2tot += abs(e.Ip(det.band_center))

	print "-"*20
	print "Total a2: %.3f %%\n"%(a2tot * 100)

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
	e = opt.OpticalElement()
	e.load("CMB", 2.725, 1)
	elements.append(e)


	e = opt.OpticalElement()
	e.loadAtm(atmFile)
	elements.append(e)


	# Loads elements from Optical Chain file
	elements += opt.loadOpticalChain(opticsFile, det)


	e = opt.OpticalElement()
	e.load("Detector", det.bath_temp, 1 - det.det_eff)
	elements.append(e) 


	#Inserts HWP at desired position
	hwpIndex = 9  	#-----SO
	# hwpIndex = 10    	#-----Ebex
	# hwpIndex = 3 		#-----pb

	e = opt.OpticalElement()
	e.load("HWP", elements[-1].temp, 0)
	elements.insert(hwpIndex, e)


	geta2(elements, det)
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

	return det.band_center/GHz, sum(PPout)*pW, sum(PPout)*pW/pW_per_Kcmb

def runAll(fileDir):
	fileDir = "Experiments/V2_dichroic/45cm"
	expDirs  = [sorted(gb.glob(x+'/*')) for x in sorted(gb.glob(fileDir))]
	tab = {}
	for e in expDirs[0]:
		wf = True
		print e
		f, ApW, AK = runModel(e + "/LargeTelescope/", 1, writeFile = wf)
		tab[f] = [ApW, AK]
		f, ApW, AK = runModel(e + "/LargeTelescope/", 2, writeFile = wf)
		tab[f] = [ApW, AK]
		print "*" * 80
	
	keys = sorted(tab.iterkeys())
	print "pW: {" + ", ".join(map(lambda x : "%.5f"%(tab[x][0]), keys)) + "}"
	print "Kcmb: {" + ", ".join(map(lambda x : "%.5f"%(tab[x][1]), keys)) + "}"


if __name__=="__main__":
	# runModel("Experiments/Comparisons/ebex/LargeTelescope/", 1, False) #---	Run Ebex Comparison
	#runModel("Experiments/Comparisons/pb", 1, False) #---	Run PB Comparison

	runModel("Experiments/V2_dichroic/45cm/HF_45cm_3waf_silicon/LargeTelescope/", 1 , False)

	# runAll("Experiments/V2_dichroic/45cm")




	