#!/usr/bin/env bash
set -euo pipefail

# Usage: ./run_xtend.sh region | run | pipeline | extract
# run: xapipeline followed immediately by extraction (no manual stop)
# region: generate initial regions from indir/xtend/event_cl/*.evt.gz (before xapipeline)
# pipeline: run xapipeline after visually checking/editing regions
# extract: extract spectra/lightcurves and responses from reprocessed events

mode="${1:-}"
if [[ "$mode" != "region" && "$mode" != "run" && "$mode" != "pipeline" && "$mode" != "extract" ]]; then
  echo 'Usage: run_xtend.sh region|run|pipeline|extract' >&2; exit 2
fi

scriptdir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
obsid="${OBSID:-xa902003010}"
dataclass="${DATACLASS:-31100010}"
raw_obsid="${obsid//[^0-9]/}"
indir="${INDIR:-${HOME}/work/analysis/xrism/rawdata/astroquery/obs/rev3/${obsid:2:1}/${raw_obsid}}"
outdir="${OUTDIR:-xtd_reproc}"
regiondir="${REGIONDIR:-xtd_regions}"
mkdir -p "$regiondir"
regiondir="$(cd "$regiondir" && pwd)"
# Do not create OUTDIR before xapipeline: clobber=no may reject it.
# OUTDIR can remain a relative path for xapipeline.
pfiles_dir="$(mktemp -d "${TMPDIR:-/tmp}/xtend-pfiles.XXXXXX")"
trap 'rm -rf "$pfiles_dir"' EXIT
export PFILES="${pfiles_dir};${HEADAS:?Please initialize HEASoft}/syspfiles"
export HEADASNOQUERY=1
export HEADASPROMPT=/dev/null

evt="${obsid}xtd_p0${dataclass}_cl.evt"

if [[ "$mode" == "region" ]]; then
  # Intentionally read the original archive BEFORE reprocessing. Do not
  # silently fall back to pipeline output: the review belongs before pipeline.
  event_for_regions=""
  for candidate in \
    "$indir/xtend/event_cl/$evt.gz" \
    "$indir/xtend/event_cl/$evt"; do
    if [[ -f "$candidate" ]]; then
      event_for_regions="$candidate"
      break
    fi
  done
  [[ -n "$event_for_regions" ]] || {
    echo "No cleaned event in $indir/xtend/event_cl ($evt[.gz])" >&2
    exit 1
  }
  echo "Initial region source: $event_for_regions"
  python3 "$scriptdir/make_xtd_region.py" "$event_for_regions" "$dataclass" --outdir "$regiondir"
  echo "Inspect/edit $regiondir/region_xtd_src.reg and region_xtd_bgd.reg with DS9."
  echo 'Then run: ./run_xtend.sh run'
  exit 0
fi

if [[ "$mode" == "run" || "$mode" == "pipeline" ]]; then
  # Require the editable regions to exist. Visual approval is a user step.
  for name in src bgd; do
    [[ -s "$regiondir/region_xtd_${name}.reg" ]] || {
      echo "Missing region_xtd_${name}.reg. Run region first and inspect it." >&2
      exit 1
    }
  done
  # Pipeline owns the output directory. Do not pre-create it with regions.
  if [[ -e "$outdir" ]]; then
    echo "Output path already exists: $outdir" >&2
    echo "With clobber=no, choose a fresh OUTDIR or handle the existing pipeline output separately." >&2
    exit 1
  fi
  punlearn xapipeline
  xapipeline indir="$indir" outdir="$outdir" steminputs="$obsid" stemoutputs=DEFAULT \
    entry_stage=1 exit_stage=3 instrument=xtend verify_input=no create_ehkmkf=no \
    calc_pointing=yes calc_optaxis=yes seed=650504 clobber=no
  [[ -d "$outdir" ]] || { echo "xapipeline finished but output directory is missing: $outdir" >&2; exit 1; }
  # Only after successful xapipeline: place reviewed region files in its output.
  cp -- "$regiondir/region_xtd_src.reg" "$regiondir/region_xtd_bgd.reg" "$outdir/"
  mkdir -p "$outdir/log_xapipeline_xtd"
  shopt -s nullglob
  for log in coordpnt.log xa*.log; do
    [[ -f "$log" ]] && mv -f "$log" "$outdir/log_xapipeline_xtd/"
  done
  shopt -u nullglob
  if [[ "$mode" == "pipeline" ]]; then
    echo 'Pipeline finished. Run: ./run_xtend.sh extract'
    exit 0
  fi
  echo 'Pipeline finished; starting extraction automatically.'
fi

