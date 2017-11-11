import healpy


maps = healpy.read_map('/home/rashmi/maps/planck_sevem_1024_full_test.fits', field = 0)
#nside = healpy.npix2nside(1024)
healpy.zoomtool.mollzoom(maps)

#print healpy.pixelfunc.get_nside(maps)

