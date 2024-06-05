#!/bin/sh

export HEADAS=/home/ogawa/work/tools/heasoft/XRISM_15Oct2023_Build7/x86_64-pc-linux-gnu-libc2.31
. $HEADAS/headas-init.sh

export CALDB=/home/ogawa/work/tools/caldb
. $CALDB/software/tools/caldbinit.sh

pfiles_dir=pfiles
mkdir -p $pfiles_dir
export PFILES="`pwd`/${pfiles_dir};$HEADAS/syspfiles"

obsid=$1

xaexpmap ehkfile=${obsid}.ehk.gz gtifile=${obsid}rsl_p0px1000_cl2.evt \
instrume=RESOLVE badimgfile=NONE pixgtifile=${obsid}rsl_px1000_exp.gti.gz \
outfile=${obsid}rsl_p0px1000.expo outmaptype=EXPOSURE delta=20.0 numphi=1 \
stopsys=SKY instmap=CALDB qefile=CALDB contamifile=CALDB vigfile=CALDB obffile=CALDB \
fwfile=CALDB gvfile=CALDB maskcalsrc=yes fwtype=FILE specmode=MONO specfile=spec.fits \
specform=FITS evperchan=DEFAULT abund=1 cols=0 covfac=1 clobber=yes chatter=1
logfile=make_expo_${obsid}rsl_p0px1000.log

rm -fr $pfiles_dir