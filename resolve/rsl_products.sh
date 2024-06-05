#!/bin/sh

export HEADAS=/home/ogawa/work/tools/heasoft/XRISM_15Oct2023_Build7/x86_64-pc-linux-gnu-libc2.31
. $HEADAS/headas-init.sh

export CALDB=/home/ogawa/work/tools/caldb
. $CALDB/software/tools/caldbinit.sh

export XSELECT_MDB=/home/ogawa/work/analysis/xrism/xselect.mdb.xrism

dir_analysis=$1
obsid=$2
dir_scripts=`pwd`
dir_scripts_comon=$dir_scripts/..
cd $dir_analysis
#sh $dir_scripts/rsl_telgti_screen.sh $obsid
sh $dir_scripts/rsl_copy.sh $obsid
sh $dir_scripts/rsl_screening.sh $obsid
sh $dir_scripts/rsl_imgextract.sh $obsid
sh $dir_scripts/rsl_specextract.sh $obsid
sh $dir_scripts/rsl_lcextract.sh $obsid 128
sh $dir_scripts/rsl_rmf.sh $obsid
sh $dir_scripts/rsl_xaexpmap.sh $obsid
sh $dir_scripts/rsl_xaarfgen.sh $obsid ${obsid}rsl_pix_S.rmf region_RSL_det_27.reg
sh $dir_scripts_comon/grppha.sh ${obsid}rsl_pix.pha ${obsid}rsl_pixgr1.pha min 1
sh $dir_scripts_comon/bkg_rmf_arf.sh ${obsid}rsl_pixgr1.pha NONE ${obsid}rsl_pix_S.rmf ${obsid}rsl_p0px1000_ptsrc.arf
