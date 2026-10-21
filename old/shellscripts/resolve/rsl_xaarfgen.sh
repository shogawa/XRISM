#!/bin/sh

obsid=$1
mode=$2
regionfile=$3

pfiles_dir=pfiles
mkdir -p $pfiles_dir
export PFILES="`pwd`/${pfiles_dir};$HEADAS/syspfiles"

rm -rf $pfiles_dir/xaarfgen.par
rm -rf $pfiles_dir/xaxmaarfgen.par

RA_NOM=`fkeyprint ../resolve/event_cl/${obsid}rsl_p0px1000_cl.evt.gz+0 RA_NOM | grep deg | awk '{print $3}'`
DEC_NOM=`fkeyprint ../resolve/event_cl/${obsid}rsl_p0px1000_cl.evt.gz+0 DEC_NOM | grep deg | awk '{print $3}'`
PA_NOM=`fkeyprint ../resolve/event_cl/${obsid}rsl_p0px1000_cl.evt.gz+0 PA_NOM | grep deg | awk '{print $3}'`

RDETX0=3.5
RDETY0=3.5

coordpnt=`coordpnt input="$RDETX0,$RDETY0" outfile=NONE telescop=XRISM instrume=RESOLVE teldeffile=CALDB startsys=DET stopsys=RADEC ra=${RA_NOM} dec=${DEC_NOM} roll=${PA_NOM} ranom=${RA_NOM} decnom=${DEC_NOM} clobber=yes`

ra=$(echo "$coordpnt" | awk '{print $4}')
dec=$(echo "$coordpnt" | awk '{print $5}')

#rm -rf raytrace_${obsid}rsl_p0px1000_ptsrc.fits

xaarfgen xrtevtfile=raytrace_${obsid}rsl_p0px1000_ptsrc.fits \
source_ra=$ra source_dec=$dec telescop=XRISM instrume=RESOLVE \
emapfile=${obsid}rsl_p0px1000.expo regmode=DET regionfile=${regionfile} \
sourcetype=POINT rmffile=${obsid}rsl_${mode}.rmf  erange="0.3 18.0 0 0" \
outfile=${obsid}rsl_${mode}.arf numphoton=300000 minphoton=100 teldeffile=CALDB \
qefile=CALDB contamifile=CALDB obffile=CALDB fwfile=CALDB gatevalvefile=CALDB \
onaxisffile=CALDB onaxiscfile=CALDB mirrorfile=CALDB obstructfile=CALDB \
frontreffile=CALDB backreffile=CALDB pcolreffile=CALDB scatterfile=CALDB \
mode=h clobber=yes seed=7 imgfile=NONE

rm -fr $pfiles_dir