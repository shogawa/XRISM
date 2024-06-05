#!/bin/sh

export HEADAS=$TOOLS/heasoft/XRISM_15Oct2023_Build7/x86_64-pc-linux-gnu-libc2.31
. $HEADAS/headas-init.sh

export CALDB=$TOOLS/caldb
. $CALDB/software/tools/caldbinit.sh


export XSELECT_MDB=$TOOLS/heasoft/xrism/xselect.mdb.xrism

obsid=$1
pix=$2

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
filter pha_cutoff 0 59999
filter column "PIXEL=${pix}:${pix}"
filter GRADE "0:0"
extract spectrum
save spec ${obsid}rsl_pix${pix0}.pha clobber=yes
exit
no
EOF

rm -fr $pfiles_dir