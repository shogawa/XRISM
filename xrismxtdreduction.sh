#!/bin/sh

pfiles_dir=pfiles`date "+%Y%m%d%H%M%S"`
mkdir -p $pfiles_dir
pfiles_dir=`pwd`/${pfiles_dir}
export PFILES="${pfiles_dir};$HEADAS/syspfiles"
export HEADASNOQUERY=
export HEADASPROMPT=/dev/null

obsid=xa902003010
dataclass=31100010
indir=${HOME}/work/analysis/xrism/rawdata/astroquery/obs/rev3/${obsid:2:1}/${obsid//[^0-9]/}
outdir=xtd_reproc

punlearn xapipeline
xapipeline indir=${indir} outdir=${outdir} steminputs=${obsid} stemoutputs=DEFAULT \
entry_stage=1 exit_stage=3 instrument=xtend verify_input=no create_ehkmkf=no calc_pointing=yes \
calc_optaxis=yes seed=650504 clobber=no

mkdir -p ${outdir}/log_xapipeline_xtd
mv coordpnt.log xa*.log ${outdir}/log_xapipeline_xtd

cp region_xtd_src.reg region_xtd_bgd.reg ${outdir}
cd ${outdir}

xselect<<EOF
xsel
no
read eve ${obsid}xtd_p0${dataclass}_cl.evt .
./
yes
set image sky
filter region region_xtd_bgd.reg
filter pha_cutoff 83 1667
set binsize 128.0
extr curve exposure=0.6
save curve ${obsid}xtd_0p5to10keV_b128_bgd_lc.fits clobber=yes
clear pha_cutoff
extr spectrum
save spectrum ${obsid}xtd_bgd.pi clobber=yes
clear region
filter region region_xtd_src.reg
filter pha_cutoff 83 1667
extr curve exposure=0.6
save curve ${obsid}xtd_0p5to10keV_b128_src_lc.fits clobber=yes
extract image
save image ${obsid}xtd_p0${dataclass}_src_skyimg.fits clobber=yes
clear pha_cutoff
extr spectrum
save spectrum ${obsid}xtd_src.pi clobber=yes
exit
no
EOF


punlearn xaexpmap

xaexpmap ehkfile=${obsid}.ehk gtifile=${obsid}xtd_p0${dataclass}_cl.evt \
instrume=XTEND badimgfile=${obsid}xtd_p0${dataclass}.bimg \
pixgtifile=NONE outfile=${obsid}xtd_a0${dataclass}.expo \
outmaptype=EXPOSURE delta=20.0 numphi=1 stopsys=SKY instmap=CALDB qefile=CALDB \
contamifile=CALDB vigfile=CALDB obffile=CALDB fwfile=CALDB gvfile=CALDB maskcalsrc=yes \
fwtype=FILE specmode=MONO specfile=spec.fits specform=FITS evperchan=DEFAULT abund=1 \
cols=0 covfac=1 clobber=yes chatter=1 logfile=make_expo_${obsid}xtd_p0${dataclass}.log

fparkey fitsfile=${obsid}xtd_a0${dataclass}.expo keyword=OPTAOFFX value=0.0 comm="optical axisX offset reset to 0"
fparkey fitsfile=${obsid}xtd_a0${dataclass}.expo keyword=OPTAOFFY value=0.0 comm="optical axisY offset reset to 0"

punlearn xtdrmf
xtdrmf infile=${obsid}xtd_src.pi outfile=${obsid}xtd_p0${dataclass}_src.rmf \
rmfparam=CALDB eminin=200 dein="2,24" nchanin="5900,500" eminout=0 deout=6 nchanout=4096

RA_NOM=`fkeyprint ${obsid}xtd_p0${dataclass}_cl.evt+0 RA_NOM | grep Nominal | awk '{print $3}'`
DEC_NOM=`fkeyprint ${obsid}xtd_p0${dataclass}_cl.evt+0 DEC_NOM | grep Nominal | awk '{print $3}'`

punlearn xaarfgen
xaarfgen xrtevtfile=raytrace_${obsid}xtd_p0${dataclass}_boxreg_ptsrc.fits \
source_ra=${RA_NOM} source_dec=${DEC_NOM} telescop=XRISM instrume=XTEND \
emapfile=${obsid}xtd_a0${dataclass}.expo regmode=RADEC \
regionfile=region_xtd_src.reg  sourcetype=POINT \
rmffile=${obsid}xtd_p0${dataclass}_src.rmf erange="0.3 18.0 2.0 8.0" \
outfile=${obsid}xtd_p0${dataclass}_ptsrc.arf numphoton=300000 minphoton=100 \
teldeffile=CALDB qefile=CALDB contamifile=CALDB obffile=CALDB fwfile=CALDB \
onaxisffile=CALDB onaxiscfile=CALDB mirrorfile=CALDB obstructfile=CALDB \
frontreffile=CALDB backreffile=CALDB pcolreffile=CALDB \
scatterfile=CALDB mode=h clobber=yes seed=7 imgfile=NONE

ftgrouppha infile=${obsid}xtd_src.pi outfile=${obsid}xtd_srcgrp30.pi grouptype=min groupscale=30
fparkey ${obsid}xtd_p0${dataclass}_src.rmf ${obsid}xtd_srcgrp30.pi RESPFILE
fparkey ${obsid}xtd_p0${dataclass}_ptsrc.arf ${obsid}xtd_srcgrp30.pi ANCRFILE
fparkey ${obsid}xtd_bgd.pi ${obsid}xtd_srcgrp30.pi BACKFILE

rm -fr $pfiles_dir

