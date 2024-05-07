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

if [ ! -e ${obsid}xtd_p0${dataclass}_cl2.evt ]; then
ln -sf ${obsid}xtd_p0${dataclass}_cl.evt.gz ${obsid}xtd_p0${dataclass}_cl2.evt
fi

xselect<<EOF
xsel
no
read eve ${obsid}xtd_p0${dataclass}_cl2.evt .
./
yes
set image DET
filter region exclude_calsources.reg
filter pha_cutoff 83 1667
extract image
save image ${obsid}xtd_p0${dataclass}_detimg.fits
exit
no
EOF

rm -fr pfiles