#!/bin/sh

. /home/ogawa/anaconda3/etc/profile.d/conda.sh && conda activate spex

obsid=$1
phafile=$2
rmffile=$3
arffile=$4

ogip2spex \
--phafile ${phafile} \
--rmffile ${rmffile} \
--arffile ${arffile} \
--spofile ${obsid}rsl.spo \
--resfile ${obsid}rsl.res
