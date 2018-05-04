import healpy

'''
File: plotmaps.py

Purpose: contains the commands to type into ipython via the command line interface; I 
	just store them here so I can copy/paste easily. Healpy's mollview and mollzoom 
	modules are only accessible through ipython

'''
maps = healpy.read_map('/home/rashmi/maps/planck_sevem_1024_full_test.fits', field = 0)
healpy.zoomtool.mollzoom(maps)


