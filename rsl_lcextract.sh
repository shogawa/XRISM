#!/bin/sh

export HEADAS=/home/ogawa/work/tools/heasoft/XRISM_15Oct2023_Build7/x86_64-pc-linux-gnu-libc2.31
source $HEADAS/headas-init.sh

export CALDB=/home/ogawa/work/tools/caldb
source $CALDB/software/tools/caldbinit.sh

export XSELECT_MDB=/home/ogawa/work/analysis/xrism/xselect.mdb.xrism

mkdir -p pfiles
export PFILES="./pfiles;$HEADAS/syspfiles"

obsid=$1
xselect<<EOF
xsel
no
read event ${obsid}rsl_p0px1000_cl2.evt
./
yes
set image det
filter pha_cutoff 4000 20000
set binsize 128.0
extr curve exposure=0.8
save curve ${obsid}rsl_allpix_b128_lc.fits clobber=yes
exit
no

rm -fr pfiles