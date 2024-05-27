#!/bin/sh

export HEADAS=/home/ogawa/work/tools/heasoft/XRISM_15Oct2023_Build7/x86_64-pc-linux-gnu-libc2.31
. $HEADAS/headas-init.sh

export CALDB=/home/ogawa/work/tools/caldb
. $CALDB/software/tools/caldbinit.sh

pfiles_dir=pfiles
mkdir -p $pfiles_dir
export PFILES="`pwd`/${pfiles_dir};$HEADAS/syspfiles"

obsid=$1

ln -sf ../resolve/event_uf/${obsid}rsl_p0px5000_uf.evt.gz .

mgtime ingtis="${obsid}rsl_p0px5000_uf.evt.gz[2],${obsid}rsl_p0px5000_uf.evt.gz[6]" outgti=Fe55track.gti merge=AND
rslgain infile=${obsid}rsl_p0px5000_uf.evt.gz outfile=Fe55.ghf linetocorrect=MnKa calmethod=Fe55 clobber=yes debug=yes logfile="rslgain.log" spangti=no ckrisetime=yes calcerr=yes writeerrfunc=yes extraspread=40 numevent=1000 minevent=200 gtifile=Fe55track.gti maxdshift=7.0 minwidth=0.1
rslpha2pi infile=${obsid}rsl_p0px1000_cl.evt.gz outfile=${obsid}rsl_p0px1000_cl_gain.evt driftfile=Fe55.ghf logfile=rslpha2pi.log debug=yes writetemp=yes clobber=yes

rm -fr $pfiles_dir