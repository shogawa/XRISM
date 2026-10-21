#!/bin/sh

pfiles_dir=pfiles
mkdir -p $pfiles_dir
export PFILES="`pwd`/${pfiles_dir};$HEADAS/syspfiles"

obsid=$1
dataclass=$2

xaexpmap ehkfile=${obsid}.ehk.gz gtifile=${obsid}xtd_p0${dataclass}_cl2.evt \
instrume=XTEND badimgfile=${obsid}xtd_p0${dataclass}.bimg.gz \
pixgtifile=${obsid}xtd_a0${dataclass}.fpix.gz outfile=${obsid}xtd_a0${dataclass}.expo \
outmaptype=EXPOSURE delta=20.0 numphi=1 stopsys=SKY instmap=CALDB qefile=CALDB \
contamifile=CALDB vigfile=CALDB obffile=CALDB fwfile=CALDB gvfile=CALDB maskcalsrc=yes \
fwtype=FILE specmode=MONO specfile=spec.fits specform=FITS evperchan=DEFAULT abund=1 \
cols=0 covfac=1 clobber=yes chatter=1 logfile=make_expo_${obsid}xtd_p0${dataclass}.log

rm -fr $pfiles_dir