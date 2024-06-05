
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


def plot_xtd_src_lightcurve(lcFile):
    color="blue"
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
    ax.set_title('Xtend Source Light Curve (0.5-10 keV): {0:.1f} ks'.format(exposure/1000))
    ax.set_xlim(0,400000)
    #fig.savefig
    return fig


def plot_xtd_bgd_lightcurve(lcFile):
    hdu = pyfits.open(lcFile)['RATE']
    lc = hdu.data
    exposure = hdu.header["EXPOSURE"]
    fig, ax = plt.subplots()
    #ax.scatter(lc["TIME"], lc["RATE"], marker='o')
    ax.errorbar(lc["TIME"], lc["RATE"], yerr = [lc["ERROR"], lc["ERROR"]], capsize=0, fmt=' ', markersize=5, ecolor="k", markeredgecolor = "k", markerfacecolor='none', color="k",marker='o')
    ax.tick_params(direction = "in", bottom=True, top=True, right=True, left=True)
    ax.set_xlabel('Time (s)', fontsize=12)
    ax.set_ylabel(r'Count rate ($\rm counts \, s^{-1}$)', fontsize=12)
    ax.set_title('Xtend Background Light Curve (0.5-10 keV): {0:.1f} ks'.format(exposure/1000))
    #fig.savefig
    return fig

def plot_xtd_image(imgFile1, imgFile2, rslFOV=False, reg=False):
    hdu = pyfits.open(imgFile2)[0]
    data2= hdu.data
    hdu = pyfits.open(imgFile1)[0]
    wcs = WCS(hdu.header)
    wcs.wcs.crval = [hdu.header["CRVAL1P"], hdu.header["CRVAL2P"]]
    wcs.wcs.crpix = [hdu.header["CRPIX1P"], hdu.header["CRPIX2P"]]
    wcs.wcs.cdelt = [hdu.header["CDELT1P"], hdu.header["CDELT2P"]]
    fig = plt.figure()
    ax = fig.add_subplot(projection=wcs)
    data = data2+hdu.data+1e-1
    norm = ImageNormalize(np.log10(data),interval=ZScaleInterval(), vmax=3, vmin=-1)
    im = ax.imshow(np.log10(data), norm=norm, cmap="PuRd")
    #im = ax.imshow(np.log10(data), vmax=3, vmin=0, cmap="viridis")
    cbar = fig.colorbar(im, ax=ax)
    cbar.ax.yaxis.set_tick_params(direction='in', color='k')
    cbar.ax.set_ylabel(r'Counts', fontsize=12)
    ax.tick_params(direction = "in")
    #ax.set_xlabel('Time (s)', fontsize=12)
    #ax.set_ylabel(r'Count rate ($\rm counts \, s^{-1}$)', fontsize=12)
    ax.set_title('Xtend Image (0.5-10 keV)')
    if rslFOV:
        rx = 1810/2-183.6
        ry = 1810/2-170
        rw = 103.7
        rh = 103.7
        x1  = rx - rw/2
        y1  = ry - rh/2
        x2  = rx + rw/2
        y2  = ry + rh/2
        Rect = [ [ [x1,x2], [y1,y1] ],
                [ [x2,x2], [y1,y2] ],
                [ [x1,x2], [y2,y2] ],
                [ [x1,x1], [y1,y2] ] ]

        lns = []
        #for rect in Rect:
        #    ln, = ax.plot(rect[0],rect[1],color='cyan',lw=1,alpha=0.5)
        #    lns.append(ln)

        pix_size = 85/2.5*0.5
        for i in range(0,7):
            if i<1:
                ax.plot([x1+i*pix_size,x1+i*pix_size],[y1+pix_size,y2],color='cyan',lw=1,alpha=0.5)
                ax.plot([x1+pix_size,x2],[y1+i*pix_size,y1+i*pix_size],color='cyan',lw=1,alpha=0.5)
            else:
                ax.plot([x1+i*pix_size,x1+i*pix_size],[y1,y2],color='cyan',lw=1,alpha=0.5)
                ax.plot([x1,x2],[y1+i*pix_size,y1+i*pix_size],color='cyan',lw=1,alpha=0.5)

    if reg:
        rx = 734.30754
        ry = 732.6416
        rw = 65
        rh = 170
        x1  = rx - rw/2
        y1  = ry - rh/2
        x2  = rx + rw/2
        y2  = ry + rh/2
        Rect = [ [ [x1,x2], [y1,y1] ],
                [ [x2,x2], [y1,y2] ],
                [ [x1,x2], [y2,y2] ],
                [ [x1,x1], [y1,y2] ] ]

        lns = []
        for rect in Rect:
            ln, = ax.plot(rect[0],rect[1],color='b',lw=1,alpha=0.5)
            lns.append(ln)

        rx = 733.15014
        ry = 466.43789
        rw = 65
        rh = 170
        x1  = rx - rw/2
        y1  = ry - rh/2
        x2  = rx + rw/2
        y2  = ry + rh/2
        Rect = [ [ [x1,x2], [y1,y1] ],
                [ [x2,x2], [y1,y2] ],
                [ [x1,x2], [y2,y2] ],
                [ [x1,x1], [y1,y2] ] ]

        lns = []
        for rect in Rect:
            ln, = ax.plot(rect[0],rect[1],color='b',lw=1,alpha=0.5)
            lns.append(ln)

    return fig


if __name__ == "__main__":
    lcFile = "xa000162000xtd_0p5to10keV_b128_src_lc.fits"
    lcFile = "xa000162000xtd_0p5to10keV_b1000_src_lc.fits"
    fig = plot_xtd_src_lightcurve(lcFile)
    fig.savefig("xtd_lcsrc.pdf",bbox_inches='tight', dpi=300,transparent=True)

    lcFile = "xa000162000xtd_0p5to10keV_b128_bgd_lc.fits"
    lcFile = "xa000162000xtd_0p5to10keV_b1000_bgd_lc.fits"
    fig = plot_xtd_bgd_lightcurve(lcFile)
    fig.savefig("xtd_lcbgd.pdf",bbox_inches='tight', dpi=300,transparent=True)


    imgFile1 = "xa000162000xtd_p031100010_detimgsfpfree.fits"
    imgFile1 = "xa000162000xtd_p031100010_detimg.fits"
    imgFile2 = "xa000162000xtd_p032000010_detimg.fits"
    fig = plot_xtd_image(imgFile1, imgFile2, rslFOV=False, reg=False)
    fig.savefig("xtd_img.pdf",bbox_inches='tight', dpi=300,transparent=True)