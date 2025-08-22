#! /usr/bin/env python3
from decimal import Decimal, ROUND_HALF_UP
import datetime
from math import log10, floor
import os

import astropy.io.fits as pyfits
from astropy.time import Time
from astropy.time import TimeDelta
from astropy.visualization import ZScaleInterval,ImageNormalize
from astropy.wcs import WCS
import astropy.units as UNITS
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import numpy as np
import pandas as pd
import scipy.constants
from scipy.ndimage import gaussian_filter1d
import seaborn as sns

def plot_rsl_lightcurve(lcFile):
    color=matplotlib.colormaps.get_cmap("Pastel1")(3)
    color="purple"
    hdu = pyfits.open(lcFile)['RATE']
    lc = hdu.data
    exposure = hdu.header["EXPOSURE"]
    fig, ax = plt.subplots()
    #t = Time(hdu.header["MJDREFI"], format='mjd', scale='utc') + TimeDelta(hdu.header["TSTART"], format="sec")
    #ts = t + lc["TIME"]*UNITS.s
    #ax.scatter(lc["TIME"], lc["RATE"], marker='o')
    #ax.errorbar(ts.mjd, lc["RATE"], yerr = [lc["ERROR"], lc["ERROR"]], capsize=0, fmt=' ', markersize=5, ecolor="k", markeredgecolor = "k", markerfacecolor='none', color="k",marker='o')
    ax.errorbar(lc["TIME"], lc["RATE"], yerr = [lc["ERROR"], lc["ERROR"]], capsize=0, fmt=' ', markersize=5, ecolor=color, markeredgecolor = color, markerfacecolor='none', color=color,marker='o')
    ax.tick_params(direction = "in", bottom=True, top=True, right=True, left=True)
    ax.set_xlabel('Time (s)', fontsize=12)
    ax.set_ylabel(r'Count rate ($\rm counts \, s^{-1}$)', fontsize=12)
    ax.set_title('Resolve Light Curve (2-10 keV): {0:.1f} ks'.format(exposure/1000))
    ax.set_xlim(0,400000)
    #fig.savefig
    return fig


if __name__ == "__main__":
    lcFile = "xa000162000rsl_allpix_b1000_lc.fits"
    lcFile = "xa000162000rsl_allpix_b1000_lc_notelgti.fits"
    fig = plot_rsl_lightcurve(lcFile)
    fig.savefig("rsl_lc.pdf",bbox_inches='tight', dpi=300,transparent=True)
