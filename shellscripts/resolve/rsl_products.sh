#!/bin/sh

export TOOLS=/home/ogawa/work/tools

export HEADAS=$TOOLS/heasoft/XRISM_15Oct2023_Build7/x86_64-pc-linux-gnu-libc2.31
. $HEADAS/headas-init.sh

export CALDB=$TOOLS/caldb
. $CALDB/software/tools/caldbinit.sh

export XSELECT_MDB=$TOOLS/heasoft/xrism/xselect.mdb.xrism

dir_analysis=$1
obsid=$2
dir_scripts=`pwd`
cd $dir_analysis
#sh $dir_scripts/rsl_telgti_screen.sh $obsid
sh $dir_scripts/rsl_copy.sh $obsid
sh $dir_scripts/rsl_screening.sh $obsid
sh $dir_scripts/rsl_imgextract.sh $obsid
sh $dir_scripts/rsl_specextract.sh $obsid
sh $dir_scripts/rsl_lcextract.sh $obsid 128
sh $dir_scripts/rsl_rmf.sh $obsid S
sh $dir_scripts/rsl_xaexpmap.sh $obsid
sh $dir_scripts/rsl_xaarfgen.sh $obsid S region_RSL_det_27.reg
ftgrouppha infile=${obsid}rsl_src.pha outfile=${obsid}rsl_srgr1.pha grouptype=min groupscale=1
fparkey NONE ${obsid}rsl_srgr1.pha BACKFILE
fparkey ${obsid}rsl_S.rmf ${obsid}rsl_srgr1.pha RESPFILE
fparkey ${obsid}rsl_S.arf ${obsid}rsl_srgr1.pha ANCRFILE
