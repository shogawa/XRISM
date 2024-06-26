#!/bin/sh

export HEADAS=$TOOLS/heasoft/XRISM_15Oct2023_Build7/x86_64-pc-linux-gnu-libc2.31
. $HEADAS/headas-init.sh

export CALDB=$TOOLS/caldb
. $CALDB/software/tools/caldbinit.sh

export XSELECT_MDB=$TOOLS/heasoft/xrism/xselect.mdb.xrism

pfiles_dir=pfiles
mkdir -p $pfiles_dir
export PFILES="`pwd`/${pfiles_dir};$HEADAS/syspfiles"

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

rm -fr $pfiles_dir