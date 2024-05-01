#!/bin/zsh

export HEADAS=/home/ogawa/work/tools/heasoft/XRISM_15Oct2023_Build7/x86_64-pc-linux-gnu-libc2.31
source $HEADAS/headas-init.sh

export CALDB=/home/ogawa/work/tools/caldb
source $CALDB/software/tools/caldbinit.sh

export XSELECT_MDB=/home/ogawa/work/analysis/xrism/xselect.mdb.xrism

dir_analysis=$1
obsid=$2
dataclass=$3
dir_scripts=`pwd`
cd $dir_analysis

zsh $dir_scripts/copy.sh $obsid
cd $dir_analysis/analysis
mkdir -p pfiles
export PFILES="$dir_analysis/analysis;$HEADAS/syspfiles"
#zsh $dir_scripts/xtd_screening.sh $obsid $dataclass
zsh $dir_scripts/xtd_imgextract.sh $obsid $dataclass
echo "ok?(y/N): "
read -q
zsh $dir_scripts/xtd_specextract.sh $obsid $dataclass
zsh $dir_scripts/xtd_lcextract.sh $obsid $dataclass
zsh $dir_scripts/xtd_rmf.sh $obsid $dataclass
zsh $dir_scripts/xtd_xaexpmap.sh $obsid $dataclass
zsh $dir_scripts/xtd_xaarfgen.sh $obsid $dataclass
zsh $dir_scripts/grppha.sh ${obsid}xtd_src.pi ${obsid}xtd_srgr1.pi min 1
zsh $dir_scripts/bkg_rmf_arf.sh ${obsid}xtd_srgr1.pi ${obsid}xtd_bgd.pi ${obsid}xtd_p0${dataclass}_src.rmf ${obsid}xtd_p0${dataclass}_ptsrc.arf