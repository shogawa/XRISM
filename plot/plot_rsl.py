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


def plot_rsl_branting_ratio(evtFile):
    hdu = pyfits.open(evtFile)['EVENTS']
    evt = hdu.data
    exposure = hdu.header["EXPOSURE"]
    Hp = evt[evt["ITYPE"]==0]
    Mp = evt[evt["ITYPE"]==1]
    Ms = evt[evt["ITYPE"]==2]
    Lp = evt[evt["ITYPE"]==3]
    Ls = evt[evt["ITYPE"]==4]
    grades = evt["ITYPE"]
    fig, ax = plt.subplots()
    #ax.scatter(lc["TIME"], lc["RATE"], marker='o')
    weights = np.ones(len(grades))/float(len(grades))
    ax.hist(grades, weights=weights, bins=[0,1,2,3,4,5], align="mid", color="orange",width=0.5)
    ax.tick_params(direction = "in", bottom=True, top=True, right=True, left=True)
    ax.set_xlabel('Grade', fontsize=12)
    ax.set_ylabel('Fraction', fontsize=12)
    ax.set_title('Histogram of Resolve grade')
    ax.set_ylim(0,1)
    ax.set_xlim(-0.5,5)
    ax.set_yticks(np.linspace(0,1,11))
    ax.set_xticks(np.array([0, 1, 2, 3, 4])+0.25)
    ax.set_xticklabels(["Hp", "Mp", "Ms", "Lp", "Ls"])
    #fig.savefig
    return fig

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

def plot_rsl_ghf(ghfFile, hkFile):
    pixnum = 36
    fig, axes = plt.subplots(
    2, 1, # 縦 x 横
    gridspec_kw=dict(width_ratios=[1], height_ratios=[1,1], wspace=0.4, hspace=0), \
    sharex='col', sharey='row', figsize=(8,4), dpi=200
    )
    #ghfFile = "/home/ogawa/work/analysis/xrism/000162000/resolve/event_uf/xa000162000rsl_000_fe55.ghf.gz"
    hdu = pyfits.open(ghfFile)['Drift_energy']
    data = hdu.data
    for p in range(pixnum):
        px_data = data[data['PIXEL']==p]
        #ax.plot(px_data['TIME'], px_data['TEMP_AVE']*1e3,marker='o')
        axes[1].plot(px_data['TIME']-hdu.header["TSTART"], px_data['TEMP_FIT']*1e3,marker='${}$'.format(p), label=p)
    axes[1].set_ylim(49.85,50.15)
    axes[1].tick_params(direction = "in", bottom=True, top=True, right=True, left=True)
    axes[1].set_xlabel('TIME [second]')
    axes[1].set_ylabel('TEMP_FIT [mK]')

    hdu = pyfits.open(hkFile)['HK_SXS_FWE']
    data = hdu.data

    axes[0].plot(data['TIME']-hdu.header["TSTART"], data['FWE_FW_POSITION1_CAL'], color="#624498")
    axes[0].set_ylim(0, 360)
    axes[0].tick_params(direction = "in", bottom=True, top=True, right=True, left=True)
    axes[0].set_ylabel('FW Position [degree]')

    axes[0].text(0.06, 329/360, "Fe55", transform=axes[0].transAxes, size=10)
    axes[0].text(0.06, 30/360, "OPEN", transform=axes[0].transAxes, size=10)
    #axes[0].set_yticks([0, 1, 2, 3, 4, 5])
    #axes[0].set_yticklabels(["UNDEF", "OPEN", "Polymide", "ND", "Be", "Fe55"])
    axes[0].tick_params(axis="y", labelrotation=0)
    fig.align_ylabels()
    axes[0].tick_params(labelbottom=False)
    #ax.legend(ncol=6)
    return fig

