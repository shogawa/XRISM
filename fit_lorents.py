#!/usr/bin/env python3
# coding: utf-8

import xspec as xs

from argparse import ArgumentParser
from decimal import Decimal, ROUND_HALF_UP
from math import log10, floor
import os

import astropy.constants as Const
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

c = Const.c.to('km/s').value

def get_argument():
    argparser = ArgumentParser(description='This is the error calculation program.')
    argparser.add_argument('-t', '--target', default='Circinus galaxy', help='target name')
    argparser.add_argument('-l', '--line', default='FeKa', help='Line name')
    argparser.add_argument('-sf', '--specfile', default='xa000162000rsl_pixgr1.pha', help='spectra')
    argparser.add_argument('-rf', '--respfile', default='xa000162000rsl_X_comb.rmf', help='responce')
    argparser.add_argument('-af', '--anclfile', default='xa000162000rsl_X_comb.arf', help='responce')
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

linelist = {
"FeKa":[
[6404.148,1.613,0.278],
[6391.19,2.487,0.207],
[6403.295,1.965,0.182],
[6389.106,2.339,0.066],
[6400.653,4.833,0.106],
[6390.275,4.433,0.065],
[6402.077,2.803,0.094]
],
"FeKb":[
[7046.9,14.17,0.301],
[7057.21,3.12,0.279],
[7058.36,1.97,0.241],
[7054.75,6.38,0.179]
],
"NiKa":[
[7478.281,2.013,0.487],
[7461.131,2.674,0.25],
[7476.529,4.711,0.171],
[7459.874,3.039,0.064],
[7458.029,4.476,0.028]
],
"MnKa":[
[5898.853,1.715,0.353],
[5887.743,2.361,0.229],
[5897.867,2.043,0.141],
[5886.495,4.216,0.11],
[5894.829,4.499,0.079],
[5896.532,2.663,0.066],
[5899.417,0.969,0.005]
],
"CrKa":[
[5414.874,1.457,0.378],
[5405.551,2.224,0.271],
[5414.099,1.76,0.132],
[5403.986,4.74,0.054],
[5412.745,3.138,0.084],
[5410.583,5.149,0.073],
[5418.304,1.988,0.009]
],
"CoKa":[
[6930.425,1.795,0.378],
[6915.713,2.406,0.197],
[6929.388,2.695,0.144],
[6914.659,2.773,0.095],
[6927.676,4.555,0.127],
[6913.078,4.463,0.05],
[6930.941,0.808,0.088]
],
"CuKa":[
[8047.837,2.285,0.579],
[8027.993,2.666,0.236],
[8045.367,3.358,0.08],
[8026.504,3.571,0.105]
],
"CrKb":[
[5947,1.7,0.307],
[5935.31,15.98,0.236],
[5946.24,1.9,0.172],
[5942.04,6.69,0.148],
[5944.93,3.37,0.137]
],
"MnKb":[
[6490.89,1.83,0.254],
[6486.31,9.4,0.234],
[6477.73,13.22,0.234],
[6490.06,1.81,0.164],
[6488.83,2.81,0.114]
],
"CoKb":[
[7649.6,3.05,0.449],
[7647.83,3.58,0.189],
[7639.87,9.78,0.153],
[7645.49,4.89,0.103],
[7636.21,13.59,0.082],
[7654.13,3.79,0.025]
],
"NiKb":[
[8265.01,3.76,0.45],
[8263.01,4.34,0.258],
[8256.67,13.7,0.203],
[8268.7,5.18,0.089]
],
"CuKb":[
[8905.532,3.52,0.485],
[8903.109,3.52,0.248],
[8908.462,3.55,0.11],
[8897.387,8.08,0.1],
[8911.393,5.31,0.055]
]
}

args = get_argument()
file = args.specfile
respFIle = args.respfile
target = args.target
line = args.line

xs.Fit.query = "yes"
xs.Plot.xAxis = "kev"
xs.Plot.add = True
xs.Plot.device = "/null"

xs.Fit.statMethod = "cstat"

xs.Xset.parallel.leven = 12
xs.Xset.parallel.error = 12
xs.Xset.parallel.steppar = 3
xs.Xset.parallel.walkers = 12

xs.AllData(file)

s = xs.AllData(1)
s.response = respFIle
resp = s.response

lines = np.array(linelist[line])
line_energy = np.dot(lines[:,0],lines[:,2])/lines[:,2].sum()
emin = (line_energy - 50)/1000
emax = (line_energy + 30)/1000
print(line_energy,emin,emax)
s.ignore("**-**")
s.notice("{}-{}".format(emin,emax))

num_lorentz = len(lines)
lorentz_model = "zashift(gsmooth((" + " + ".join(["lorentz"] * num_lorentz) + ")constant))"
Model = "powerlaw" + " + " + lorentz_model

