#!/bin/sh

export TOOLS=/home/ogawa/work/tools

export HEADAS=$TOOLS/heasoft/XRISM_15Oct2023_Build7/x86_64-pc-linux-gnu-libc2.31
. $HEADAS/headas-init.sh

export CALDB=$TOOLS/caldb
. $CALDB/software/tools/caldbinit.sh

export XSELECT_MDB=$TOOLS/heasoft/xrism/xselect.mdb.xrism

dir_analysis=$1
obsid=$2
lcbin=128
dir_scripts=`pwd`
cd $dir_analysis

mkdir -p each_pixel

for pix in `seq 0 35`
do
if [ $pix = 12 ]; then
echo "pix = $pix"
else
pix0=`printf "%02d" ${pix}`
sh $dir_scripts/rsl_specextract_pix.sh $obsid $pix
sh $dir_scripts/rsl_lcextract_pix.sh $obsid $pix $lcbin
sh $dir_scripts/rsl_rmf_pix.sh $obsid $pix
sh $dir_scripts/rsl_xaarfgen_pix.sh $obsid ${obsid}rsl_pix${pix0}_S.rmf $pix
mv ${obsid}rsl_pix${pix0}.pha ${obsid}rsl_pix${pix0}_S.rmf ${obsid}rsl_${pix0}_S.arf region_RSL_det_pix${pix0}.reg ${obsid}rsl_pix${pix0}_b${lcbin}_lc.fits each_pixel
cd each_pixel
ftgrouppha infile=${obsid}rsl_pix${pix0}.pha outfile=${obsid}rsl_pix${pix0}gr1.pha grouptype=min groupscale=1
fparkey NONE ${obsid}rsl_pix${pix0}gr1.pha BACKFILE
fparkey ${obsid}rsl_pix${pix0}_S.rmf ${obsid}rsl_pix${pix0}gr1.pha RESPFILE
fparkey ${obsid}rsl_pix${pix0}_S.arf ${obsid}rsl_pix${pix0}gr1.pha ANCRFILE
cd ../
fi
done