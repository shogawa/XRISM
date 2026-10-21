#!/bin/sh

pfiles_dir=pfiles
mkdir -p $pfiles_dir
export PFILES="`pwd`/${pfiles_dir};$HEADAS/syspfiles"

obsid=$1

xselect<<EOF
xsel
no
read event ${obsid}rsl_p0px1000_cl2.evt
./
yes
filter pha_cutoff 0 59999
filter column "PIXEL=0:11,13:26,28:35"
filter GRADE "0:0"
extract spectrum
save spec ${obsid}rsl_src.pha clobber=yes
exit
no
EOF

rm -fr $pfiles_dir