xs.AllModels += Model
m1 = xs.AllModels(1)

#m1.powerlaw.PhoIndex = [2,0.01,1,1,3,3]

modelLorents = [i for i in m1.componentNames if "lorentz" in i]

for i, lorentsName in enumerate(modelLorents):
    energy, width, norm = lines[i]
    getattr(m1, lorentsName).LineE = energy*1e-3
    getattr(m1, lorentsName).LineE.frozen = True
    getattr(m1, lorentsName).Width = width*1e-3
    getattr(m1, lorentsName).Width.frozen = True
    getattr(m1, lorentsName).norm = norm
    getattr(m1, lorentsName).norm.frozen = True


m1.show()

m1.powerlaw.norm = 0
m1.powerlaw.norm.frozen = True
m1.zashift.Redshift.frozen = True
m1.gsmooth.Sig_6keV = 0.002
m1.gsmooth.Sig_6keV.frozen = True
xs.Fit.perform()

m1.zashift.Redshift.frozen = False
xs.Fit.perform()
m1.powerlaw.norm.frozen = False
m1.gsmooth.Sig_6keV.frozen = False
xs.Fit.perform()

xs.Fit.error("{0} {1}".format(m1.zashift.Redshift.index, m1.gsmooth.Sig_6keV.index))
#xs.Fit.error("1. {0} {1}".format(m1.zashift.Redshift.index, m1.gsmooth.Sig_6keV.index))

errn = m1.gsmooth.Sig_6keV.values[0] - m1.gsmooth.Sig_6keV.error[0]
errp = m1.gsmooth.Sig_6keV.error[1] - m1.gsmooth.Sig_6keV.values[0]
value = m1.gsmooth.Sig_6keV.values[0]
gsmooth = np.array([value, errp, errn])*1000
print("sigma: {0:.3f}+{1:.3f}-{2:.3f}".format(*gsmooth))
print("FWHM: {0:.3f}+{1:.3f}-{2:.3f}".format(*gsmooth*2.35))

errn = m1.zashift.Redshift.values[0] - m1.zashift.Redshift.error[0]
errp = m1.zashift.Redshift.error[1] - m1.zashift.Redshift.values[0]
value = m1.zashift.Redshift.values[0]
redshift = np.array([value, errp, errn])
print("Redshift: {0}+{1}-{2}".format(*redshift))
print("offset: {0}+{1}-{2}".format(*redshift*line_energy))

plot_data = plot_parameters("data del")

#palette = sns.color_palette('pastel',16)
cmp=matplotlib.colormaps.get_cmap("Pastel1")


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
axes[0].set_xlim(emin,emax)
#axes[0].set_ylim(1E-13,1e-8)
#axes[0].set_ylim(1E-12,1e-8)
ymax = max(yVals + yErrs)
scale = 10**np.floor(np.log10(ymax))
rounded_num = np.ceil(ymax / scale) * scale
axes[0].set_ylim(0,rounded_num)
axes[1].set_xlim(emin,emax)
axes[1].set_ylim(-4.5,4.5)
axes[1].set_xlabel(r'Energy (keV)', fontsize=12)
axes[0].set_ylabel(r'$\rm counts \, s^{-1} \, keV^{-1}$', fontsize=12)
axes[1].set_ylabel('(data - model)/error')
axes[1].set_ylabel('Residual', fontsize=12)
fig.align_ylabels()
axes[0].tick_params(bottom=False, labelbottom=False)
axes[1].plot([0.1,100],[0,0],"k")
color=cmp(3)

txt = target.replace('GC', 'GC ').replace('IC', 'IC ').replace('-', '$-$').replace('CenA', 'Centaurus A')
txt += " " + line.replace("Ka", "K$\\alpha$").replace("Kb", "K$\\beta$")
txt += "\n$\sigma$: ${0:.3f}^{{+{1:.3f}}}_{{-{2:.3f}}}$ eV".format(*gsmooth)
txt += "\nFWHM: ${0:.3f}^{{+{1:.3f}}}_{{-{2:.3f}}}$ eV".format(*gsmooth*2.35)
txt += "\n$z$: ${0:.6f}^{{+{1:.6f}}}_{{-{2:.6f}}}$".format(*redshift)
txt += "\n$cz$: ${0:.3f}^{{+{1:.3f}}}_{{-{2:.3f}}}$ km/s".format(*redshift*c)
axes[0].text(0.01, 0.50, txt, transform=axes[0].transAxes, size=12)

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

#axes[0].set_title('{}'.format(target + " " + line.replace("Ka", "K$\\alpha$").replace("Kb", "K$\\beta$")))

fig.savefig("{0}_{1}.pdf".format(target.replace(" ", "_"),line),bbox_inches='tight', dpi=300,transparent=True)
