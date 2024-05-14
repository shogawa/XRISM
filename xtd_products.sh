#!/bin/sh

export HEADAS=/home/ogawa/work/tools/heasoft/XRISM_15Oct2023_Build7/x86_64-pc-linux-gnu-libc2.31
. $HEADAS/headas-init.sh

export CALDB=/home/ogawa/work/tools/caldb
. $CALDB/software/tools/caldbinit.sh

export XSELECT_MDB=/home/ogawa/work/analysis/xrism/xselect.mdb.xrism

dir_analysis=$1
obsid=$2
dataclass=$3
dir_scripts=`pwd`
cd $dir_analysis

sh $dir_scripts/xtd_copy.sh $obsid
mkdir -p pfiles
export PFILES="$dir_analysis/analysis;$HEADAS/syspfiles"
#sh $dir_scripts/xtd_screening.sh $obsid $dataclass
sh $dir_scripts/xtd_imgextract.sh $obsid $dataclass
echo "ok?"
read -q
sh $dir_scripts/xtd_specextract.sh $obsid $dataclass
#sh $dir_scripts/xtd_lcextract.sh $obsid $dataclass
sh $dir_scripts/xtd_rmf.sh $obsid $dataclass
sh $dir_scripts/xtd_xaexpmap.sh $obsid $dataclass
sh $dir_scripts/xtd_xaarfgen.sh $obsid $dataclass
sh $dir_scripts/grppha.sh ${obsid}xtd_src.pi ${obsid}xtd_srgr1.pi min 1
sh $dir_scripts/bkg_rmf_arf.sh ${obsid}xtd_srgr1.pi ${obsid}xtd_bgd.pi ${obsid}xtd_p0${dataclass}_src.rmf ${obsid}xtd_p0${dataclass}_ptsrc.arf

rm -fr pfiles