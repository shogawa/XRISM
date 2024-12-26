#!/bin/sh

pfiles_dir=pfiles
mkdir -p $pfiles_dir
export PFILES="`pwd`/${pfiles_dir};$HEADAS/syspfiles"

phafile=$1
backfile=$2
respfile=$3
respfile1=$4
respfile2=$5
arffile=$6

outgrpphafile=`echo $phafile | sed 's/.pi/_grpobin.pi/'`
outgrpphafile1=`echo $phafile | sed 's/.pi/_grpobin1.pi/'`
outphafile1=`echo $phafile | sed 's/.pi/_obin1.pi/'`
outrmffile=`echo $respfile | sed 's/.rmf/_obin.rmf/'`
outrmffile11=`echo $respfile1 | sed 's/.rmf/_obin1.rmf/'`
outrmffile12=`echo $respfile2 | sed 's/.rmf/_obin1.rmf/'`
outcombrmffile=`echo $respfile1 | sed 's/.rmf/_comb_obin1.rmf/'`
outarffile=`echo $arffile | sed 's/.arf/_obin.arf/'`
rspfile=`echo $respfile | sed 's/.rmf/.rsp/'`
outrspfile1=`echo $rspfile | sed 's/.rsp/_obin1.rsp/'`

ftgrouppha infile=$phafile backfile=$backfile respfile=$respfile outfile=$outgrpphafile grouptype=opt clobber=yes &
ftgrouppha infile=$phafile backfile=$backfile respfile=$respfile outfile=$outgrpphafile1 grouptype=optmin groupscale=1 clobber=yes &
#ftmarfrmf $respfile $arffile $rspfile clobber=yes

wait

ftrbnrmf infile=$respfile1 cmpmode=phafile phafile=$outgrpphafile1 outfile=$outrmffile11 clobber=yes &
ftrbnrmf infile=$respfile2 cmpmode=phafile phafile=$outgrpphafile1 outfile=$outrmffile12 clobber=yes &
ftrbnpha infile=$phafile outfile=$outphafile1 phafile=$outgrpphafile1 properr=no error=poiss-0 clobber=yes &
ftrbnrmf infile=newdiag60000.rmf.gz cmpmode=phafile phafile=$outgrpphafile1 outfile=newdiag60000_obin1.rmf clobber=yes

wait

cp $outrmffile11 $outcombrmffile
ftappend "$outrmffile12[EBOUNDS]" $outcombrmffile
ftappend "$outrmffile12[MATRIX]" $outcombrmffile

fparkey EBOUNDS "$outcombrmffile[1]" EXTENSION add=yes
fparkey 1 "$outcombrmffile[1]" EXTVER add=yes
fparkey MATRIX "$outcombrmffile[2]" EXTENSION add=yes
fparkey 1 "$outcombrmffile[2]" EXTVER add=yes
fparkey EBOUNDS "$outcombrmffile[3]" EXTENSION add=yes
fparkey 2 "$outcombrmffile[3]" EXTVER add=yes
fparkey MATRIX "$outcombrmffile[4]" EXTENSION add=yes
fparkey 2 "$outcombrmffile[4]" EXTVER add=yes

fparkey $backfile $outphafile1 BACKFILE
fparkey $outcombrmffile $outphafile1 RESPFILE
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