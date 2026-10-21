#!/bin/sh

pfiles_dir=pfiles
mkdir -p $pfiles_dir
export PFILES="`pwd`/${pfiles_dir};$HEADAS/syspfiles"

obsid=$1

#ftcopy infile="${obsid}rsl_p0px1000_cl.evt.gz[EVENTS][(PI>=600)&&((RISE_TIME>=40&&RISE_TIME<=60&&ITYPE<4)||(ITYPE==4))&&STATUS[4]==b0]" outfile=${obsid}rsl_p0px1000_cl2.evt copyall=yes clobber=yes history=yes

#for above 15 keV
#ftcopy infile="${obsid}rsl_p0px1000_cl.evt.gz[EVENTS][(PI>=600)&&((RISE_TIME>=30&&RISE_TIME<=60&&ITYPE<4)||(ITYPE==4))&&STATUS[4]==b0]" outfile=${obsid}rsl_p0px1000_cl2.evt copyall=yes clobber=yes history=yes

#XRISM Quick-Start Guide Version 2.1
ftcopy infile="${obsid}rsl_p0px1000_cl.evt.gz[EVENTS][(PI>=600) && (((((RISE_TIME+0.00075*DERIV_MAX)>46)&&((RISE_TIME+0.00075*DERIV_MAX)<58))&&ITYPE<4)||(ITYPE==4))&&STATUS[4]==b0]" outfile=${obsid}rsl_p0px1000_cl2.evt copyall=yes clobber=yes history=yes

rm -fr $pfiles_dir