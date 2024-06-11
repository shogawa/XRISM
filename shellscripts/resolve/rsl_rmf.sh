#!/bin/sh

export HEADAS=$TOOLS/heasoft/XRISM_15Oct2023_Build7/x86_64-pc-linux-gnu-libc2.31
. $HEADAS/headas-init.sh

export CALDB=$TOOLS/caldb
. $CALDB/software/tools/caldbinit.sh

pfiles_dir=pfiles
mkdir -p $pfiles_dir
export PFILES="`pwd`/${pfiles_dir};$HEADAS/syspfiles"

obsid=$1
mode=$2

if [ $mode = "S" ]; then
#rslmkrmf infile=${obsid}rsl_p0px1000_cl2.evt outfileroot=${obsid}rsl_S regmode=DET whichrmf=S resolist=0 regionfile=NONE pixlist=0-11,13-26,28-35
rslmkrmf infile=${obsid}rsl_p0px1000_cl2.evt \
outfileroot=${obsid}rsl_S \
regmode=DET whichrmf=S resolist=0 \
regionfile=NONE pixlist=0-11,13-26,28-35 \
eminin=0.0 dein=0.5 nchanin=60000 \
useingrd=no eminout=0.0 deout=0.5 nchanout=60000

elif [ $mode = "M" ]; then
rslmkrmf infile=${obsid}rsl_p0px1000_cl2.evt \
outfileroot=${obsid}rsl_M \
regmode=DET whichrmf=M resolist=0 \
regionfile=NONE pixlist=0-11,13-26,28-35 \
eminin=0.0 dein=0.5 nchanin=60000 \
useingrd=no eminout=0.0 deout=0.5 nchanout=60000

elif [ $mode = "L" ]; then
rslmkrmf infile=${obsid}rsl_p0px1000_cl2.evt \
outfileroot=${obsid}rsl_L \
regmode=DET whichrmf=L resolist=0 \
regionfile=NONE pixlist=0-11,13-26,28-35 \
eminin=0.0 dein=0.5 nchanin=60000 \
useingrd=no eminout=0.0 deout=0.5 nchanout=60000

elif [ $mode = "X" ]; then
rslmkrmf infile=${obsid}rsl_p0px1000_cl2.evt \
outfileroot=${obsid}rsl_X \
regmode=DET whichrmf=X resolist=0 \
regionfile=NONE pixlist=0-11,13-26,28-35 \
eminin=0.0 dein=0.5 nchanin=60000 \
useingrd=no eminout=0.0 deout=0.5 nchanout=60000

elif [ $mode = "X_comb" ]; then
rslmkrmf infile=${obsid}rsl_p0px1000_cl2.evt \
outfileroot=${obsid}rsl_X \
regmode=DET whichrmf=X resolist=0 \
regionfile=NONE pixlist=0-11,13-26,28-35 \
eminin=0.0 dein=0.5 nchanin=60000 \
useingrd=no eminout=0.0 deout=0.5 nchanout=60000 \
splitrmf=yes elcbinfac=16 splitcomb=yes

else
  echo "Failed"
fi

#rslmkrmf infile=${obsid}rsl_p0px1000_cl.evt.gz outfileroot=${obsid}rsl_S regmode=DET whichrmf=S resolist=0 regionfile=NONE pixlist=0,1,2,3,4,5,6,7,8,9,10,11,13,14,16,17,18,19,20,21,22,23,24,25,26,28,29,30,31,32,33,34,35 eminin=0.0 dein=0.5 nchanin=60000 useingrd=no eminout=0.0 deout=0.5 nchanout=60000
#rslmkrmf infile=${obsid}rsl_p0px1000_cl.evt.gz outfileroot=${obsid}_L regmode=DET whichrmf=L resolist=0 regionfile=NONE pixlist=0,1,2,3,4,5,6,7,8,9,10,11,13,14,16,17,18,19,20,21,22,23,24,25,26,28,29,30,31,32,33,34,35 eminin=0.0 dein=0.5 nchanin=60000 useingrd=no eminout=0.0 deout=0.5 nchanout=60000
#rslmkrmf infile=${obsid}rsl_p0px1000_cl.evt.gz outfileroot=${obsid}_split regmode=DET splitrmf=yes elcbinfac=16 whichrmf=X splitcomb=yes resolist=0 regionfile=NONE pixlist=0,1,2,3,4,5,6,7,8,9,10,11,13,14,16,17,18,19,20,21,22,23,24,25,26,28,29,30,31,32,33,34,35 eminin=0.0 dein=0.5 nchanin=60000 useingrd=no eminout=0.0 deout=0.5 nchanout=60000

#rslmkrmf infile=${obsid}rsl_p0px1000_cl.evt.gz outfileroot=${obsid}_allpix_S regmode=DET whichrmf=S resolist=0 regionfile=ALLPIX
#rslmkrmf infile=xa${obsid}rsl_p0px1000_cl.evt outfileroot=${obsid}_allpix_L regmode=DET whichrmf=L resolist=0 regionfile=ALLPIX eminin=0.0 dein=0.5 nchanin=60000 useingrd=no eminout=0.0 deout=0.5 nchanout=60000

rm -fr $pfiles_dir