#!/usr/bin/env python
# coding: utf-8

import xspec as xs

from argparse import ArgumentParser
from decimal import Decimal, ROUND_HALF_UP
from math import log10, floor
import os

import astropy.io.fits as pyfits
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import scipy.constants
from scipy.ndimage import gaussian_filter1d
import seaborn as sns

def get_argument():
    argparser = ArgumentParser(description='This is the error calculation program.')
    argparser.add_argument('-ob', '--object', default='Circinus galaxy', help='object')
    argparser.add_argument('-f', '--file', default='xa000162000rsl_fe55.pha', help='spectra')
    argparser.add_argument('-re', '--resp', default='newdiag.rmf', help='responce')
    return argparser.parse_args()

def getNearestValue(list, num, sidx="no"):
    idx = np.abs(np.asarray(list) - num).argmin()
    return list[idx] if sidx=="no" else idx

def plot_parameters(plot):
    xs.Plot(plot)
    plot_data = [[xs.Plot.x(i+1,1),
              xs.Plot.y(i+1,1),
              xs.Plot.xErr(i+1,1),
              xs.Plot.yErr(i+1,1),
              xs.Plot.x(i+1,2),
              xs.Plot.y(i+1,2),
              xs.Plot.xErr(i+1,2),
              xs.Plot.yErr(i+1,2),
              xs.Plot.model(i+1,1),
              [xs.Plot.addComp(j+1,i+1) for j in range(xs.Plot.nAddComps(i+1))]
              ] for i in range(xs.AllData.nSpectra)]
    return plot_data

def plot_resluts(plot_data, gsmooth, offset, pixel):
    palette = sns.color_palette('pastel',16)
    cmp=ListedColormap(palette)


    xVals, yVals, xErrs, yErrs, xrVals, yrVals, xrErrs, yrErrs, modVals, modComps = plot_data[0]
    fig, axes = plt.subplots(
    2, 1, # 縦 x 横
    gridspec_kw=dict(width_ratios=[1], height_ratios=[2,1], wspace=0.4, hspace=0), \
    sharex='col', sharey='row', figsize=(5,5), dpi=200
    )
    axes[0].set_xscale('linear')
    axes[0].set_yscale('linear')
    #axes[0].set_yscale('linear')
    axes[1].set_xscale('linear')
    axes[1].set_yscale('linear')
    axes[0].set_xlim(5.8,5.92)
    #axes[0].set_ylim(1E-13,1e-8)
    #axes[0].set_ylim(1E-12,1e-8)
    axes[0].set_ylim(0,10 ** (int(np.log10(max(yVals)))+1))
    axes[1].set_xlim(5.85,5.92)
    axes[1].set_ylim(-5,5)
    axes[1].set_xlabel(r'Energy (keV)', fontsize=12)
    axes[0].set_ylabel(r'$\rm counts \, s^{-1} \, keV^{-1}$', fontsize=12)
    axes[1].set_ylabel('(data - model)/error')
    axes[1].set_ylabel('Residual', fontsize=12)
    fig.align_ylabels()
    axes[0].tick_params(bottom=False, labelbottom=False)
    axes[1].plot([0.1,100],[0,0],"k")
    color=cmp(0)

    txt = target.replace('GC', 'GC ').replace('IC', 'IC ').replace('-', '$-$').replace('CenA', 'Centaurus A')
    txt += "\nFWHM: ${0:.3f}^{{+{1:.3f}}}_{{-{2:.3f}}}$".format(*gsmooth*2.35)
    txt += "\noffset: ${0:.3f}^{{+{1:.3f}}}_{{-{2:.3f}}}$".format(*offset)
    axes[0].text(0.01, 0.70, txt, transform=axes[0].transAxes, size=12)


    for i in range(len(plot_data)):
        xVals, yVals, xErrs, yErrs, xrVals, yrVals, xrErrs, yrErrs, modVals, modComps = plot_data[i]
        axes[0].plot(xVals, modVals, color="k", label="Total",linewidth=1,alpha=0.8)
        if not modComps == [[]]:
            for j in range(len(modComps)):
                axes[0].plot(xVals, modComps[j], color="gray",linewidth=1,alpha=0.8)
    ms = 5
    upper=1.5
    for i in range(len(plot_data)):
        xVals, yVals, xErrs, yErrs, xrVals, yrVals, xrErrs, yrErrs, modVals, modComps = plot_data[i]
        color=matplotlib.colormaps.get_cmap("Pastel1")(i+3)
        axes[0].errorbar(xVals, yVals, xerr = [xErrs, xErrs], yerr = [yErrs, yErrs], capsize=0, fmt=' ', markersize=ms, ecolor=color, markeredgecolor = color, markerfacecolor='none', color=color,marker=None)
        axes[1].errorbar(xrVals, yrVals, xerr =[xrErrs, xrErrs], yerr = [yrErrs, yrErrs], capsize=0, fmt=' ', markersize=ms, ecolor=color, markeredgecolor = color, markerfacecolor='none', color=color,marker=None)



    #axes[0].legend(loc="upper right", frameon=False, fontsize=10)
    for ax in axes:
        ax.tick_params(which = "both", direction = 'in',bottom=True, top=True, left=True, right=True)

    axes[0].set_title(r'Pixel {0} Hp spectrum in Mn K$\alpha$ from Fe55 Filter'.format(pixel))
    return fig

