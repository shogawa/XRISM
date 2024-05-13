#!/bin/sh

export HEADAS=/home/ogawa/work/tools/heasoft/XRISM_15Oct2023_Build7/x86_64-pc-linux-gnu-libc2.31
. $HEADAS/headas-init.sh

export CALDB=/home/ogawa/work/tools/caldb
. $CALDB/software/tools/caldbinit.sh

mkdir -p pfiles
export PFILES="./pfiles;$HEADAS/syspfiles"

obsid=$1
dataclass=$2

xaexpmap ehkfile=${obsid}.ehk.gz gtifile=${obsid}xtd_p0${dataclass}_cl2.evt \
instrume=XTEND badimgfile=${obsid}xtd_p0${dataclass}.bimg.gz \
pixgtifile=${obsid}xtd_a0${dataclass}.fpix.gz outfile=${obsid}xtd_a0${dataclass}.expo \
outmaptype=EXPOSURE delta=20.0 numphi=1 stopsys=SKY instmap=xa_xtd_instmap_20190101v004.fits qefile=CALDB \
contamifile=CALDB vigfile=CALDB obffile=CALDB fwfile=CALDB gvfile=CALDB maskcalsrc=yes \
fwtype=FILE specmode=MONO specfile=spec.fits specform=FITS evperchan=DEFAULT abund=1 \
cols=0 covfac=1 clobber=yes chatter=1 logfile=make_expo_${obsid}xtd_p0${dataclass}.log

rm -fr pfiles