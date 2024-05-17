#!/bin/sh

export HEADAS=/home/ogawa/work/tools/heasoft/XRISM_15Oct2023_Build7/x86_64-pc-linux-gnu-libc2.31
. $HEADAS/headas-init.sh

export CALDB=/home/ogawa/work/tools/caldb
. $CALDB/software/tools/caldbinit.sh

export XSELECT_MDB=/home/ogawa/work/analysis/xrism/xselect.mdb.xrism

obsid=$1
pix=$2
binsize=$3

pix0=`printf "%02d" ${pix}`

pfiles_dir=pfiles_${pix0}
mkdir -p $pfiles_dir
export PFILES="`pwd`/${pfiles_dir};$HEADAS/syspfiles"

xselect<<EOF
xsel
no
read event ${obsid}rsl_p0px1000_cl2.evt
./
yes
set image det
filter pha_cutoff 4000 20000
filter column "PIXEL=${pix}:${pix}"
set binsize $binsize
extr curve exposure=0.8
save curve ${obsid}rsl_pix${pix0}_b${binsize}_lc.fits clobber=yes
exit
no

rm -fr $pfiles_dir