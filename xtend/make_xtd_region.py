#!/usr/bin/env python3
"""Seed Xtend source/background regions. Python stdlib + HEASoft coordpnt.

This is a geometric INITIAL GUESS, not an exposure/source-contamination test.
"""
import argparse
import gzip
import math
import re
import shutil
import struct
import subprocess
from collections import defaultdict
from pathlib import Path


def header(stream):
    cards = []
    while True:
        block = stream.read(2880)
        if len(block) != 2880:
            raise ValueError('Invalid/truncated FITS header')
        part = [block[i:i+80].decode('ascii', 'replace') for i in range(0, 2880, 80)]
        cards.extend(part)
        if any(c[:8].strip() == 'END' for c in part):
            break
    values = {}
    for c in cards:
        if c[8:10] == '= ':
            raw = c[10:].split('/')[0].strip()
            values[c[:8].strip()] = raw.strip("' ")
    return values


def event_info(filename):
    op = gzip.open if str(filename).endswith('.gz') else open
    with op(filename, 'rb') as stream:
        hdr = header(stream)
        while True:
            size = (int(hdr.get('NAXIS1', 0))*int(hdr.get('NAXIS2', 0)) + int(hdr.get('PCOUNT', 0)))
            if hdr.get('EXTNAME', '').upper() == 'EVENTS':
                break
            stream.seek(((size + 2879)//2880)*2880, 1)
            hdr = header(stream)
        cols, offset = {}, 0
        for i in range(1, int(hdr['TFIELDS'])+1):
            form = hdr[f'TFORM{i}'].strip()
            match = re.fullmatch(r'(\d*)([LXBIJKAEDCM])', form)
            if not match:
                raise ValueError(f'Unsupported TFORM: {form}')
            count = int(match[1] or 1)
            code = match[2]
            width = ((count+7)//8 if code == 'X' else count*{'L':1,'B':1,'I':2,'J':4,'K':8,'A':1,'E':4,'D':8,'C':8,'M':16}[code])
            cols[hdr[f'TTYPE{i}'].strip()] = (offset, code, count)
            offset += width
        if not {'DETX','DETY','CCD_ID','PI'}.issubset(cols):
            raise ValueError('EVENTS lacks DETX, DETY, CCD_ID or PI')
        if offset != int(hdr['NAXIS1']):
            raise ValueError('FITS row size mismatch')
        rowlen = int(hdr['NAXIS1'])
        rows = int(hdr['NAXIS2'])
        # Sample fixed-stride events for CCD coverage, rather than reading every
        # source-dominated event. Still a finite approximate occupancy estimate.
        stride = max(1, rows // 100000)
        selected = []
        fmt = {'B':'B','I':'h','J':'i','K':'q'}
        def get(row, key):
            pos, code, count = cols[key]
            if code not in fmt or count != 1:
                raise ValueError(f'Unsupported event column {key}: {code}{count}')
            return struct.unpack_from('>'+fmt[code], row, pos)[0]
        for idx in range(rows):
            row = stream.read(rowlen)
            if len(row) != rowlen:
                raise ValueError('Truncated FITS EVENTS')
            if idx % stride: continue
            pi = get(row,'PI')
            if 83 <= pi <= 1667:
                selected.append((get(row,'DETX'), get(row,'DETY'), get(row,'CCD_ID')))
        return hdr, selected


def coord_point(x, y, ra, dec, pa, start, stop):
    cmd = ['coordpnt', f'input={x:.10f},{y:.10f}', 'outfile=NONE',
           'telescop=XRISM', 'instrume=XTEND', 'teldeffile=CALDB',
           f'startsys={start}', f'stopsys={stop}',
           f'ra={ra:.12f}', f'dec={dec:.12f}', f'roll={pa:.12f}',
           f'ranom={ra:.12f}', f'decnom={dec:.12f}', 'rollnom=0',
           'chatter=2']
    p = subprocess.run(cmd, text=True, stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, check=True)
    m = re.search(r'OUTX\s+OUTY\s*=\s*([-+\d.eE]+)\s+([-+\d.eE]+)', p.stdout)
    if not m:
        raise RuntimeError('Cannot parse coordpnt output:\n' + p.stdout)
    return float(m.group(1)), float(m.group(2))


def coord_region(det_file, out_file, ra, dec, pa):
    cmd = ['coordpnt', f'input={det_file}', f'outfile={out_file}',
           'telescop=XRISM', 'instrume=XTEND', 'teldeffile=CALDB',
           'startsys=DET', 'stopsys=RADEC',
           f'ra={ra:.12f}', f'dec={dec:.12f}', f'roll={pa:.12f}',
           f'ranom={ra:.12f}', f'decnom={dec:.12f}', 'rollnom=0',
           'clobber=yes']
    subprocess.run(cmd, check=True)


def percentile(vals, f):
    a = sorted(vals)
    return a[int((len(a)-1)*f)]


def pick_background(events, sx, sy, half_x, half_y, radius, full):
    per = defaultdict(list)
    for x,y,c in events:
        per[c].append((x,y))
    if not per: raise ValueError('No sampled PI=83..1667 events')
    # Source CCD: nearest local events, rather than largest CCD count overall.
    nearby = {c:sum((x-sx)**2+(y-sy)**2 <= 45**2 for x,y in pts)
              for c,pts in per.items()}
    ccd = max(nearby, key=nearby.get)
    if nearby[ccd] == 0: raise ValueError('No events near source DET position; inspect pointing')
    pts = per[ccd]
    xmin,xmax = percentile([x for x,y in pts], .001),percentile([x for x,y in pts], .999)
    ymin,ymax = percentile([y for x,y in pts], .001),percentile([y for x,y in pts], .999)
    # DET box is aligned with DET axes, width 120 arcsec, height 300 arcsec.
    # Require a 5 px margin from percentile-derived boundaries.
    hx = radius if full else half_x
    hy = radius if full else half_y
    margin = 0
    lo_x,hi_x = xmin+hx+margin,xmax-hx-margin
    lo_y,hi_y = ymin+hy+margin,ymax-hy-margin
    if hi_x < lo_x or hi_y < lo_y:
        raise ValueError(f'CCD {ccd} sampled bounding box too thin to fit the region. Manual placement required.')
    candidates=[]
    # step ~half width/height. Source overlap excluded by inflated half-widths.
    step_x=max(8,int(hx))
    step_y=max(12,int(hy))
    for xi in range(math.ceil(lo_x),math.floor(hi_x)+1,step_x):
        for yi in range(math.ceil(lo_y),math.floor(hi_y)+1,step_y):
            if full:
                if math.hypot(xi-sx,yi-sy) < 2*radius+20: continue
            elif abs(xi-sx)<2*hx+15 and abs(yi-sy)<2*hy+15: continue
            # crude count density as a diagnostic only; do not mistake empty
            # unexposed bins for good background: require nearby detections.
            in_reg = sum(((x-xi)**2+(y-yi)**2 <= radius**2) if full else
                         (abs(x-xi)<=hx and abs(y-yi)<=hy) for x,y in pts)
            neighborhood = sum(abs(x-xi)<hx+20 and abs(y-yi)<hy+20 for x,y in pts)
            if neighborhood < 10: continue
            distance=math.hypot(xi-sx, yi-sy)
            candidates.append((in_reg, -neighborhood, -distance, xi, yi))
    if not candidates:
        raise ValueError('No credible same-CCD BG candidate found. Manual placement required.')
    # Avoid trivially zero density: prioritize quiet region near sampled data.
    candidates.sort()
    _,_,_,bx,by = candidates[0]
    return ccd,bx,by,(xmin,xmax,ymin,ymax),nearby


def write_if_absent(path, content):
    if path.exists():
        print(f'KEEP manually editable file: {path}')
    else:
        path.write_text(content)
        print(f'CREATED: {path}')


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('events',type=Path)
    ap.add_argument('dataclass')
    ap.add_argument('--pixscale',type=float,default=1.77,
                    help='approximate XTEND DET arcsec/pixel; verify for current CALDB')
    ap.add_argument('--bg-detx',type=float,help='manual background DETX override')
    ap.add_argument('--bg-dety',type=float,help='manual background DETY override')
    ap.add_argument('--outdir',type=Path,default=Path('.'))
    a=ap.parse_args()
    a.outdir.mkdir(parents=True,exist_ok=True)
    hdr,events=event_info(a.events)
    ra,dec,pa=(float(hdr[k]) for k in ['RA_NOM','DEC_NOM','PA_NOM'])
    full=a.dataclass.startswith('300')
    sx,sy=coord_point(ra,dec,ra,dec,pa,'RADEC','DET')
    radius=150/a.pixscale
    hx=60/a.pixscale
    hy=150/a.pixscale
    ccd,bx,by,bounds,nearby=pick_background(events,sx,sy,hx,hy,radius,full)
    if a.bg_detx is not None: bx=a.bg_detx
    if a.bg_dety is not None: by=a.bg_dety
    if full:
        src_det=f'circle({sx:.6f},{sy:.6f},{radius:.6f})\n'
        bg_det=f'circle({bx:.6f},{by:.6f},{radius:.6f})\n'
        src_sky=f'fk5\ncircle({ra:.10f},{dec:.10f},150")\n'
    else:
        src_det=f'box({sx:.6f},{sy:.6f},{2*hx:.6f},{2*hy:.6f},0)\n'
        bg_det=f'box({bx:.6f},{by:.6f},{2*hx:.6f},{2*hy:.6f},0)\n'
        # Preserve original, reportedly correct SKY source shape/orientation.
        src_sky=f'fk5\nbox({ra:.10f},{dec:.10f},120",300",{pa:.9f})\n'
    root=a.outdir
    for name,contents in [('region_xtd_src_auto_det.reg',src_det),
                          ('region_xtd_bgd_auto_det.reg',bg_det)]:
        (root/name).write_text(contents)
    # Convert DET geometry as an independent overlay reference. Preserve the
    # source's established fk5 shape/angle for the actual background region.
    coord_region(root/'region_xtd_bgd_auto_det.reg',
                 root/'region_xtd_bgd_det_converted.reg',ra,dec,pa)
    bg_ra,bg_dec=coord_point(bx,by,ra,dec,pa,'DET','RADEC')
    if full:
        bg_sky=f'fk5\ncircle({bg_ra:.10f},{bg_dec:.10f},150")\n'
    else:
        bg_sky=f'fk5\nbox({bg_ra:.10f},{bg_dec:.10f},120",300",{pa:.9f})\n'
    (root/'region_xtd_bgd_auto.reg').write_text(bg_sky)
    (root/'region_xtd_src_auto.reg').write_text(src_sky)
    # Never overwrite edited files.
    for name in ['src','bgd']:
        final=root/f'region_xtd_{name}.reg'
        auto=root/f'region_xtd_{name}_auto.reg'
        if not final.exists(): shutil.copyfile(auto,final)
        else: print('KEEP manually edited:',final)
    print(f'dataclass={a.dataclass}, mode={"FULL circle" if full else "WINDOW box"}')
    print(f'Source DET=({sx:.2f},{sy:.2f}); CCD_ID={ccd}, near counts={dict(nearby)}')
    print(f'Background candidate DET=({bx:.2f},{by:.2f}), sampled CCD bounds={bounds}')
    print('CAUTION: check source alignment, CCD boundaries, exposure, other sources in DS9.')
    print('NOTE: DET box axes and nominal SKY source box may differ: verify both.')


if __name__=='__main__':
    main()
