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
    argparser.add_argument('-ed', '--eventsdir', default='.', help='Eventfile directory path')
    return argparser.parse_args()

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

def plot_rsl_ghf(ghfFile, calghfFile, hkFile):
    pixnum = 36
    fig, axes = plt.subplots(
    2, 1, # 縦 x 横
    gridspec_kw=dict(width_ratios=[1], height_ratios=[1,1], wspace=0.4, hspace=0), \
    sharex='col', sharey='row', figsize=(8,4), dpi=200
    )
    hdu = pyfits.open(ghfFile)['Drift_energy']
    data = hdu.data
    for p in range(pixnum):
        px_data = data[data['PIXEL']==p]
        #ax.plot(px_data['TIME'], px_data['TEMP_AVE']*1e3,marker='o')
        axes[1].plot(px_data['TIME']-hdu.header["TSTART"], px_data['TEMP_FIT']*1e3,marker='${}$'.format(p))

    hdu_cal = pyfits.open(calghfFile)['Drift_energy']
    data_cal = hdu_cal.data
    px_data = data_cal[data_cal['PIXEL']==12]
    axes[1].plot(px_data['TIME']-hdu_cal.header["TSTART"], px_data['TEMP_FIT']*1e3,marker=None, label='Cal pixel', color='k')
    axes[1].set_ylim(49.85,50.15)
    axes[1].tick_params(direction = "in", bottom=True, top=True, right=True, left=True)
    axes[1].set_xlabel('TIME [second]')
    axes[1].set_ylabel('TEMP_FIT [mK]')

    hdu = pyfits.open(hkFile)['HK_SXS_FWE']
    data = hdu.data

    axes[0].plot(data['TIME']-hdu.header["TSTART"], data['FWE_FW_POSITION1_CAL'], color="#624498")
    axes[0].set_ylim(0, 360)
    axes[0].tick_params(direction = "in", bottom=True, top=True, right=True, left=True)
    axes[0].set_ylabel('FW Position')# [degree]')

    axes[0].text(0.01, 330/360, "Fe55", transform=axes[0].transAxes, size=6)
    axes[0].text(0.01, 270/360, "Be", transform=axes[0].transAxes, size=6)
    axes[0].text(0.01, 210/360, "OPEN2", transform=axes[0].transAxes, size=6)
    axes[0].text(0.01, 150/360, "ND", transform=axes[0].transAxes, size=6)
    axes[0].text(0.01, 90/360, "OBF", transform=axes[0].transAxes, size=6)
    axes[0].text(0.01, 30/360, "OPEN", transform=axes[0].transAxes, size=6)
    #axes[0].set_yticks([0, 1, 2, 3, 4, 5])
    #axes[0].set_yticklabels(["UNDEF", "OPEN", "Polymide", "ND", "Be", "Fe55"])
    axes[0].set_yticks([30,90,150,210,270,330])
    #axes[0].set_yticklabels(["OPEN", "ND", "Fe55"])
    axes[0].tick_params(axis="y", labelrotation=0)
    fig.align_ylabels()
    axes[0].tick_params(labelbottom=False)
    axes[1].legend(loc='lower left', fontsize=6)
    return fig


if __name__ == "__main__":
    args = get_argument()
    obsid = args.obsid
    evtFile = args.clevt
    eventsdir = args.eventsdir

    eventsdir = pathlib.Path(eventsdir).resolve()
    feghfFile = eventsdir.joinpath('resolve/event_uf/{0}rsl_000_fe55.ghf.gz'.format(obsid))
    calghfFile = eventsdir.joinpath('resolve/event_uf/{0}rsl_000_pxcal.ghf.gz'.format(obsid))
    hkFile = eventsdir.joinpath('resolve/hk/{0}rsl_a0.hk1.gz'.format(obsid))

    if not pathlib.Path(evtFile).exists(): sys.exit(str(evtFile) + ' does not exist.')
    if not feghfFile.exists(): sys.exit(str(feghfFile) + ' does not exist.')
    if not calghfFile.exists(): sys.exit(str(calghfFile) + ' does not exist.')
    if not hkFile.exists(): sys.exit(str(hkFile) + ' does not exist.')

    fig = plot_rsl_branting_ratio(evtFile)
    fig.savefig("{}rsl_ratio.png".format(obsid),bbox_inches='tight', dpi=300)

    fig = plot_rsl_ghf(feghfFile, calghfFile, hkFile)
    fig.savefig("{}rsl_ghf.png".format(obsid),bbox_inches='tight', dpi=300)
