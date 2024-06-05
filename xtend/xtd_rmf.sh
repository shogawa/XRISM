#!/bin/sh

export HEADAS=$TOOLS/heasoft/XRISM_15Oct2023_Build7/x86_64-pc-linux-gnu-libc2.31
. $HEADAS/headas-init.sh

export CALDB=$TOOLS/caldb
. $CALDB/software/tools/caldbinit.sh

pfiles_dir=pfiles
mkdir -p $pfiles_dir
export PFILES="`pwd`/${pfiles_dir};$HEADAS/syspfiles"

obsid=$1
dataclass=$2

xtdrmf infile=${obsid}xtd_src.pi outfile=${obsid}xtd_p0${dataclass}_src.rmf \
rmfparam=CALDB eminin=200 dein="2,24" nchanin="5900,500" eminout=0 deout=6 nchanout=4096 clobber=yes

rm -fr $pfiles_dir