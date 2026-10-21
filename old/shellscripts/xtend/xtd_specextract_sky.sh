#!/bin/sh

pfiles_dir=pfiles
mkdir -p $pfiles_dir
export PFILES="`pwd`/${pfiles_dir};$HEADAS/syspfiles"

obsid=$1
dataclass=$2
xselect<<EOF
xsel
no
read eve ${obsid}xtd_p0${dataclass}_cl2.evt .
./
yes
set image sky
filter region region_xtd_bgd.reg
filter pha_cutoff 83 1667
set binsize 128.0
extr curve exposure=0.6
save curve ${obsid}xtd_0p5to10keV_b128_bgd_lc.fits clobber=yes
clear pha_cutoff
extr spectrum
save spectrum ${obsid}xtd_bgd.pi clobber=yes
clear region
filter region region_xtd_src.reg
filter pha_cutoff 83 1667
extr curve exposure=0.6
save curve ${obsid}xtd_0p5to10keV_b128_src_lc.fits clobber=yes
clear pha_cutoff
extr spectrum
save spectrum ${obsid}xtd_src.pi clobber=yes
extr image
save image ${obsid}xtd_p0${dataclass}_skyimg_region.fits clobber=yes
exit
no
EOF

rm -fr $pfiles_dir