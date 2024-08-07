#!/bin/sh

pfiles_dir=pfiles
mkdir -p $pfiles_dir
export PFILES="`pwd`/${pfiles_dir};$HEADAS/syspfiles"

obsid=$1
dataclass=$2
binsize=$3

xselect<<EOF
xsel
no
read eve ${obsid}xtd_p0${dataclass}_cl2.evt .
./
yes
set image det
filter region region_xtd_bgd.reg
filter pha_cutoff 83 1667
set binsize $binsize
extr curve exposure=0.6
save curve ${obsid}xtd_0p5to10keV_b${binsize}_bgd_lc.fits clobber=yes
clear region
filter region region_xtd_src.reg
extr curve exposure=0.6
save curve ${obsid}xtd_0p5to10keV_b${binsize}_src_lc.fits clobber=yes
exit
no
EOF

rm -fr $pfiles_dir