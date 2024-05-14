#!/bin/sh

export HEADAS=/home/ogawa/work/tools/heasoft/XRISM_15Oct2023_Build7/x86_64-pc-linux-gnu-libc2.31
. $HEADAS/headas-init.sh

export CALDB=/home/ogawa/work/tools/caldb
. $CALDB/software/tools/caldbinit.sh

export XSELECT_MDB=/home/ogawa/work/analysis/xrism/xselect.mdb.xrism

mkdir -p pfiles
export PFILES="./pfiles;$HEADAS/syspfiles"

obsid=$1
dataclass=$2

cellsize=0
logprob2=-30
n_division=1
bgdlevel=500

searchflickpix infile=${obsid}xtd_p0${dataclass}_cl.evt.gz outfile=${obsid}xxtd_a0${dataclass}.fpix \
cellsize=$cellsize logprob1=10 logprob2=$logprob2 iterate=no n_division=$n_division bthresh=$bgdlevel \
cleanimg=no clobber=yes

searchflickpix infile=${obsid}xtd_p0${dataclass}_cl.evt.gz outfile=${obsid}xtd_p0${dataclass}_cl2.evt \
cellsize=$cellsize logprob1=10 logprob2=$logprob2 iterate=no n_division=$n_division bthresh=$bgdlevel \
cleanimg=yes clobber=yes

ftappend ${obsid}xtd_p0${dataclass}_cl.evt.gz ${obsid}xtd_p0${dataclass}_cl2.evt

rm -fr pfiles