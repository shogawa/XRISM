#!/bin/sh

pfiles_dir=pfiles
mkdir -p $pfiles_dir
export PFILES="`pwd`/${pfiles_dir};$HEADAS/syspfiles"

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
save image ${obsid}xtd_p0${dataclass}_detimg.fits clobber=yes
exit
no
EOF

rm -fr $pfiles_dir