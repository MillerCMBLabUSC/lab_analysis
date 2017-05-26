import numpy as np
import thermo as th
import OpticalElement as oe
#########################################################
#   Input Data
#########################################################
expDir = "Experiments/MF_30cm_silicon/LargeTelescope/"
channelFile = expDir + "channels.txt"
cameraFile = expDir + "camera.txt"
opticsFile = expDir + "opticalChain.txt"
atmFile = "Atacama_1000um_60deg.txt"
# Must be 1 or 2. This determines the frequency and is needed to import the proper absorption


# Gets channel frequency bounds
GHz = 1.e9 # GHz -> Hz

bandID = 1

ch_str = np.loadtxt(channelFile, dtype=np.str)
band_center = float(ch_str[bandID][2])*GHz #[Hz]
fbw = float(ch_str[bandID][3]) #fractional bandwidth
pixSize = float(ch_str[bandID][4])/1000.
waistFact = float(ch_str[bandID][6])
det_eff = float(ch_str[bandID][7])

flo = band_center*(1 - .5 * fbw) #detector lower bound [Hz]
fhi = band_center*(1 + .5 * fbw) #detector upper bound [Hz]

##Import camera data
cam_str = np.loadtxt(cameraFile, dtype=np.str, usecols=[2])
f_num = float(cam_str[2])
bath_temp = float(cam_str[2])


elements = [] #List of optical elements

#CMB optical element
elements.append(oe.OpticalElement("CMB", 2.725, 1, 1))