import numpy as np
import matplotlib.pyplot as plt
import ephem
from lab_analysis.libs.geometry import coordinates as crd
from datetime import datetime
from lab_analysis.apps.get_ra_dec import get_ra_dec as grd
np.set_printoptions(edgeitems = 50)

usc = ephem.Observer()
usc.lon = '-118.286926'
usc.lat = '34.019579'

kwargs = {"obs": usc}
default = grd.ScanParameters(50, 50, 100, 100, 5, 1, **kwargs)

default.grd.get_ra_dec(**kwargs)


