#!/bin/sh

pfiles_dir=pfiles`date "+%Y%m%d%H%M%S"`
mkdir -p $pfiles_dir
pfiles_dir=`pwd`/${pfiles_dir}
export PFILES="${pfiles_dir};$HEADAS/syspfiles"
export HEADASNOQUERY=
export HEADASPROMPT=/dev/null

obsid=xa902003010
indir=${HOME}/work/analysis/xrism/rawdata/astroquery/obs/rev3/${obsid:2:1}/${obsid//[^0-9]/}
outdir=rsl_reproc

punlearn xapipeline
xapipeline indir=${indir} outdir=${outdir} steminputs=${obsid} \
stemoutputs=DEFAULT entry_stage=1 exit_stage=3 instrument=resolve verify_input=no \
create_ehkmkf=no calc_pointing=yes calc_optaxis=yes calc_gtilost=no calc_adrgti=no \
calc_mxsgti=no rsl_gainfile=CALDB calmethod=FE55 linetocorrect=MnKa seed=650504 \
numevent=1000 minevent=200 extraspread=40 spangti=no

mkdir -p ${outdir}/log_xapipeline_rsl
mv coordpnt.log xa*.log ${outdir}/log_xapipeline_rsl

cd ${outdir}


ftcopy infile="${obsid}rsl_p0px1000_cl.evt[EVENTS][(PI>=600) && (((((RISE_TIME+0.00075*DERIV_MAX)>46)&&((RISE_TIME+0.00075*DERIV_MAX)<58)) &&ITYPE<4)||(ITYPE==4))&&STATUS[4]==b0]" outfile=${obsid}rsl_p0px1000_cl2.evt copyall=yes clobber=yes history=yes

xselect<<EOF
xsel
no
read event ${obsid}rsl_p0px1000_cl2.evt
./
yes
filter column "PIXEL=0:11,13:26,28:35"
filter GRADE "0:0"
extract spectrum
save spec ${obsid}rsl_src.pi clobber=yes
exit
no
EOF

punlearn xaexpmap

xaexpmap ehkfile=${obsid}.ehk gtifile=${obsid}rsl_p0px1000_cl2.evt \
instrume=RESOLVE badimgfile=NONE pixgtifile=${obsid}rsl_px1000_exp.gti \
outfile=${obsid}rsl_p0px1000.expo outmaptype=EXPOSURE delta=20.0 numphi=1 \
stopsys=SKY instmap=CALDB qefile=CALDB contamifile=CALDB vigfile=CALDB obffile=CALDB \
fwfile=CALDB gvfile=CALDB maskcalsrc=yes fwtype=FILE specmode=MONO specfile=spec.fits \
specform=FITS evperchan=DEFAULT abund=1 cols=0 covfac=1 clobber=yes chatter=1 \
logfile=make_expo_${obsid}rsl_p0px1000.log

fparkey fitsfile=${obsid}rsl_p0px1000.expo keyword=OPTAOFFX value=0.0 comm="optical axis X offset reset to 0"
fparkey fitsfile=${obsid}rsl_p0px1000.expo keyword=OPTAOFFY value=0.0 comm="optical axis Y offset reset to 0"

ftcopy infile="${obsid}rsl_p0px1000_cl2.evt[EVENTS][(PI>=6000)&&(PI<=20000)&&(ITYPE<4)]" outfile=${obsid}rsl_p0px1000_UPR.evt copyall=yes clobber=yes history=yes

rm -rf $pfiles_dir/xaarfgen.par
rm -rf $pfiles_dir/xaxmaarfgen.par

RA_NOM=`fkeyprint ${obsid}rsl_p0px1000_cl.evt+0 RA_NOM | grep Nominal | awk '{print $3}'`
DEC_NOM=`fkeyprint ${obsid}rsl_p0px1000_cl.evt+0 DEC_NOM | grep Nominal | awk '{print $3}'`
PA_NOM=`fkeyprint ${obsid}rsl_p0px1000_cl.evt+0 PA_NOM | grep Nominal | awk '{print $3}'`

RDETX0=3.5
RDETY0=3.5

coordpnt=`coordpnt input="$RDETX0,$RDETY0" outfile=NONE telescop=XRISM instrume=RESOLVE teldeffile=CALDB startsys=DET stopsys=RADEC ra=${RA_NOM} dec=${DEC_NOM} roll=${PA_NOM} ranom=${RA_NOM} decnom=${DEC_NOM} clobber=yes`

ra=$(echo "$coordpnt" | awk '{print $4}')
dec=$(echo "$coordpnt" | awk '{print $5}')


punlearn rslmkrsp
rslmkrsp inevtfile=${obsid}rsl_p0px1000_cl2.evt \
xrtevtfile=raytrace_${obsid}rsl_p0px1000_ptsrc.fits source_ra=$ra source_dec=$dec \
emapfile=${obsid}rsl_p0px1000.expo regionfile=NONE, pixlist=0-11,13-26,28-35 sourcetype=POINT \
imgfile=NONE useingrd=yes erange="0.3 18.0 2 8" numphoton=300000 minphoton=100 teldeffile=CALDB qefile=CALDB \
contamifile=CALDB obffile=CALDB fwfile=CALDB gatevalvefile=CALDB onaxisffile=CALDB onaxiscfile=CALDB \
mirrorfile=CALDB obstructfile=CALDB frontreffile=CALDB backreffile=CALDB pcolreffile=CALDB \
scatterfile=CALDB seed=10439 outfileroot=${obsid}rsl_X_UPR whichrmf=X \
resolist="0" splitrmf=yes splitcomb=yes elcbinfac=16 includels=no gfelo=3.0 gfehi=10.0 clobber=yes logfile=rslmkrsp_UPR.log

punlearn rslmkrsp
rslmkrsp inevtfile=${obsid}rsl_p0px1000_cl2.evt \
xrtevtfile=raytrace_${obsid}rsl_p0px1000_ptsrc.fits source_ra=$ra source_dec=$dec \
emapfile=${obsid}rsl_p0px1000.expo regionfile=NONE, pixlist=0-11,13-26,28-35 sourcetype=POINT \
imgfile=NONE useingrd=yes erange="0.3 18.0 2 8" numphoton=300000 minphoton=100 teldeffile=CALDB qefile=CALDB \
contamifile=CALDB obffile=CALDB fwfile=CALDB gatevalvefile=CALDB onaxisffile=CALDB onaxiscfile=CALDB \
mirrorfile=CALDB obstructfile=CALDB frontreffile=CALDB backreffile=CALDB pcolreffile=CALDB \
scatterfile=CALDB seed=10439 outfileroot=${obsid}rsl_X whichrmf=X \
resolist="0" splitrmf=yes splitcomb=yes elcbinfac=16 includels=yes gfelo=3.0 gfehi=10.0 clobber=yes

phafile=${obsid}rsl_src.pi
backfile=NONE
respfile=${obsid}rsl_X_UPR_comb.rsp
arffile=NONE

outgrpphafile=`echo $phafile | sed 's/.pi/_grpobin.pi/'`

ftgrouppha infile=$phafile backfile=$backfile respfile=$respfile outfile=$outgrpphafile grouptype=opt clobber=yes 

fparkey ${respfile} ${outgrpphafile} RESPFILE


rm -rf $pfiles_dir
