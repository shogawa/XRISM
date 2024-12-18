#!/bin/sh

pfiles_dir=pfiles
mkdir -p $pfiles_dir
export PFILES="`pwd`/${pfiles_dir};$HEADAS/syspfiles"

phafile=$1
backfile=$2
respfile=$3
arffile=$4

outgrpphafile=`echo $phafile | sed 's/.pi/_grpobin.pi/'`
outgrpphafile1=`echo $phafile | sed 's/.pi/_grpobin1.pi/'`
outphafile1=`echo $phafile | sed 's/.pi/_obin1.pi/'`
outrmffile=`echo $respfile | sed 's/.rmf/_obin.rmf/'`
outrmffile1=`echo $respfile | sed 's/.rmf/_obin1.rmf/'`
outarffile=`echo $arffile | sed 's/.arf/_obin.arf/'`
rspfile=`echo $respfile | sed 's/.rmf/.rsp/'`
outrspfile1=`echo $rspfile | sed 's/.rsp/_obin1.rsp/'`

ftgrouppha infile=$phafile backfile=$backfile respfile=$respfile outfile=$outgrpphafile grouptype=opt clobber=yes &
ftgrouppha infile=$phafile backfile=$backfile respfile=$respfile outfile=$outgrpphafile1 grouptype=optmin groupscale=1 clobber=yes &
#ftmarfrmf $respfile $arffile $rspfile clobber=yes

wait

ftrbnrmf infile=$respfile cmpmode=phafile phafile=$outgrpphafile1 outfile=$outrmffile1 clobber=yes &
ftrbnpha infile=$phafile outfile=$outphafile1 phafile=$outgrpphafile1 properr=no error=poiss-0 clobber=yes &
ftrbnrmf infile=newdiag60000.rmf.gz cmpmode=phafile phafile=$outgrpphafile1 outfile=newdiag60000_obin1.rmf clobber=yes


wait

fparkey $backfile $outphafile1 BACKFILE
fparkey $outrmffile1 $outphafile1 RESPFILE
fparkey $arffile $outphafile1 ANCRFILE

fparkey $backfile $outgrpphafile BACKFILE
fparkey $respfile $outgrpphafile RESPFILE
fparkey $arffile $outgrpphafile ANCRFILE
fparkey $backfile $outgrpphafile1 BACKFILE
fparkey $respfile $outgrpphafile1 RESPFILE
fparkey $arffile $outgrpphafile1 ANCRFILE

#ftrbnrmf infile=$respfile cmpmode=none ecmpmode=optimal phafile=$phafile outfile=$outrmffile inarffile=$arffile outarffile=$outarffile clobber=yes
#fparkey $backfile $outphafile BACKFILE
#fparkey $outrmffile $outphafile RESPFILE
#fparkey $outarffile $outphafile ANCRFILE

rm -rf $pfiles_dir