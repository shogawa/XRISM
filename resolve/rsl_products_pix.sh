#!/bin/sh

export HEADAS=$TOOLS/heasoft/XRISM_15Oct2023_Build7/x86_64-pc-linux-gnu-libc2.31
. $HEADAS/headas-init.sh

export CALDB=$TOOLS/caldb
. $CALDB/software/tools/caldbinit.sh

export XSELECT_MDB=$TOOLS/heasoft/xselect.mdb.xrism

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
mv ${obsid}rsl_pix${pix0}.pha ${obsid}rsl_pix${pix0}_S.rmf ${obsid}rsl_p0px1000_ptsrc_pix${pix0}.arf region_RSL_det_pix${pix0}.reg ${obsid}rsl_pix${pix0}_b${lcbin}_lc.fits each_pixel
cd each_pixel
sh $dir_scripts/grppha.sh ${obsid}rsl_pix${pix0}.pha ${obsid}rsl_pix${pix0}gr1.pha min 1
sh $dir_scripts/bkg_rmf_arf.sh ${obsid}rsl_pix${pix0}gr1.pha NONE ${obsid}rsl_pix${pix0}_S.rmf ${obsid}rsl_p0px1000_ptsrc_pix${pix0}.arf
cd ../
fi
done