args = get_argument()
file = args.file
respFIle = args.resp
target = args.object

xs.Fit.query = "yes"
xs.Plot.xAxis = "kev"
xs.Plot.add = True
xs.Plot.device = "/null"

xs.Fit.statMethod = "cstat"

xs.Xset.parallel.error = 12
xs.Xset.parallel.steppar = 3
xs.Xset.parallel.walkers = 12

xs.AllData(file)

s = xs.AllData(1)
s.response = respFIle
resp = s.response
s.ignore("1-11701,11840-60000")

resp.setPars("1,-0.01,0.01,0.5,1.5,5","0,0.01,-1,-1,1,1")

Model = "gsmooth((lorentz + lorentz + lorentz + lorentz + lorentz + lorentz + lorentz + lorentz)constant)"

xs.AllModels += Model
m1 = xs.AllModels(1)

linefile = os.environ["HOME"] + "/work/tools/caldb/data/gen/bcf/ah_gen_linefit_20140101v003.fits"
hdu = pyfits.open(linefile)["MnKa"]
lineEnergy = hdu.data["ENERGY"]
lineWidth = hdu.data["WIDTH"]
lineNorm = hdu.data["AREA"]

modelLorents = [i for i in m1.componentNames if "lorentz" in i]

for i, lorentsName in enumerate(modelLorents):
    getattr(m1, lorentsName).LineE = lineEnergy[i]*1e-3
    getattr(m1, lorentsName).LineE.frozen = True
    getattr(m1, lorentsName).Width = lineWidth[i]*1e-3
    getattr(m1, lorentsName).Width.frozen = True
    getattr(m1, lorentsName).norm = lineNorm[i]
    getattr(m1, lorentsName).norm.frozen = True

m1.gsmooth.Sig_6keV = 0.002

m1.show()

m1.gsmooth.Sig_6keV.frozen = True
xs.Fit.perform()
m1.gsmooth.Sig_6keV.frozen = False
xs.Fit.perform()

xs.Fit.error("1. 1,27")
xs.Fit.error("1. 2",True)

errn = m1.gsmooth.Sig_6keV.values[0] - m1.gsmooth.Sig_6keV.error[0]
errp = m1.gsmooth.Sig_6keV.error[1] - m1.gsmooth.Sig_6keV.values[0]
value = m1.gsmooth.Sig_6keV.values[0]
gsmooth = np.array([value, errp, errn])*1000
print("sigma: {0:.3f}+{1:.3f}-{2:.3f}".format(*gsmooth))
print("FWHM: {0:.3f}+{1:.3f}-{2:.3f}".format(*gsmooth*2.35))

errn = resp.gain.offset.values[0] - resp.gain.offset.error[0]
errp = resp.gain.offset.error[1] - resp.gain.offset.values[0]
value = resp.gain.offset.values[0]
offset = np.array([value, errp, errn])*1000
print("offset: {0}+{1}-{2}".format(*offset))

plot_data = plot_parameters("data del")

fig = plot_resluts(plot_data, gsmooth, offset, "ALL")
fig.savefig("{0}_mnka.pdf".format(target.replace(" ", "_")),bbox_inches='tight', dpi=300,transparent=True)
m1.constant.factor = m1.constant.factor.values[0]/40.
for pixel in range(36):
    if pixel == 12:
        continue
    pixFile = "_pix{0:02d}.".format(pixel).join(file.split("."))
    xs.AllData(pixFile)
    s = xs.AllData(1)
    s.response = respFIle
    resp = s.response
    s.ignore("1-11701,11840-60000")

    resp.setPars("1,-0.01,0.01,0.5,1.5,5","0,0.01,-1,-1,1,1")

    m1.gsmooth.Sig_6keV.frozen = True
    xs.Fit.perform()
    m1.gsmooth.Sig_6keV.frozen = False
    xs.Fit.perform()
    xs.Fit.error("1. 1,27")
    xs.Fit.error("1. 2",True)

    errn = m1.gsmooth.Sig_6keV.values[0] - m1.gsmooth.Sig_6keV.error[0]
    errp = m1.gsmooth.Sig_6keV.error[1] - m1.gsmooth.Sig_6keV.values[0]
    value = m1.gsmooth.Sig_6keV.values[0]
    gsmooth = np.array([value, errp, errn])*1000
    print("sigma: {0:.3f}+{1:.3f}-{2:.3f}".format(*gsmooth))
    print("FWHM: {0:.3f}+{1:.3f}-{2:.3f}".format(*gsmooth*2.35))

    errn = resp.gain.offset.values[0] - resp.gain.offset.error[0]
    errp = resp.gain.offset.error[1] - resp.gain.offset.values[0]
    value = resp.gain.offset.values[0]
    offset = np.array([value, errp, errn])*1000
    print("offset: {0}+{1}-{2}".format(*offset))

    plot_data = plot_parameters("data del")

    fig = plot_resluts(plot_data, gsmooth, offset, pixel)

    fig.savefig("{0}_mnka_pix{1:02d}.pdf".format(target.replace(" ", "_"), pixel),bbox_inches='tight', dpi=300,transparent=True)
