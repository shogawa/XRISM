#!/bin/zsh

export HEADAS=/home/ogawa/work/tools/heasoft/XRISM_15Oct2023_Build7/x86_64-pc-linux-gnu-libc2.31
source $HEADAS/headas-init.sh

export CALDB=/home/ogawa/work/tools/caldb
source $CALDB/software/tools/caldbinit.sh

export XSELECT_MDB=/home/ogawa/work/analysis/xrism/xselect.mdb.xrism

mkdir -p pfiles
export PFILES="./pfiles;$HEADAS/syspfiles"

dir_analysis=$1
obsid=$2
dir_scripts=`pwd`
cd $dir_analysis
zsh $dir_scripts/copy.sh $obsid
cd $dir_analysis/analysis
mkdir -p pfiles
export PFILES="$dir_analysis/analysis;$HEADAS/syspfiles"
zsh $dir_scripts/rsl_screening.sh $obsid
zsh $dir_scripts/rsl_imgextract.sh $obsid
zsh $dir_scripts/rsl_specextract.sh $obsid
zsh $dir_scripts/rsl_lcextract.sh $obsid
zsh $dir_scripts/rsl_rmf.sh $obsid
zsh $dir_scripts/rsl_xaexpmap.sh $obsid
zsh $dir_scripts/rsl_xaarfgen.sh $obsid ${obsid}rsl_pix_S.rmf region_RSL_det_27.reg
zsh $dir_scripts/grppha.sh ${obsid}rsl_pix.pha ${obsid}rsl_pixgr1.pha min 1
zsh $dir_scripts/bkg_rmf_arf.sh ${obsid}rsl_pixgr1.pha NONE ${obsid}rsl_pix_S.rmf ${obsid}rsl_p0px1000_ptsrc.arf

rm -fr pfiles