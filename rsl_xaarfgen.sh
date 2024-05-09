#!/bin/sh

export HEADAS=/home/ogawa/work/tools/heasoft/XRISM_15Oct2023_Build7/x86_64-pc-linux-gnu-libc2.31
. $HEADAS/headas-init.sh

export CALDB=/home/ogawa/work/tools/caldb
. $CALDB/software/tools/caldbinit.sh

obsid=$1

RA_NOM=`fkeyprint ${obsid}rsl_p0px1000_cl.evt.gz+0 RA_NOM | grep deg | awk '{print $3}'`
DEC_NOM=`fkeyprint ${obsid}rsl_p0px1000_cl.evt.gz+0 DEC_NOM | grep deg | awk '{print $3}'`
PA_NOM=`fkeyprint ${obsid}rsl_p0px1000_cl.evt.gz+0 PA_NOM | grep deg | awk '{print $3}'`

RDETX0=3.5
RDETY0=3.5

coordpnt=`coordpnt input="$RDETX0,$RDETY0" outfile=NONE telescop=XRISM instrume=RESOLVE teldeffile=CALDB startsys=DET stopsys=RADEC ra=${RA_NOM} dec=${DEC_NOM} roll=${PA_NOM} ranom=${RA_NOM} decnom=${DEC_NOM} clobber=yes`

ra=$(echo "$coordpnt" | awk '{print $4}')
dec=$(echo "$coordpnt" | awk '{print $5}')

mkdir -p pfiles
export PFILES="./pfiles;$HEADAS/syspfiles"

rm ~/pfiles/xaarfgen.par
rm ~/pfiles/xaxmaarfgen.par

rmf=$2
regionfile=$3


xaarfgen xrtevtfile=raytrace_${obsid}rsl_p0px1000_ptsrc.fits \
._ra=$ra ._dec=$dec telescop=XRISM instrume=RESOLVE \
emapfile=${obsid}rsl_p0px1000.expo regmode=DET regionfile=${regionfile} \
.type=POINT rmffile=${rmf} erange="0.3 18.0 0 0" \
outfile=${obsid}rsl_p0px1000_ptsrc.arf numphoton=300000 minphoton=100 teldeffile=CALDB \
qefile=CALDB contamifile=CALDB obffile=CALDB fwfile=CALDB gatevalvefile=CALDB \
onaxisffile=CALDB onaxiscfile=CALDB mirrorfile=CALDB obstructfile=CALDB \
frontreffile=CALDB backreffile=CALDB pcolreffile=CALDB scatterfile=CALDB \
mode=h clobber=yes seed=7 imgfile=NONE

rm -fr pfiles