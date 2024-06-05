#!/bin/sh

export HEADAS=$TOOLS/heasoft/XRISM_15Oct2023_Build7/x86_64-pc-linux-gnu-libc2.31
. $HEADAS/headas-init.sh

export CALDB=$TOOLS/caldb
. $CALDB/software/tools/caldbinit.sh

export XSELECT_MDB=$TOOLS/heasoft/xselect.mdb.xrism

pfiles_dir=pfiles
mkdir -p $pfiles_dir
export PFILES="`pwd`/${pfiles_dir};$HEADAS/syspfiles"

obsid=$1

ftcopy "${CALDB}/data/xrism/resolve/bcf/response/xa_rsl_rmfparam_20190101v005.fits.gz[GAUSFWHM1]" xa_rsl_rmfparam_fordiagrmf.fits clobber=yes

ftcalc 'xa_rsl_rmfparam_fordiagrmf.fits[GAUSFWHM1]' xa_rsl_rmfparam_fordiagrmf.fits PIXEL0 0.000000001 rows=- clobber=yes

rslrmf NONE newdiag whichrmf=S rmfparamfile=xa_rsl_rmfparam_fordiagrmf.fits clobber=yes

ln -sf ../../resolve/event_cl/${obsid}rsl_p0px5000_cl.evt.gz .

xselect<<EOF
xsel
no
read event ${obsid}rsl_p0px5000_cl.evt.gz
./
yes
filter pha_cutoff 0 59999
filter column "PIXEL=0:11,13:26,28:35"
filter GRADE "0:0"
extract spectrum
save spec ${obsid}rsl_fe55.pha clobber=yes
exit
no
EOF


rm -fr $pfiles_dir