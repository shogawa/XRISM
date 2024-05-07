#!/bin/sh

export HEADAS=/home/ogawa/work/tools/heasoft/XRISM_15Oct2023_Build7/x86_64-pc-linux-gnu-libc2.31
source $HEADAS/headas-init.sh

export CALDB=/home/ogawa/work/tools/caldb
source $CALDB/software/tools/caldbinit.sh

export XSELECT_MDB=/home/ogawa/work/analysis/xrism/xselect.mdb.xrism

var=$1

xselect<<EOF
xsel
no
read event ${var}rsl_p0px1000_cl.evt.gz
./
yes
filter column "PIXEL=0:11,13:35"
filter GRADE "0:0"
extract spectrum
save spec ${var}rsl.pha clobber=yes
extract curve
save curve ${var}rsl.lc clobber=yes
exit
no
EOF
