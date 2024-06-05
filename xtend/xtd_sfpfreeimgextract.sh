#!/bin/sh

export HEADAS=$TOOLS/heasoft/XRISM_15Oct2023_Build7/x86_64-pc-linux-gnu-libc2.31
. $HEADAS/headas-init.sh

export CALDB=$TOOLS/caldb
. $CALDB/software/tools/caldbinit.sh

export XSELECT_MDB=$TOOLS/heasoft/xselect.mdb.xrism

pfiles_dir=pfiles
mkdir -p $pfiles_dir
export PFILES="`pwd`/${pfiles_dir};$HEADAS/syspfiles"

obsid=$1
dataclass=$2

xselect<<EOF
xsel
no
read eve ${obsid}xtd_p0${dataclass}_cl.evt.gz .
./
yes
set image DET
filter region exclude_calsources.reg
extract image
save image ${obsid}xtd_p0${dataclass}_detimgsfpfree.fits clobber=yes
exit
no
EOF

rm -fr $pfiles_dir