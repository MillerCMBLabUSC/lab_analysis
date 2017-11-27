#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 16 13:21:06 2017

@author: jacoblashner
"""

import matplotlib.pyplot as plt


ips = np.array(ips)
ipsOld = np.array(ipsOld)
plt.plot(freqs/ GHz, ips*100)
plt.plot(freqs/ GHz, ipsOld*100)
plt.legend(["2 Layers", "1 Layers"])
plt.xlabel("Frequency (GHz)")
plt.ylabel("IP (%)")
plt.title("IP vs Frequency Optimized for 120 GHz")
plt.savefig("/Users/jacoblashner/Desktop/ip_vs_freq.pdf")

#ips93 = np.array(ips93)
#ips93Old = np.array(ips93Old)
#ips145 = np.array(ips145)
#ips145Old = np.array(ips145Old)
#
#freqs = np.array(freqs)
#
#plt.plot(freqs / GHz, ips93 * 100, color='C0')
#plt.plot(freqs / GHz, ips145 * 100, color='C1')
#plt.plot(freqs / GHz, ips93Old * 100, color='C0', linestyle='dashed')
#plt.plot(freqs / GHz, ips145Old * 100, color = 'C1', linestyle = 'dashed')
#
##plt.axvline(120, 0, 1, color='black', linestyle='dashed')
#
#plt.xlabel("Opt Frequency (GHz)")
#plt.ylabel("IP (%)")
#plt.legend(["93 GHz,   2 Layers","145 GHz, 2 Layers","93 GHz,   1 Layer","145 GHz, 1 Layer"])
#plt.title("Window IP vs Optimized Frequency for FOV = 30 degrees")
#plt.savefig("/Users/jacoblashner/Desktop/ip_vs_optFreq.pdf")