#!/bin/sh

pfiles_dir=pfiles
mkdir -p $pfiles_dir
export PFILES="`pwd`/${pfiles_dir};$HEADAS/syspfiles"

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

rm -fr $pfiles_dir