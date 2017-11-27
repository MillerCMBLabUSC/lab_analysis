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
def f2Model(expDir, hwpi = 9,  writeFile = False):
    channelFile = expDir + "channels.txt"
    cameraFile = expDir + "camera.txt"
    opticsFile = expDir + "opticalChain.txt"
    atmFile = "Atacama_1000um_60deg.txt"

    outFile = expDir + "2f_out.txt"



    outString = ""
    outString +=  "bid\tf\tHWP_f\ta2 Ave\t\tA2\t\t\tA2\n"
    outString +=  "[]\t[GHz]\t[GHz]\t[]\t\t[pW]\t\t[Kcmb]\n"
    outString +=  "-"*40 + "\n"

    band_centers = []
    a2s = []
    A2_pW = []
    A2_K = []
    for bandID in [1,2]:

        #Imports detector data 
        det = dt.Detector(channelFile, cameraFile, bandID)

        elements = [] #List of optical elements

        #CMB optical element
        e = opt.OpticalElement()
        e.load("CMB", 2.725, 1)
        elements.append(e)


        e = opt.OpticalElement()
        e.loadAtm(atmFile, det)
        elements.append(e)


        # Loads elements from Optical Chain file
        elements += opt.loadOpticalChain(opticsFile, det)


        e = opt.OpticalElement()
        e.load("Detector", det.bath_temp, 1 - det.det_eff)
        elements.append(e) 



        # Checks if HWP is already in Optical chain. 
        # If not, inserts it at index specified.
        try:
            hwpIndex = [e.name for e in elements].index("WP")
        except ValueError:
            hwpIndex = hwpi
            e = opt.OpticalElement()
            e.load("HWP", elements[-1].temp, 0)
            elements.insert(hwpIndex, e)



        #Inserts HWP at desired position
        # hwpIndex = 9      #-----SO
        # hwpIndex = 10        #-----Ebex
        # hwpIndex = 3         #-----pb



        ## Get closest hwp frequency to the band center
        bc = det.band_center/GHz
        posFreqs = [30,40,90,150,220,230,280]
        hwpFreq = reduce(lambda x, y: (x if (abs(x - bc) < abs(y - bc)) else y), posFreqs)

        incAngle = 8
        # Import mueller data file
        muellerDir = "Mueller_AR/"
    
        muellerFile = muellerDir +  "Mueller_V2_nu%.1f_no3p068_ne3p402_ARcoat_thetain%.1f.txt"%(hwpFreq, incAngle)
        print "reading from:  \t %s"%muellerFile


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
        a2Ave = abs(intg.simps(y, x=x)/(det.fhi - det.flo))

        #Inserts HWP at hwpIndex
        # elements.insert(hwpIndex, opt.OpticalElement("HWP", elements[hwpIndex - 1].temp, 0, 1))
        elements.insert(hwpIndex, e)

        pW_per_Kcmb = th.dPdT(elements, det)*pW


        freqs, UPspecs, _, _ = ps.A4Prop(elements, det, hwpIndex)



        effs = lambda f : map(lambda x : x.Eff(f), elements[hwpIndex+1:])
        cumEff = lambda f : reduce((lambda x, y: x*y), effs(f))

        # Incident power on the HWP
        hwpInc = UPspecs[hwpIndex]
        detIp = hwpInc * rho(freqs) * cumEff(freqs) 
        # Polarized emission of HWP
        hwpEmis = th.weightedSpec(freqs,elements[hwpIndex].temp, elements[hwpIndex].pEmis) * cumEff(freqs)



        #2f power at the detector
        det2FPow = detIp + hwpEmis

        #Total A2 (W)
        A2 = abs(np.trapz(det2FPow, freqs))
        
        telEff =  reduce((lambda x, y : x * y), [e.Eff(det.band_center) for e in elements[2:]])
        print telEff
        band_centers.append(det.band_center / GHz)
        a2s.append(a2Ave)
        A2_pW.append(A2 * pW )
        A2_K.append(A2 * pW / pW_per_Kcmb)

        outString +=  "%d\t%.1f\t%.1f\t%.2e\t%.8e\t%.3f\n"%(det.bid, det.band_center/GHz, hwpFreq, a2Ave, A2*pW / telEff, A2*pW/pW_per_Kcmb)
    print outString

    if writeFile:

        f = open(outFile, 'w')
        f.write(outString)
        f.close()

    return band_centers, a2s, A2_pW, A2_K

def toTeXTable(table, acc = 4):
    out_string = ""
    keys = sorted(table.iterkeys())

    for k in keys:
        out_string += "%.1f & %s\\\\ \n"%(k, str(round(table[k][0],acc)))

    return out_string

def runAll(fileDir):
    expDirs  = [sorted(gb.glob(x+'/*')) for x in sorted(gb.glob(fileDir))]

    hwpIndices = [8,9,10]

    tab_a2 = {}
    tab_pW = {}
    tab_K = {}
    for e in expDirs[0]:
        for hwpi in hwpIndices:
            wf = False
            band_centers, a2s, A2_pW, A2_K = f2Model(e + "/LargeTelescope/", hwpIndex = hwpi, writeFile = wf)
            print  "*"*50 + "\n"

            for i in range(2):
                if band_centers[i] in tab_a2.iterkeys():
                    tab_a2[band_centers[i]].append(a2s[i])
                    tab_pW[band_centers[i]].append(A2_pW[i])
                    tab_K[band_centers[i]].append(A2_K[i])
                else:
                    tab_a2[band_centers[i]] = [a2s[i]]
                    tab_pW[band_centers[i]] = [A2_pW[i]]
                    tab_K[band_centers[i]] = [A2_K[i]]

    print toTeXTable(tab_K)



if __name__=="__main__":
    # f2Model("Experiments/V2_dichroic/45cm/HF_45cm_3waf_silicon/LargeTelescope/" , True)
    f2Model("Experiments/small_aperture/LargeTelescope/")
    # runAll("Experiments/V2_dichroic/45cm")

