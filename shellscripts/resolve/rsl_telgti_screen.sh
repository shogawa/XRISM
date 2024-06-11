#!/bin/sh

export HEADAS=$TOOLS/heasoft/XRISM_15Oct2023_Build7/x86_64-pc-linux-gnu-libc2.31
. $HEADAS/headas-init.sh

export CALDB=$TOOLS/caldb
. $CALDB/software/tools/caldbinit.sh

pfiles_dir=pfiles
mkdir -p $pfiles_dir
export PFILES="`pwd`/${pfiles_dir};$HEADAS/syspfiles"

obsid=$1

ln -sf ../resolve/event_uf/${obsid}rsl_p0px1000_uf.evt.gz .
ln -sf ../resolve/event_uf/${obsid}rsl_adr.gti.gz .
ln -sf ../auxil/${obsid}_gen.gti.gz .

ahscreen "infile=${obsid}rsl_p0px1000_uf.evt.gz" "outfile=${obsid}rsl_p0px1000_cl_notelgti.evt" \ "gtifile=${obsid}rsl_adr.gti.gz[GTIADROFF],${obsid}rsl_p0px1000_uf.evt.gz[GTIPOINT],${obsid}_gen.gti.gz[GTIATT],${obsid}rsl_p0px1000_uf.evt.gz[GTI], \
${obsid}rsl_p0px1000_uf.evt.gz[GTIMKF],${obsid}rsl_p0px1000_uf.evt.gz[GTIEHK]" "expr=NONE" "selectfile=CALDB" "label=PIXELALL" "mergegti=AND" "cpkeyword=yes" "leapsecfile=REFDATA" \
 "logfile=${obsid}rsl_p0px1000_cl_notelgti.log" "clobber=yes"

fthedit ${obsid}rsl_p0px1000_cl_notelgti.evt+1 TLMIN46 a 0

ln -sf ${obsid}rsl_p0px1000_cl_notelgti.evt ${obsid}rsl_p0px1000_cl.evt.gz

rm -fr $pfiles_dir