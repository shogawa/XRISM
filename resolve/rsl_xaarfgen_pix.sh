#!/bin/sh

export HEADAS=$TOOLS/heasoft/XRISM_15Oct2023_Build7/x86_64-pc-linux-gnu-libc2.31
. $HEADAS/headas-init.sh

export CALDB=$TOOLS/caldb
. $CALDB/software/tools/caldbinit.sh

obsid=$1
rmf=$2
pix=$3

pix0=`printf "%02d" ${pix}`

pfiles_dir=pfiles_${pix0}
mkdir -p $pfiles_dir
export PFILES="`pwd`/${pfiles_dir};$HEADAS/syspfiles"

RA_NOM=`fkeyprint ../resolve/event_cl/${obsid}rsl_p0px1000_cl.evt.gz+0 RA_NOM | grep deg | awk '{print $3}'`
DEC_NOM=`fkeyprint ../resolve/event_cl/${obsid}rsl_p0px1000_cl.evt.gz+0 DEC_NOM | grep deg | awk '{print $3}'`
PA_NOM=`fkeyprint ../resolve/event_cl/${obsid}rsl_p0px1000_cl.evt.gz+0 PA_NOM | grep deg | awk '{print $3}'`

RDETX0=3.5
RDETY0=3.5

coordpnt=`coordpnt input="$RDETX0,$RDETY0" outfile=NONE telescop=XRISM instrume=RESOLVE teldeffile=CALDB startsys=DET stopsys=RADEC ra=${RA_NOM} dec=${DEC_NOM} roll=${PA_NOM} ranom=${RA_NOM} decnom=${DEC_NOM} clobber=yes`

ra=$(echo "$coordpnt" | awk '{print $4}')
dec=$(echo "$coordpnt" | awk '{print $5}')

rm -rf $pfiles_dir/xaarfgen.par
rm -rf $pfiles_dir/xaxmaarfgen.par

if [ ${pix} -eq 0 ]; then pix_region='+box(4,3,1,1)' ; fi
if [ ${pix} -eq 1 ]; then pix_region='+box(6,3,1,1)' ; fi
if [ ${pix} -eq 2 ]; then pix_region='+box(5,3,1,1)' ; fi
if [ ${pix} -eq 3 ]; then pix_region='+box(6,2,1,1)' ; fi
if [ ${pix} -eq 4 ]; then pix_region='+box(5,2,1,1)' ; fi
if [ ${pix} -eq 5 ]; then pix_region='+box(6,1,1,1)' ; fi
if [ ${pix} -eq 6 ]; then pix_region='+box(5,1,1,1)' ; fi
if [ ${pix} -eq 7 ]; then pix_region='+box(4,2,1,1)' ; fi
if [ ${pix} -eq 8 ]; then pix_region='+box(4,1,1,1)' ; fi
if [ ${pix} -eq 9 ]; then pix_region='+box(1,3,1,1)' ; fi
if [ ${pix} -eq 10 ]; then pix_region='+box(2,3,1,1)' ; fi
if [ ${pix} -eq 11 ]; then pix_region='+box(1,2,1,1)' ; fi
if [ ${pix} -eq 12 ]; then pix_region='+box(1,1,1,1)' ; fi
if [ ${pix} -eq 13 ]; then pix_region='+box(2,2,1,1)' ; fi
if [ ${pix} -eq 14 ]; then pix_region='+box(2,1,1,1)' ; fi
if [ ${pix} -eq 15 ]; then pix_region='+box(3,2,1,1)' ; fi
if [ ${pix} -eq 16 ]; then pix_region='+box(3,1,1,1)' ; fi
if [ ${pix} -eq 17 ]; then pix_region='+box(3,3,1,1)' ; fi
if [ ${pix} -eq 18 ]; then pix_region='+box(3,4,1,1)' ; fi
if [ ${pix} -eq 19 ]; then pix_region='+box(1,4,1,1)' ; fi
if [ ${pix} -eq 20 ]; then pix_region='+box(2,4,1,1)' ; fi
if [ ${pix} -eq 21 ]; then pix_region='+box(1,5,1,1)' ; fi
if [ ${pix} -eq 22 ]; then pix_region='+box(2,5,1,1)' ; fi
if [ ${pix} -eq 23 ]; then pix_region='+box(1,6,1,1)' ; fi
if [ ${pix} -eq 24 ]; then pix_region='+box(2,6,1,1)' ; fi
if [ ${pix} -eq 25 ]; then pix_region='+box(3,5,1,1)' ; fi
if [ ${pix} -eq 26 ]; then pix_region='+box(3,6,1,1)' ; fi
if [ ${pix} -eq 27 ]; then pix_region='+box(6,4,1,1)' ; fi
if [ ${pix} -eq 28 ]; then pix_region='+box(5,4,1,1)' ; fi
if [ ${pix} -eq 29 ]; then pix_region='+box(6,5,1,1)' ; fi
if [ ${pix} -eq 30 ]; then pix_region='+box(6,6,1,1)' ; fi
if [ ${pix} -eq 31 ]; then pix_region='+box(5,5,1,1)' ; fi
if [ ${pix} -eq 32 ]; then pix_region='+box(5,6,1,1)' ; fi
if [ ${pix} -eq 33 ]; then pix_region='+box(4,5,1,1)' ; fi
if [ ${pix} -eq 34 ]; then pix_region='+box(4,6,1,1)' ; fi
if [ ${pix} -eq 35 ]; then pix_region='+box(4,4,1,1)' ; fi

cat <<EOF > region_RSL_det_pix${pix0}.reg
physical
${pix_region}
EOF

regionfile=region_RSL_det_pix${pix0}.reg

xaarfgen xrtevtfile=raytrace_${obsid}rsl_p0px1000_ptsrc.fits \
source_ra=$ra source_dec=$dec telescop=XRISM instrume=RESOLVE \
emapfile=${obsid}rsl_p0px1000.expo regmode=DET regionfile=${regionfile} \
sourcetype=POINT rmffile=${rmf} erange="0.3 18.0 0 0" \
outfile=${obsid}rsl_p0px1000_ptsrc_pix${pix0}.arf numphoton=300000 minphoton=100 teldeffile=CALDB \
qefile=CALDB contamifile=CALDB obffile=CALDB fwfile=CALDB gatevalvefile=CALDB \
onaxisffile=CALDB onaxiscfile=CALDB mirrorfile=CALDB obstructfile=CALDB \
frontreffile=CALDB backreffile=CALDB pcolreffile=CALDB scatterfile=CALDB \
mode=h clobber=yes seed=7 imgfile=NONE

rm -fr $pfiles_dir