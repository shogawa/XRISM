#!/bin/sh

pfiles_dir=pfiles
mkdir -p $pfiles_dir
export PFILES="`pwd`/${pfiles_dir};$HEADAS/syspfiles"

obsid=$1
binsize=$2

xselect<<EOF
xsel
no
read event ${obsid}rsl_p0px1000_cl2.evt
./
yes
set image det
filter pha_cutoff 4000 20000
set binsize $binsize
extr curve exposure=0.8
save curve ${obsid}rsl_allpix_b${binsize}_lc.fits clobber=yes
exit
no
EOF

rm -fr $pfiles_dir