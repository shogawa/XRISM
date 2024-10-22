#!/bin/sh

pfiles_dir=pfiles
mkdir -p $pfiles_dir
export PFILES="`pwd`/${pfiles_dir};$HEADAS/syspfiles"

phafile=$1
backfile=$2
respfile=$3
arffile=$4

outphafile=`echo $phafile | sed 's/.pha/_obin.pha/'`
outrmffile=`echo $respfile | sed 's/.rmf/_obin.rmf/'`
outarffile=`echo $arffile | sed 's/.arf/_obin.arf/'`

ftgrouppha infile=$phafile backfile=$backfile respfile=$respfile outfile=$outphafile grouptype=opt clobber=yes &
ftrbnrmf infile=$respfile cmpmode=none ecmpmode=optimal phafile=$phafile outfile=$outrmffile inarffile=$arffile outarffile=$outarffile clobber=yes

wait

fparkey $backfile $outphafile BACKFILE
fparkey $outrmffile $outphafile RESPFILE
fparkey $outarffile $outphafile ANCRFILE

rm -rf $pfiles_dir