def plot_rsl_image(imgFile):
    hdu = pyfits.open(imgFile)[0]
    wcs = WCS(hdu.header)
    wcs.wcs.crval = [hdu.header["CRVAL1P"], hdu.header["CRVAL2P"]]
    wcs.wcs.crpix = [hdu.header["CRPIX1P"], hdu.header["CRPIX2P"]]
    wcs.wcs.cdelt = [hdu.header["CDELT1P"], hdu.header["CDELT2P"]]
    fig = plt.figure()
    ax = fig.add_subplot(projection=wcs)
    data = hdu.data
    norm = ImageNormalize(np.log10(data+1e-10),interval=ZScaleInterval(), vmax=5, vmin=2)
    im = ax.imshow(np.log10(data+1e-10), norm=norm, cmap="PuRd")
    #norm = ImageNormalize(data,interval=ZScaleInterval())
    #im = ax.imshow(data, norm=norm, cmap="PuRd")
    cbar = fig.colorbar(im, ax=ax)
    cbar.ax.yaxis.set_tick_params(direction='in', color='k')
    cbar.ax.set_ylabel(r'Counts', fontsize=12)
    #cbar.ax.set_yticks(np.linspace(2,4,5))
    xi=np.arange(0,6)
    yi=np.arange(0,6)
    pmap=np.zeros([6,6],dtype=int)
    pmap[0,0]=12; pmap[1,0]=14; pmap[2,0]=16; pmap[3,0]=8; pmap[4,0]=6; pmap[5,0]=5;
    pmap[0,1]=11; pmap[1,1]=13; pmap[2,1]=15; pmap[3,1]=7; pmap[4,1]=4; pmap[5,1]=3;
    pmap[0,2]=9;  pmap[1,2]=10; pmap[2,2]=17; pmap[3,2]=0; pmap[4,2]=2; pmap[5,2]=1;
    pmap[0,3]=19; pmap[1,3]=20; pmap[2,3]=18; pmap[3,3]=35; pmap[4,3]=28; pmap[5,3]=27;
    pmap[0,4]=21; pmap[1,4]=22; pmap[2,4]=25; pmap[3,4]=33; pmap[4,4]=31; pmap[5,4]=29;
    pmap[0,5]=23; pmap[1,5]=24; pmap[2,5]=26; pmap[3,5]=34; pmap[4,5]=32; pmap[5,5]=30;
    pmap.T
    for i in xi:
        for j in yi:
            #ax.text(i,j,pmap[i][j],horizontalalignment='center')
            ax.text(i-0.25,j+0.25,pmap[i][j],horizontalalignment="center")
            ax.text(i,j,data[i][j],horizontalalignment="center")
    x1  = -0.5
    y1  = -0.5
    x2  = 5.5
    y2  = 5.5
    pix_size=1
    for i in range(0,7):
        if i<1:
            ax.plot([x1+i*pix_size,x1+i*pix_size],[y1+pix_size,y2],color='k',lw=1,alpha=0.5)
            ax.plot([x1+pix_size,x2],[y1+i*pix_size,y1+i*pix_size],color='k',lw=1,alpha=0.5)
        else:
            ax.plot([x1+i*pix_size,x1+i*pix_size],[y1,y2],color='k',lw=1,alpha=0.5)
            ax.plot([x1,x2],[y1+i*pix_size,y1+i*pix_size],color='k',lw=1,alpha=0.5)
    ax.tick_params(direction = "in")
    #ax.set_xlabel('Time (s)', fontsize=12)
    #ax.set_ylabel(r'Count rate ($\rm counts \, s^{-1}$)', fontsize=12)
    ax.set_xlim(-0.5,5.5)
    ax.set_ylim(-0.5,5.5)
    #ax.set_ylim(0,6.5)
    ax.set_title('Resolve Image (2-10 keV)')
    return fig


if __name__ == "__main__":
    evtFile = "xa000162000rsl_p0px1000_cl2.evt"
    fig = plot_rsl_branting_ratio(evtFile)
    fig.savefig("rsl_ratio.pdf",bbox_inches='tight', dpi=300,transparent=True)


    lcFile = "xa000162000rsl_allpix_b1000_lc.fits"
    fig = plot_rsl_lightcurve(lcFile)
    fig.savefig("rsl_lc.pdf",bbox_inches='tight', dpi=300,transparent=True)


    ghfFile = "/home/ogawa/work/analysis/xrism/000162000/analysis_gain/Fe55.ghf"
    hkFile = "/home/ogawa/work/analysis/xrism/000162000/resolve/hk/xa000162000rsl_a0.hk1.gz"
    fig = plot_rsl_ghf(ghfFile, hkFile)
    fig.savefig("rsl_ghf.pdf",bbox_inches='tight', dpi=300,transparent=True)

    imgFile = "xa000162000rsl_p0px1000_detimg.fits"
    fig = plot_rsl_image(imgFile)
    fig.savefig("rsl_img.pdf",bbox_inches='tight', dpi=300,transparent=True)