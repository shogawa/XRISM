#!/bin/sh

export TOOLS=/home/ogawa/work/tools

export HEADAS=$TOOLS/heasoft/XRISM_15Oct2023_Build7/x86_64-pc-linux-gnu-libc2.31
. $HEADAS/headas-init.sh

export CALDB=$TOOLS/caldb
. $CALDB/software/tools/caldbinit.sh

export XSELECT_MDB=$TOOLS/heasoft/xrism/xselect.mdb.xrism

dir_analysis=$1
obsid=$2
dataclass=$3
dir_scripts=`pwd`
cd $dir_analysis

sh $dir_scripts/xtd_copy.sh $obsid
#sh $dir_scripts/xtd_screening.sh $obsid $dataclass
sh $dir_scripts/xtd_imgextract.sh $obsid $dataclass
sh $dir_scripts/xtd_specextract.sh $obsid $dataclass
#sh $dir_scripts/xtd_lcextract.sh $obsid $dataclass
sh $dir_scripts/xtd_rmf.sh $obsid $dataclass
sh $dir_scripts/xtd_xaexpmap.sh $obsid $dataclass
sh $dir_scripts/xtd_xaarfgen.sh $obsid $dataclass
ftgrouppha infile=${obsid}xtd_src.pi outfile=${obsid}xtd_srgr1.pi grouptype=min groupscale=1
fparkey ${obsid}xtd_bgd.pi ${obsid}xtd_src.pi BACKFILE
fparkey ${obsid}xtd_p0${dataclass}_src.rmf ${obsid}xtd_src.pi RESPFILE
fparkey ${obsid}xtd_p0${dataclass}_ptsrc.arf ${obsid}xtd_src.pi ANCRFILE
ftgrouppha infile=${obsid}xtd_src.pi outfile=${obsid}xtd_srgr1.pi  backfile=${obsid}xtd_bgd.pi respfile=${obsid}xtd_p0${dataclass}_src.rmf grouptype=min groupscale=1
