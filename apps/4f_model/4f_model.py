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


# Units and Constants
GHz = 1.e9 # GHz -> Hz
pW = 1.e12 # W -> pW



def geta2(elements, det):
    a2tot = 0
    for e in elements:
        if (e.name == "HWP"):
            break
        if (e.Ip(det.band_center) != 0):

#            print "%s: %.3f %%"%(e.name, abs(e.Ip(det.band_center))*100)
            a2tot += abs(e.Ip(det.band_center))

    print "-"*20
    print "Total a4: %.3f %%\n"%(a2tot * 100)

def runModel(expDir, bandID, hwpIndex = 9, lensIP = .0004, theta =  0.1308, writeFile = False):
    """ Gets A4 for specified experiment
    
    Parameters
    -------
    expDir : string
        Path to folder containing `channels.txt`, `camera.txt`, and `opticalChain.txt.`
    bandID : int (1 or 2)
        Frequency number for specified experiment
    hwpIndex : int
        Index for HWP to be placed at
    lensIP : float
        IP of lenses in telescope
    theta : float [rad]
        Incident angle (Small aperture)
    writeFile : bool
        If optical power file should be printed
        
    Returns
    --------
    det : Detector
        Detector object used for experiment
    elements : list of OpticalElements
        Optical chain created for experiment
    powOnDetector : float [pW]
        Polarized Power incident on detector
    powCMB : float [Kcmb]
        Equivalent power in Kcmb at the start of the telescope
    """
    channelFile = expDir + "channels.txt"
    cameraFile = expDir + "camera.txt"
    opticsFile = expDir + "opticalChain.txt"
    atmFile = "Atacama_1000um_60deg.txt"


    outputString = ""

    #Imports detector data 
    det = dt.Detector(channelFile, cameraFile, bandID)


    """
        CREATES OPTICAL CHAIN
    """
    
    elements = [] #List of optical elements

    #CMB Element
    e = opt.OpticalElement()
    e.load("CMB", 2.725, 1)
    elements.append(e)
    
    #Atmosphere Element
    e = opt.OpticalElement()
    e.loadAtm(atmFile, det)
    elements.append(e)


    #Telescope elements
    elements += opt.loadOpticalChain(opticsFile, det, lensIP = lensIP, theta=theta)

    #Detector Element
    e = opt.OpticalElement()
    e.load("Detector", det.bath_temp, 1 - det.det_eff)
    elements.append(e) 

    #Gets HWP index
            
    try:
        hwpIndex = [e.name for e in elements].index("HWP")
    except:
        e = opt.OpticalElement()
        e.load("HWP", elements[hwpIndex - 1].temp, 0)
        elements.insert(hwpIndex, e)

    #Inserts HWP at desired position
    # hwpIndex = 9      #-----SO
    # hwpIndex = 10        #-----Ebex
    # hwpIndex = 3         #-----pb
    
    freqs, UPspecs, UPout, PPout = ps.A4Prop(elements, det ,hwpIndex)

    incPow = map(lambda x : th.powFromSpec(freqs, x), UPspecs)

    pW_per_Kcmb = th.dPdT(elements, det)*pW
    effs = [e.Eff(det.band_center) for e in elements[1:]]
    print effs
    cumEff = reduce(lambda x, y: x * y, effs)

    #######################################################
    ## Print table
    #######################################################
    outputString +=  "bandID: %d \t freq: %.2f GHz\n"%(det.bid, det.band_center/GHz)
    outputString +=  "Name\t\t\tIncident UP(pW)\t\tUP Output (pW) \t\tPP Output (pW)\n"
    outputString +=  "-"*70 + "\n"

    for i in range(len(elements)):
        outputString +=  "%-8s\t\t%e\t\t%e\t\t%e\n"%(elements[i].name, incPow[i]*pW, UPout[i]*pW, PPout[i]*pW)

    outputString +=  "\n%e pW / Kcmb\n"%pW_per_Kcmb
    outputString += "Telescope Efficiency: %e"%(cumEff)
    outputString +=  "\nFinal output up:\t%e pW \t %e Kcmb\n"%(sum(UPout)*pW, sum(UPout)*pW / pW_per_Kcmb)
    outputString +=  "Final output pp:\t%e pW \t %e Kcmb\n" %(sum(PPout)*pW,  sum(PPout)*pW / pW_per_Kcmb)
    print outputString

    if writeFile:
        fname = expDir + "%dGHz_opticalPowerTable.txt"%(det.band_center/GHz)
        f = open(fname, 'w')
        f.write( outputString)
        f.close()
    return det, elements, sum(PPout)*pW, sum(PPout)*pW/pW_per_Kcmb

