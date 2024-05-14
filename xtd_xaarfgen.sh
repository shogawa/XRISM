#!/bin/sh

export HEADAS=/home/ogawa/work/tools/heasoft/XRISM_15Oct2023_Build7/x86_64-pc-linux-gnu-libc2.31
. $HEADAS/headas-init.sh

export CALDB=/home/ogawa/work/tools/caldb
. $CALDB/software/tools/caldbinit.sh

mkdir -p pfiles
export PFILES="./pfiles;$HEADAS/syspfiles"

obsid=$1
dataclass=$2

RA_NOM=`fkeyprint ../xtend/event_cl/${obsid}xtd_p0${dataclass}_cl.evt.gz+0 RA_NOM | grep deg | awk '{print $3}'`
DEC_NOM=`fkeyprint ../xtend/event_cl/${obsid}xtd_p0${dataclass}_cl.evt.gz+0 DEC_NOM | grep deg | awk '{print $3}'`
PA_NOM=`fkeyprint ../xtend/event_cl/${obsid}xtd_p0${dataclass}_cl.evt.gz+0 PA_NOM | grep deg | awk '{print $3}'`

XDETX0=`grep box region_xtd_src.reg | awk -F "[(),]" '{print $2}'`
XDETY0=`grep box region_xtd_src.reg | awk -F "[(),]" '{print $3}'`

coordpnt=`coordpnt input="$XDETX0,$XDETY0" outfile=NONE telescop=XRISM instrume=XTEND teldeffile=CALDB startsys=DET stopsys=RADEC ra=${RA_NOM} dec=${DEC_NOM} roll=${PA_NOM} ranom=${RA_NOM} decnom=${DEC_NOM} clobber=yes`

ra=$(echo "$coordpnt" | awk '{print $4}')
dec=$(echo "$coordpnt" | awk '{print $5}')

#rmf=$2
#regionfile=$3
rm -rf raytrace_${obsid}xtd_p0${dataclass}_boxreg_ptsrc.fits

xaarfgen xrtevtfile=raytrace_${obsid}xtd_p0${dataclass}_boxreg_ptsrc.fits \
source_ra=$ra source_dec=$dec telescop=XRISM instrume=XTEND \
emapfile=${obsid}xtd_a0${dataclass}.expo regmode=DET \
regionfile=region_xtd_src.reg sourcetype=POINT \
rmffile=${obsid}xtd_p0${dataclass}_src.rmf erange="0.3 18.0 0 0" \
outfile=${obsid}xtd_p0${dataclass}_ptsrc.arf numphoton=300000 minphoton=100 \
teldeffile=CALDB qefile=CALDB contamifile=CALDB obffile=CALDB fwfile=CALDB \
onaxisffile=CALDB onaxiscfile=CALDB mirrorfile=CALDB obstructfile=CALDB \
frontreffile=CALDB backreffile=CALDB pcolreffile=CALDB \
scatterfile=CALDB mode=h clobber=yes seed=7 imgfile=NONE

rm -fr pfiles