#!/bin/sh

export HEADAS=/home/ogawa/work/tools/heasoft/XRISM_15Oct2023_Build7/x86_64-pc-linux-gnu-libc2.31
. $HEADAS/headas-init.sh

export CALDB=/home/ogawa/work/tools/caldb
. $CALDB/software/tools/caldbinit.sh

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
set image DET
filter pha_cutoff 4000 20000
extract image
save image ${obsid}rsl_p0px1000_detimg.fits clobber=yes
exit
no
EOF

rm -fr pfiles