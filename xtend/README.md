# XTEND: regions before reprocessing

Requires initialized HEASoft / XRISM CALDB, Python 3 standard library, and DS9 for review.
Run all commands in the folder containing `run_xtend.sh` and `make_xtd_region.py`.

## Why regions live outside xapipeline output

`xapipeline` with `clobber=no` must own creation of `xtd_reproc`. `region` writes to `xtd_regions` instead. `run` checks the output directory does not already exist; after successful pipeline execution it copies the manually reviewed regions into `xtd_reproc` and immediately extracts products. Standalone `extract` copies any missing reviewed regions to existing output. Use `REGIONDIR` to override the region staging directory. Do not pre-create `xtd_reproc`.

## Workflow (in order)

```bash
./run_xtend.sh region
# Open original cleaned events from ${indir}/xtend/event_cl in DS9.
# Inspect and edit xtd_regions/region_xtd_src.reg and region_xtd_bgd.reg.
./run_xtend.sh run   # runs xapipeline -> xselect/xaexpmap/xtdrmf/xaarfgen continuously
```

- **region**: before `xapipeline`, read `${indir}/xtend/event_cl/${obsid}xtd_p0${dataclass}_cl.evt.gz` (or uncompressed `.evt`) directly. Python reads gzip without unzipping. It estimates source DET coordinates with HEASoft `coordpnt`, identifies the nearby `CCD_ID` from event samples, and proposes a same-CCD background from sampled events. The established FK5 source shape and angle are retained.
- **manual review**: open the original events and final editable `.reg` files in DS9. Check source position, CCD/window coverage, gaps, background point-source contamination, and effective exposure. Modify `xtd_regions/region_xtd_src.reg` and `region_xtd_bgd.reg` as necessary. These files are NEVER overwritten by `region`; the `_auto.reg` files are regenerated as suggestions. An event-density estimate is *not* proof of valid effective exposure.
- **run**: after region review, run `xapipeline` and immediately continue to extraction without another manual step. The run stops on a failed command (`set -euo pipefail`).
- **pipeline** (optional): run just the user-updated `xapipeline` command *after* region review. The script checks that editable region files exist but cannot verify whether a human actually reviewed them. Pipeline logs go to `xtd_reproc/log_xapipeline_xtd`.
- **extract**: run the original XSELECT light curves/spectra, exposure map, RMF, ARF and grouped PHA using the reviewed regions and reprocessed cleaned event file, not the original compressed input.

`dataclass.startswith('300')` selects circles with radius 150 arcsec (full window). Other dataclasses use 120 x 300 arcsec boxes (window mode). Same-CCD background selection is approximate and can fail; if it cannot find a candidate the script stops instead of fabricating a valid region. Verify that the internal dataclass mapping matches your datasets.

Default observation:

```text
obsid=xa902003010
 dataclass=31100010
 indir=${HOME}/work/analysis/xrism/rawdata/astroquery/obs/rev3/${obsid:2:1}/${obsid//[^0-9]/}
 outdir=xtd_reproc
```

Overrides: `OBSID`, `DATACLASS`, `INDIR`, `OUTDIR` environment variables.
Example:

```bash
INDIR=/path/to/observation ./run_xtend.sh region
```

For diagnostic placement override, run the Python script directly:

```bash
python3 make_xtd_region.py /path/to/xtend/event_cl/xa902003010xtd_p031100010_cl.evt.gz 31100010 \
  --outdir xtd_regions --bg-detx 735 --bg-dety 400
```

**Validation limitations:** The Bash/Python syntax can be checked here, but HEASoft `coordpnt`, `xapipeline`, CALDB calibration, and end-to-end DS9 region overlays have not been verified here. Before production use, confirm `coordpnt` region conversion and rotation, and inspect the generated region locations. The existing ARF raytrace filename and `spec.fits` settings follow the supplied pipeline and may require supporting files.
