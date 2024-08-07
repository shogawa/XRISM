#!/bin/sh

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
EOF

rm -fr $pfiles_dir