# For standalone extract, stage reviewed regions if necessary.
[[ -d "$outdir" ]] || { echo "Missing reprocessed directory: $outdir" >&2; exit 1; }
for name in src bgd; do
  if [[ ! -s "$outdir/region_xtd_${name}.reg" ]]; then
    [[ -s "$regiondir/region_xtd_${name}.reg" ]] || { echo "Missing reviewed region: $regiondir/region_xtd_${name}.reg" >&2; exit 1; }
    cp -- "$regiondir/region_xtd_${name}.reg" "$outdir/"
  fi
done
cd "$outdir"
# XSELECT/xaexpmap are run on reprocessed events, not silently on input raw data.
if [[ ! -f "$evt" && -f "$evt.gz" ]]; then
  echo "Decompressing pipeline cleaned event into working directory: $evt.gz"
  gzip -dk "$evt.gz"
fi
for required in "$evt" region_xtd_src.reg region_xtd_bgd.reg; do
  [[ -f "$required" ]] || { echo "Missing $outdir/$required (run region, inspect, and run pipeline first)" >&2; exit 1; }
done

# ATTENTION: xselect SKY filtering expects fk5 RA/DEC regions.
xselect <<EOF
xsel
no
read eve ${evt} .
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
xaexpmap ehkfile="${obsid}.ehk" gtifile="$evt" \
 instrume=XTEND badimgfile="${obsid}xtd_p0${dataclass}.bimg" \
 pixgtifile=NONE outfile="${obsid}xtd_a0${dataclass}.expo" \
 outmaptype=EXPOSURE delta=20.0 numphi=1 stopsys=SKY instmap=CALDB qefile=CALDB \
 contamifile=CALDB vigfile=CALDB obffile=CALDB fwfile=CALDB gvfile=CALDB maskcalsrc=yes \
 fwtype=FILE specmode=MONO specfile=spec.fits specform=FITS evperchan=DEFAULT abund=1 \
 cols=0 covfac=1 clobber=yes chatter=1 logfile="make_expo_${obsid}xtd_p0${dataclass}.log"

fparkey fitsfile="${obsid}xtd_a0${dataclass}.expo" keyword=OPTAOFFX value=0.0 comm='optical axisX offset reset to 0'
fparkey fitsfile="${obsid}xtd_a0${dataclass}.expo" keyword=OPTAOFFY value=0.0 comm='optical axisY offset reset to 0'

punlearn xtdrmf
xtdrmf infile="${obsid}xtd_src.pi" outfile="${obsid}xtd_p0${dataclass}_src.rmf" \
 rmfparam=CALDB eminin=200 dein='2,24' nchanin='5900,500' eminout=0 deout=6 nchanout=4096

# Read nominal sky position from the cleaned FITS primary header.
ftkeypar "$evt[0]" RA_NOM
source_ra="$(pget ftkeypar rvalue)"
ftkeypar "$evt[0]" DEC_NOM
source_dec="$(pget ftkeypar rvalue)"

punlearn xaarfgen
xaarfgen xrtevtfile="raytrace_${obsid}xtd_p0${dataclass}_boxreg_ptsrc.fits" \
 source_ra="$source_ra" source_dec="$source_dec" telescop=XRISM instrume=XTEND \
 emapfile="${obsid}xtd_a0${dataclass}.expo" regmode=RADEC \
 regionfile=region_xtd_src.reg sourcetype=POINT \
 rmffile="${obsid}xtd_p0${dataclass}_src.rmf" erange='0.3 18.0 2.0 8.0' \
 outfile="${obsid}xtd_p0${dataclass}_ptsrc.arf" numphoton=300000 minphoton=100 \
 teldeffile=CALDB qefile=CALDB contamifile=CALDB obffile=CALDB fwfile=CALDB \
 onaxisffile=CALDB onaxiscfile=CALDB mirrorfile=CALDB obstructfile=CALDB \
 frontreffile=CALDB backreffile=CALDB pcolreffile=CALDB \
 scatterfile=CALDB mode=h clobber=yes seed=7 imgfile=NONE

ftgrouppha infile="${obsid}xtd_src.pi" outfile="${obsid}xtd_srcgrp30.pi" grouptype=min groupscale=30
fparkey "${obsid}xtd_p0${dataclass}_src.rmf" "${obsid}xtd_srcgrp30.pi" RESPFILE
fparkey "${obsid}xtd_p0${dataclass}_ptsrc.arf" "${obsid}xtd_srcgrp30.pi" ANCRFILE
fparkey "${obsid}xtd_bgd.pi" "${obsid}xtd_srcgrp30.pi" BACKFILE
