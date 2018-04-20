HELLO!

You have stumbled across my project! In case your goal is to pick it back up, here are some resources and information that may help.

Purpose: to simulate the data processing pipeline used to observe the polarization of the CMB using a half-wave 
	plate. The simulation is meant to be a spin-off of the LEAP project (the contents of which were provided 
	to me by my adviser). The main difference is that LEAP used a predetermined pointing, while I created my
	own pointing strategy.

Roadblocks: The main thing that I can't seem to figure out is what my adviser meant by "galactic roll." Right now, the 
	horizontal roll (roll in horiz. coords) is set to zero. Apparently, when we convert to galactic coordinates,
	this value will become nonzero and it has an important effect on the data. Before the simulation is complete,
	the influence of the galactic roll must be added in.
	Also there is a portion of the simulation code that has to do with noise (both white noise and 1/f noise).
	That portion is incomplete. Before the simulation is complete, the noise function must be up and working. 

Next Steps: Once the simulation is complete, it will be used to compare and contrast two different methods of 
	removing the I-to-P (intensity to polarization) leakage that occurs as a result of the half-wave plate.
	These methods are found in the EBEX and POLARBEAR papers, linked below.
	

Resources:

-> Repository: github.com/MillerCMBLabUSC/lab_analysis/simulation
-> My Github: github.com/rashmi-raviprasad
-> S4CMB: github.com/JulienPeloton/s4cmb
	* used S4CMB when I got stuck with converting from az/el to ra/dec. This helped a lot because, as it 
	turns out, our pointing strategies were very similar!
-> EBEX paper: arxiv.org/abs/1711.01314
-> POLARBEAR paper: arxiv.org/abs/1702.07111






