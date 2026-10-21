#!/bin/sh

pfiles_dir=pfiles
mkdir -p $pfiles_dir
export PFILES="`pwd`/${pfiles_dir};$HEADAS/syspfiles"

obsid=$1
dataclass=$2

xtdrmf infile=${obsid}xtd_src.pi outfile=${obsid}xtd_src.rmf \
rmfparam=CALDB eminin=200 dein="2,24" nchanin="5900,500" eminout=0 deout=6 nchanout=4096 clobber=yes

rm -fr $pfiles_dir