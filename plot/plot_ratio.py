#!/nasA_xarm1/prepro/tools/xappl-env/venv-xappl/bin/python

import pathlib
import sys
from argparse import ArgumentParser

import astropy.io.fits as pyfits
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from astropy.time import Time
from astropy.time import TimeDelta
from matplotlib.colors import ListedColormap

def get_argument():
    argparser = ArgumentParser(description='This is the Resolve Plot program.')
    argparser.add_argument('-oi', '--obsid', default='xa000162000', help='OBSID')
    argparser.add_argument('-cl', '--clevt', help='Cleand event file')
    argparser.add_argument('-fe', '--feghf', help='Fe55 gain history file')
    argparser.add_argument('-cal', '--calghf', help='CAL pixel gain history file')
    argparser.add_argument('-hk', '--hkfile', help='HK file')
    #argparser.add_argument('-ed', '--eventsdir', default='.', help='Eventfile directory path')
    return argparser.parse_args()

def plot_rsl_branching_ratio(evtFile):
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
    weights = np.ones(grades.size)/float(grades.size)
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
    ax.text(0., 0.9, "N: {0}\nR: {1:0.3f}".format(Hp.size, Hp.size/grades.size), size=10)
    ax.text(1., 0.9, "N: {0}\nR: {1:0.3f}".format(Mp.size, Mp.size/grades.size), size=10)
    ax.text(2., 0.9, "N: {0}\nR: {1:0.3f}".format(Ms.size, Ms.size/grades.size), size=10)
    ax.text(3., 0.9, "N: {0}\nR: {1:0.3f}".format(Lp.size, Lp.size/grades.size), size=10)
    ax.text(4., 0.9, "N: {0}\nR: {1:0.3f}".format(Ls.size, Ls.size/grades.size), size=10)
    return fig


def plot_rsl_branching_ratio_pix(evtFile):
    colors = ['b', 'r', 'orange', 'purple', 'magenta']
    fig, ax = plt.subplots()
    hdu = pyfits.open(evtFile)['EVENTS']
    evt = hdu.data
    exposure = hdu.header["EXPOSURE"]
    Hp = evt[evt["ITYPE"]==0]
    Mp = evt[evt["ITYPE"]==1]
    Ms = evt[evt["ITYPE"]==2]
    Lp = evt[evt["ITYPE"]==3]
    Ls = evt[evt["ITYPE"]==4]
    for p in range(36):
        if p==12: continue
        Hp = evt[(evt["ITYPE"]==0) & (evt["PIXEL"]==p)]
        Mp = evt[(evt["ITYPE"]==1) & (evt["PIXEL"]==p)]
        Ms = evt[(evt["ITYPE"]==2) & (evt["PIXEL"]==p)]
        Lp = evt[(evt["ITYPE"]==3) & (evt["PIXEL"]==p)]
        Ls = evt[(evt["ITYPE"]==4) & (evt["PIXEL"]==p)]
        total = Hp.size + Mp.size + Ms.size + Lp.size + Ls.size
        cps = total / exposure
        ratio_Hp = Hp.size / total
        ratio_Mp = Mp.size / total
        ratio_Ms = Ms.size / total
        ratio_Lp = Lp.size / total
        ratio_Ls = Ls.size / total
        ax.scatter(cps, ratio_Hp, alpha=0.5, c=colors[0])
        ax.scatter(cps, ratio_Mp, alpha=0.5, c=colors[1])
        ax.scatter(cps, ratio_Ms, alpha=0.5, c=colors[2])
        ax.scatter(cps, ratio_Lp, alpha=0.5, c=colors[3])
        ax.scatter(cps, ratio_Ls, alpha=0.5, c=colors[4])


    ax.scatter(1e-4, 2, label='Hp', c=colors[0])
    ax.scatter(1e-4, 2, label='Mp', c=colors[1])
    ax.scatter(1e-4, 2, label='Ms', c=colors[2])
    ax.scatter(1e-4, 2, label='Lp', c=colors[3])
    ax.scatter(1e-4, 2, label='Ls', c=colors[4])
    v = np.logspace(-3,2,100)
    br = theoritical_br(v)
    for i, r in enumerate(br):
        ax.plot(v, r, c=colors[i])

    ax.set_xlabel(r'Count rate (s$^{-1}$ pix$^{-1}$)', fontsize=12)
    ax.set_ylabel('Ratio', fontsize=12)
    ax.set_title('Resolve branching ratio')
    ax.set_ylim(-0.02,1.02)
    ax.set_xlim(1e-3,1e2)
    ax.set_xscale('log')
    ax.tick_params(direction = "in", which='both', bottom=True, top=True, right=True, left=True)
    ax.legend(loc='upper right', fontsize=12)
    return fig

def theoritical_br(v):
    dtHR = 0.07072
    dtMR = 0.01832
    Hp = np.exp(-2*v*dtHR)
    Mp = np.exp(-v*dtHR) * (np.exp(-v*dtMR) - np.exp(-v*dtHR))
    Ms = np.exp(-v*dtMR) * (np.exp(-v*dtMR) - np.exp(-v*dtHR))
    Lp = np.exp(-v*dtHR) * (1 - np.exp(-v*dtMR))
    Ls = (1 - np.exp(-v*dtMR)) * (1 + np.exp(-v*dtMR) - np.exp(-v*dtHR))
    return Hp, Mp, Ms, Lp, Ls

if __name__ == "__main__":
    args = get_argument()
    obsid = args.obsid
    evtFile = args.clevt

    #eventsdir = args.eventsdir
    #eventsdir = pathlib.Path(eventsdir).resolve()
    #feghfFile = eventsdir.joinpath('resolve/event_uf/{0}rsl_000_fe55.ghf.gz'.format(obsid))
    #calghfFile = eventsdir.joinpath('resolve/event_uf/{0}rsl_000_pxcal.ghf.gz'.format(obsid))
    #hkFile = eventsdir.joinpath('resolve/hk/{0}rsl_a0.hk1.gz'.format(obsid))

    if not pathlib.Path(evtFile).exists(): sys.exit(str(evtFile) + ' does not exist.')
    fig = plot_rsl_branching_ratio(evtFile)
    fig.savefig("{}rsl_ratio.png".format(obsid),bbox_inches='tight', dpi=300)

    fig = plot_rsl_branching_ratio_pix(evtFile)
    fig.savefig("{}rsl_ratio_pix.png".format(obsid),bbox_inches='tight', dpi=300)
