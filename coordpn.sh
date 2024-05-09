#!/bin/sh

export HEADAS=/home/ogawa/work/tools/heasoft/XRISM_15Oct2023_Build7/x86_64-pc-linux-gnu-libc2.31
. $HEADAS/headas-init.sh

export CALDB=/home/ogawa/work/tools/caldb
. $CALDB/software/tools/caldbinit.sh

mkdir -p pfiles
export PFILES="./pfiles;$HEADAS/syspfiles"

obsid=$1
RA_NOM=`fkeyprint ${obsid}rsl_p0px1000_cl.evt.gz+0 RA_NOM | grep deg | awk '{print $3}'`
DEC_NOM=`fkeyprint ${obsid}rsl_p0px1000_cl.evt.gz+0 DEC_NOM | grep deg | awk '{print $3}'`
PA_NOM=`fkeyprint ${obsid}rsl_p0px1000_cl.evt.gz+0 PA_NOM | grep deg | awk '{print $3}'`
echo $RA_NOM $DEC_NOM $PA_NOM

RDETX0=3.5
RDETY0=3.5

XDETX0=`grep box region_xtd_src.reg | awk -F "[(),]" '{print $2}'`
XDETY0=`grep box region_xtd_src.reg | awk -F "[(),]" '{print $3}'`


coordpnt input="$RDETX0,$RDETY0" outfile=NONE telescop=XRISM instrume=RESOLVE teldeffile=CALDB startsys=DET stopsys=RADEC ra=${RA_NOM} dec=${DEC_NOM} roll=${PA_NOM} ranom=${RA_NOM} decnom=${DEC_NOM} clobber=yes
coordpnt input="$XDETX0,$XDETY0" outfile=NONE telescop=XRISM instrume=XTEND teldeffile=CALDB startsys=DET stopsys=RADEC ra=${RA_NOM} dec=${DEC_NOM} roll=${PA_NOM} ranom=${RA_NOM} decnom=${DEC_NOM} clobber=yes

rm -fr pfiles