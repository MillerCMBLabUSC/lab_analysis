import healpy


maps = healpy.read_map('/home/rashmi/lab_analysis/apps/simulation/maps/planck_commander_1024_full_test.fits', field = (0, 1, 2))
#nside = healpy.npix2nside(1024)
#healpy.zoomtool.mollzoom(maps)

print healpy.pixelfunc.get_nside(maps)

print healpy.pixelfunc.get_map_size(maps)
