#!/bin/sh

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
#ftgrouppha infile=${obsid}xtd_src.pi outfile=${obsid}xtd_srgr1.pi grouptype=min groupscale=1
fparkey ${obsid}xtd_bgd.pi ${obsid}xtd_src.pi BACKFILE
fparkey ${obsid}xtd_src.rmf ${obsid}xtd_src.pi RESPFILE
fparkey ${obsid}xtd_src.arf ${obsid}xtd_src.pi ANCRFILE
ftgrouppha infile=${obsid}xtd_src.pi outfile=${obsid}xtd_srgr1.pi backfile=${obsid}xtd_bgd.pi respfile=${obsid}xtd_src.rmf grouptype=min groupscale=1