def toTeXTable(table, acc = 4):
    out_string = ""
    keys = sorted(table.iterkeys())

    for k in keys:
        out_string += "%.1f & "%k
        for i in table[k]:
            out_string += " " +  ", ".join(map(lambda x : str(round(x,acc)) , i)) + " & "
        out_string += "\\\\ \n"

    return out_string


def runAll(fileDir):
    fileDir = "Experiments/V2_dichroic/45cm"
    expDirs  = [sorted(gb.glob(x+'/*')) for x in sorted(gb.glob(fileDir))]

    ips = [.0004, .00005]
    hwpIndices = [8,9,10]

    wf = False

    tab_pW = {}
    tab_K = {}
    for e in expDirs[0]:
        print "*" * 80 + "\n"
        print e
        print     
        for bid in [1,2]:
            band_entry_pW = [[],[],[]]
            band_entry_K = [[],[],[]]
            for i, hwpi in enumerate(hwpIndices):
                for ip in ips:
                    f, ApW, AK = runModel(e + "/LargeTelehm?scope/", bid, hwpIndex = hwpi, lensIP = ip, writeFile = wf)
                    band_entry_pW[i].append(ApW)
                    band_entry_K[i].append(AK)
            tab_pW[f] = band_entry_pW
            tab_K[f] = band_entry_K


    print toTeXTable(tab_pW, 5)
    print toTeXTable(tab_K, 4)

if __name__=="__main__":
#     runModel("Experiments/Comparisons/ebex/LargeTelescope/", 1, False) #---    Run Ebex Comparison
    #runModel("Experiments/Comparisons/pb", 1, False) #---    Run PB Comparison

    runModel("Experiments/small_aperture/LargeTelescope/", 2, writeFile = False, theta = np.deg2rad(30./2))
#    runModel("Experiments/V2_dichroic/45cm/HF_45cm_3waf_silicon/LargeTelescope/", 1, writeFile = False,  hwpIndex=9 )
#    
#    
#    
#    
#    powEntrance = [[],[]]
#    powerCMB = [[],[]].
#    for theta in map(np.deg2rad, [7.5, 10., 12.5, 15.]):
#         for i in [1,2]:
#             expDir = "Experiments/small_aperture/LargeTelescope/"
#             
#             det, elements, powAtDetector, powCMB = runModel(expDir, i, writeFile = False, theta = theta, hwpIndex = 9)             
#             
#             telEff =  reduce((lambda x, y : x * y), [e.Eff(det.band_center) for e in elements[2:]])
#             
#             powEntrance[i-1] += [powAtDetector / telEff]
#             powerCMB[i-1] += [powCMB]
     
#     
        
     
##    
#     powerEntrance = [[],[]]
#     powerCMB = [[],[]]
#     for hwpi in [8, 9]:
#         for i in [1,2]:
#            
#             expDir = "Experiments/small_aperture/LargeTelescope/"
#             expDir = "Experiments/V2_dichroic/45cm/MF_45cm_3waf_silicon/LargeTelescope/"
#            
#             det, elements, powAtDetector, powCMB = runModel(expDir, i, writeFile = False, hwpIndex = hwpi)
##             geta2(elements, det)
#             print det.band_center
#             
#             telEff =  reduce((lambda x, y : x * y), [e.Eff(det.band_center) for e in elements[2:]])
#
#             
#             powerEntrance[hwpi - 8] += [powAtDetector / telEff]
#             powerCMB[hwpi - 8] += [powCMB]
#
#            
            

 #            
 #            print "band_center: %d:"%(band_center)
 #            print "Power at Det: \t %e pW"%(powAtDetector)
 #            print "Power (pW):\t%e pW" % (powAtDetector/ telEff)
 #            print "Power (Kcmb):\t%e"%powCMB
 #            print ""
            
        



    # runAll("Experiments/V2_dichroic/45cm")





    