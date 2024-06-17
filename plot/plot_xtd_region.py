from argparse import ArgumentParser
from decimal import Decimal, ROUND_HALF_UP
import datetime
from math import log10, floor
import os
import re

import astropy.io.fits as pyfits
from astropy.visualization import ZScaleInterval,ImageNormalize
from astropy.wcs import WCS
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import numpy as np

def get_argument():
    argparser = ArgumentParser(description='This is the Resolve data reduction program.')
    argparser.add_argument('-if', '--imgfile', default='xa000162000xtd_p031100010_detimg.fits', help='Image file')
    return argparser.parse_args()

def calculate_centroid(img, x1, y1, x2, y2):
    ix1 = int(x1)
    iy1 = int(y1)
    ix2 = int(x2)
    iy2 = int(y2)
    region = img[iy1:iy2+1, ix1:ix2+1]

    total = region.sum()
    if total == 0:
        return x1, y1

    rows, cols = region.shape
    row_coords, col_coords = np.mgrid[:rows, :cols]
    row_weighted_sum = (region * row_coords).sum()
    col_weighted_sum = (region * col_coords).sum()

    row_centroid = row_weighted_sum / total
    col_centroid = col_weighted_sum / total

    return x1 + col_centroid, y1 + row_centroid

def iterate_centroid(img, x1, y1, x2, y2):
    centroid_x, centroid_y = calculate_centroid(img, x1, y1, x2, y2)
    drx = 1
    dry = 1
    rx = centroid_x
    ry = centroid_y
    rw = int(x2 - x1)
    rh = int(y2 - y1)
    x1  = int(rx - rw/2)
    y1  = int(rx - rh/2)
    x2  = int(ry + rw/2)
    y2  = int(ry + rh/2)
    i = 0
    while drx>=0.05 and dry>=0.05:
        centroid_x1, centroid_y1 = calculate_centroid(img, x1, y1, x2, y2)
        drx = abs(centroid_x - centroid_x1)
        dry = abs(centroid_y - centroid_y1)
        rx = centroid_x1
        ry = centroid_y1
        rw = 60
        rh = 170
        x1  = int(rx - rw/2)
        y1  = int(rx - rh/2)
        x2  = int(ry + rw/2)
        y2  = int(ry + rh/2)
        centroid_x = centroid_x1
        centroid_y = centroid_y1
        i = i + 1
        print(i)
        print(drx,dry)
        print(centroid_x,centroid_y)

    return centroid_x1, centroid_y1

def plot_xtd_image(imgFile):
    hdu = pyfits.open(imgFile)[0]
    wcs = WCS(hdu.header)
    wcs.wcs.crval = [hdu.header["CRVAL1P"], hdu.header["CRVAL2P"]]
    wcs.wcs.crpix = [hdu.header["CRPIX1P"], hdu.header["CRPIX2P"]]
    wcs.wcs.cdelt = [hdu.header["CDELT1P"], hdu.header["CDELT2P"]]
    fig = plt.figure()
    ax = fig.add_subplot(projection=wcs)
    data = hdu.data
    norm = ImageNormalize(np.log10(data+1e-1),interval=ZScaleInterval(), vmax=3, vmin=-1)
    im = ax.imshow(np.log10(data+1e-1), norm=norm, cmap="PuRd")
    #im = ax.imshow(np.log10(data), vmax=3, vmin=0, cmap="viridis")
    cbar = fig.colorbar(im, ax=ax)
    cbar.ax.yaxis.set_tick_params(direction='in', color='k')
    cbar.ax.set_ylabel(r'Counts', fontsize=12)
    ax.tick_params(direction = "in")
    ax.set_xlim(650,800)
    ax.set_ylim(200,900)
    ax.set_xticks(np.array([600, 650, 700, 800]))
    #ax.set_xlabel('Time (s)', fontsize=12)
    #ax.set_ylabel(r'Count rate ($\rm counts \, s^{-1}$)', fontsize=12)

    rx = 733
    ry = 733
    rw = 60
    rh = 170
    x1  = rx - rw/2
    y1  = ry - rh/2
    x2  = rx + rw/2
    y2  = ry + rh/2

    centroid_x, centroid_y = iterate_centroid(data, x1, y1, x2, y2)
    rx = centroid_x
    ry = centroid_y
    with open("region_xtd_src.reg", "w") as f:
        region = 'box({0:.5f},{1:.5f},{2:.1f},{3:.1f},0)'.format(rx, ry, rw, rh)
        s = []
        s.append('physical')
        s.append(region)
        f.write('\n'.join(s))
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

    ry = ry - 334
    with open("region_xtd_bgd.reg", "w") as f:
        region = 'box({0:.5f},{1:.5f},{2:.1f},{3:.1f},0)'.format(rx, ry, rw, rh)
        s = []
        s.append('physical')
        s.append(region)
        f.write('\n'.join(s))
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
    args = get_argument()
    imgFile = args.imgfile
    fig = plot_xtd_image(imgFile)
    fig.savefig("xtd_img.pdf",bbox_inches='tight', dpi=300,transparent=True)