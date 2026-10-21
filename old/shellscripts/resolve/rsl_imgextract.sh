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
set image DET
filter pha_cutoff 4000 20000
extract image
save image ${obsid}rsl_p0px1000_detimg.fits clobber=yes
exit
no
EOF

rm -fr $pfiles_dir