#!/bin/sh

export HEADAS=/home/ogawa/work/tools/heasoft/XRISM_15Oct2023_Build7/x86_64-pc-linux-gnu-libc2.31
source $HEADAS/headas-init.sh

export CALDB=/home/ogawa/work/tools/caldb
source $CALDB/software/tools/caldbinit.sh

export XSELECT_MDB=/home/ogawa/work/analysis/xrism/xselect.mdb.xrism

mkdir -p pfiles
export PFILES="./pfiles;$HEADAS/syspfiles"

obsid=$1
dataclass=$2
xselect<<EOF
xsel
no
read eve ${obsid}xtd_p0${dataclass}_cl2.evt .
./
yes
set image det
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
exit
no
EOF

rm -fr pfiles