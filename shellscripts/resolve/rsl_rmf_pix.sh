#!/bin/sh

obsid=$1
pix=$2

pix0=`printf "%02d" ${pix}`

pfiles_dir=pfiles_${pix0}
mkdir -p $pfiles_dir
export PFILES="`pwd`/${pfiles_dir};$HEADAS/syspfiles"

rslmkrmf infile=${obsid}rsl_p0px1000_cl2.evt outfileroot=${obsid}rsl_pix${pix0}_S regmode=DET whichrmf=S resolist=0 regionfile=NONE pixlist=${pix}
#rslmkrmf infile=${obsid}rsl_p0px1000_cl.evt.gz outfileroot=${obsid}rsl_pix_S regmode=DET whichrmf=S resolist=0 regionfile=NONE pixlist=0,1,2,3,4,5,6,7,8,9,10,11,13,14,16,17,18,19,20,21,22,23,24,25,26,28,29,30,31,32,33,34,35 eminin=0.0 dein=0.5 nchanin=60000 useingrd=no eminout=0.0 deout=0.5 nchanout=60000
#rslmkrmf infile=${obsid}rsl_p0px1000_cl.evt.gz outfileroot=pix_L regmode=DET whichrmf=L resolist=0 regionfile=NONE pixlist=0,1,2,3,4,5,6,7,8,9,10,11,13,14,16,17,18,19,20,21,22,23,24,25,26,28,29,30,31,32,33,34,35 eminin=0.0 dein=0.5 nchanin=60000 useingrd=no eminout=0.0 deout=0.5 nchanout=60000
#rslmkrmf infile=${obsid}rsl_p0px1000_cl.evt.gz outfileroot=${obsid}_split regmode=DET splitrmf=yes elcbinfac=16 whichrmf=X splitcomb=yes resolist=0 regionfile=NONE pixlist=0,1,2,3,4,5,6,7,8,9,10,11,13,14,16,17,18,19,20,21,22,23,24,25,26,28,29,30,31,32,33,34,35 eminin=0.0 dein=0.5 nchanin=60000 useingrd=no eminout=0.0 deout=0.5 nchanout=60000

#rslmkrmf infile=${obsid}rsl_p0px1000_cl.evt.gz outfileroot=${obsid}_allpix_S regmode=DET whichrmf=S resolist=0 regionfile=ALLPIX
#rslmkrmf infile=xa${obsid}rsl_p0px1000_cl.evt outfileroot=${obsid}_allpix_L regmode=DET whichrmf=L resolist=0 regionfile=ALLPIX eminin=0.0 dein=0.5 nchanin=60000 useingrd=no eminout=0.0 deout=0.5 nchanout=60000

rm -fr $pfiles_dir