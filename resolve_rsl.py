from argparse import ArgumentParser
from resolve import ResolveTools

def get_argument():
    argparser = ArgumentParser(description='This is the Resolve data reduction program.')
    argparser.add_argument('-oi', '--obsid', default='xa000162000', help='OBSID')
    argparser.add_argument('-fi', '--filter', default='1000', help='Filter ID')
    argparser.add_argument('-rf', '--rmffile', default='xa000162000rsl_S.rmf ', help='RMF file')
    argparser.add_argument('-ef', '--eventfile', default='xa000162000rsl_p0px1000_cl2.evt', help='Event file')
    argparser.add_argument('-xr', '--xrtevtfile', default='xa000162000rsl_p0px1000_cl2.evt', help='Ray tracing file')
    argparser.add_argument('-em', '--emapfile', default='xa000162000rsl_p0px1000_cl2.evt', help='Ray tracing file')
    argparser.add_argument('-wr', '--whichrmf', default='S', help='RMF size')
    return argparser.parse_args()

if __name__ == "__main__":
    args = get_argument()
    respfile = args.rmffile
    whichrmf = args.whichrmf
    eventfile = args.eventfile
    rsl = ResolveTools("", "", whichrmf)
    #rsl.rsl_mkrmf(eventfile, respfile, whichrmf)
    RA_NOM, DEC_NOM, PA_NOM = rsl.get_radec_nom(eventfile)
    source_ra, source_dec = rsl.rsl_coordpnt(RA_NOM, DEC_NOM, PA_NOM, X0=3.5, Y0=3.5)
    xrtevtfile = 'raytrace_xa000162000rsl_p0px1000_ptsrc.fits'
    emapfile = 'xa000162000rsl_p0px1000.expo'
    ancrfile = 'xa000162000rsl_Ls_excluded_L.arf'
    regionfile = "region_RSL_det_27.reg"
    rsl.rsl_xaarfgen(xrtevtfile=xrtevtfile, emapfile=emapfile, respfile=respfile, ancrfile=ancrfile, regionfile=regionfile, source_ra=source_ra, source_dec=source_dec)