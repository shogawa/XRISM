#! /usr/bin/env python3

from argparse import ArgumentParser
import datetime
import os
import pathlib
import re
import shutil
import subprocess

HEADAS = '/home/ogawa/work/tools/heasoft/XRISM_20Jun2024_Build8/x86_64-pc-linux-gnu-libc2.31'
CALDB = '/home/ogawa/work/tools/caldb'
XSELECT_MDB = '/home/ogawa/work/tools/heasoft/xrism/xselect.mdb.xrism'
rmfparamfile = '/home/ogawa/work/tools/heasoft/xrism/xa_rsl_rmfparam_20190101v006.fits.gz'

def shell_source(script):
    pipe = subprocess.Popen(". %s && env -0" % script, stdout=subprocess.PIPE, shell=True)
    output = pipe.communicate()[0].decode('utf-8')
    output = output[:-1]

    env = {}
    for line in output.split('\x00'):
        line = line.split( '=', 1)
        env[ line[0] ] = line[1]

    os.environ.update(env)

def get_argument():
    argparser = ArgumentParser(description='This is the Resolve data reduction program.')
    argparser.add_argument('-oi', '--obsid', default='xa000162000', help='OBSID')
    argparser.add_argument('-fi', '--filter', default='1000', help='Filter ID')
    argparser.add_argument('-wr', '--whichrmf', default='S', help='RMF size')
    argparser.add_argument('-ed', '--eventdir', default='..', help='Eventfile directory path')
    argparser.add_argument('-pd', '--productsdir', default='.', help='Products directory path')
    return argparser.parse_args()

class ResolveTools:

    def __init__(self, obsid, filter, whichrmf, eventdir='..', productsdir='.'):
        self.obsid = obsid
        self.filter = filter
        self.whichrmf = whichrmf
        self.eventdir =  pathlib.Path(eventdir).resolve()
        self.productsdir =  pathlib.Path(productsdir).resolve()

        self.pixel_map = {
            23:[1,6], 24:[2,6], 26:[3,6], 34:[4,6], 32:[5,6], 30:[6,6],
            21:[1,5], 22:[2,5], 25:[3,5], 33:[4,5], 31:[5,5], 29:[6,5],
            19:[1,4], 20:[2,4], 18:[3,4], 35:[4,4], 28:[5,4], 27:[6,4],
             9:[1,3], 10:[2,3], 17:[3,3],  0:[4,3],  2:[5,3],  1:[6,3],
            11:[1,2], 13:[2,2], 15:[3,2],  7:[4,2],  4:[5,2],  3:[6,2],
            12:[1,1], 14:[2,1], 16:[3,1],  8:[4,1],  6:[5,1],  5:[6,1]
        }

        os.environ['HEADAS'] = HEADAS
        os.environ['CALDB'] = CALDB
        os.environ['XSELECT_MDB'] = XSELECT_MDB

        os.environ['HEADASNOQUERY'] = ''
        os.environ['HEADASPROMPT'] = '/dev/null'
        shell_source(os.environ['HEADAS'] + '/headas-init.sh')
        shell_source(os.environ['CALDB'] + '/software/tools/caldbinit.sh')

        productsdir = pathlib.Path(productsdir).resolve()
        productsdir.mkdir(parents=True, exist_ok=True)
        os.chdir(productsdir)
        now = datetime.datetime.now()
        pfiles_dir = pathlib.Path(productsdir).resolve().joinpath("pfiles" + now.strftime('%Y%m%d%H%M%S'))
        pfiles_dir.mkdir(parents=True, exist_ok=True)
        self.pfiles_path = pfiles_dir.absolute()
        headas_syspfiles = os.environ.get("HEADAS", "") + "/syspfiles"
        pfiles_env = str(pfiles_dir.absolute()) + ";" + headas_syspfiles
        os.environ["PFILES"] = pfiles_env

    def __del__(self):
        shutil.rmtree(self.pfiles_path)

    def rsl_copy(self, eventdir, obsid, filter):
        eventdir = pathlib.Path(eventdir).resolve()
        eventfile = '{0}rsl_p0px{1}_cl.evt.gz'.format(obsid, filter)
        pixgtifile = '{0}rsl_px{1}_exp.gti.gz'.format(obsid, filter)
        ehkfile = '{0}.ehk.gz'.format(obsid)
        if pathlib.Path(eventfile).exists(): pathlib.Path(eventfile).unlink()
        if pathlib.Path(pixgtifile).exists(): pathlib.Path(pixgtifile).unlink()
        if pathlib.Path(ehkfile).exists(): pathlib.Path(ehkfile).unlink()

        os.symlink('{0}/resolve/event_cl/{1}'.format(eventdir, eventfile), eventfile)
        os.symlink('{0}/resolve/event_uf/{1}'.format(eventdir, pixgtifile), pixgtifile)
        os.symlink('{0}/auxil/{1}'.format(eventdir, ehkfile), ehkfile)

        with open("region_RSL_det.reg", "w") as f:
            f.write("physical\n")
            f.write("+box(4,1,5,1)\n")
            f.write("+box(3.5,2,6,1)\n")
            f.write("+box(3.5,3,6,1)\n")
            f.write("+box(3.5,4,6,1)\n")
            f.write("+box(3.5,5,6,1)\n")
            f.write("+box(3.5,6,6,1)\n")

        with open("region_RSL_det_27.reg", "w") as f:
            f.write("physical\n")
            f.write("+box(4,1,5,1)\n")
            f.write("+box(3.5,2,6,1)\n")
            f.write("+box(3.5,3,6,1)\n")
            f.write("+box(3,4,5,1)\n")
            f.write("+box(3.5,5,6,1)\n")
            f.write("+box(3.5,6,6,1)\n")

    def rsl_rise_time_screenin(self, eventfile, obsid, filter):
        infile = eventfile + "[EVENTS][(PI>=600) && (((((RISE_TIME+0.00075*DERIV_MAX)>46)&&((RISE_TIME+0.00075*DERIV_MAX)<58))&&ITYPE<4)||(ITYPE==4))&&STATUS[4]==b0]"
        outfile = "{0}rsl_p0px{1}_cl2.evt".format(obsid, filter)
        inputs = [
            'infile='+infile,
            'outfile='+outfile,
            'copyall=yes',
            'clobber=yes',
            'history=yes'
        ]
        process = subprocess.Popen(['ftcopy', *inputs], text=True)
        process.wait()
        return outfile

    def rsl_rise_time_screenin_Ls_excluded(self, eventfile, obsid, filter):
        infile = eventfile + "[EVENTS][(PI>=600) && ((((RISE_TIME+0.00075*DERIV_MAX)>46)&&((RISE_TIME+0.00075*DERIV_MAX)<58))&&ITYPE<4)]"
        outfile = "{0}rsl_p0px{1}_cl2_Ls_excluded.evt".format(obsid, filter)
        inputs = [
            'infile='+infile,
            'outfile='+outfile,
            'copyall=yes',
            'clobber=yes',
            'history=yes'
        ]
        process = subprocess.Popen(['ftcopy', *inputs], text=True)
        process.wait()
        return outfile

    def rsl_gain_gti(self, eventfile, eventdir, obsid, filter):
        eventdir = pathlib.Path(eventdir).resolve()
        eventfile_fe55 = '{0}rsl_p0px5000_uf.evt.gz'.format(obsid)
        if pathlib.Path(eventfile_fe55).exists(): pathlib.Path(eventfile_fe55).unlink()
        os.symlink('{0}/resolve/event_uf/{1}'.format(eventdir, eventfile_fe55), eventfile_fe55)
        outfile = '{0}rsl_p0px{1}_cl_gain.evt'.format(obsid, filter)
        mgtime_inputs = [
            'ingtis={0}[2],{0}[6]'.format(eventfile_fe55),
            'outgti=Fe55track.gti',
            'merge=AND'
        ]

        rslgain_inputs = [
            'infile='+eventfile_fe55,
            'outfile=Fe55.ghf',
            'linetocorrect=MnKa',
            'calmethod=Fe55',
            'clobber=yes',
            'debug=yes',
            'logfile=rslgain.log',
            'spangti=no',
            'ckrisetime=yes',
            'calcerr=yes',
            'writeerrfunc=yes',
            'extraspread=40',
            'numevent=1000',
            'minevent=200',
            'gtifile=Fe55track.gti',
            'maxdshift=7.0',
            'minwidth=0.1'
        ]

        rslpha2pi_inputs = [
            'infile={0}'.format(eventfile),
            'outfile='+outfile,
            'driftfile=Fe55.ghf',
            'logfile=rslpha2pi.log',
            'debug=yes',
            'writetemp=yes',
            'clobber=yes'
        ]

        process = subprocess.Popen(['mgtime', *mgtime_inputs], text=True)
        process.wait()
        process = subprocess.Popen(['rslgain', *rslgain_inputs], text=True)
        process.wait()
        process = subprocess.Popen(['rslpha2pi', *rslpha2pi_inputs], text=True)
        process.wait()
        return outfile

    def calspec(self, eventdir, specfile, obsid, pixel='0:11,13:26,28:35', grade='0:0'):
        eventdir = pathlib.Path(eventdir).resolve()
        ftcopy_inputs = [
            os.environ['CALDB'] + '/data/xrism/resolve/bcf/response/xa_rsl_rmfparam_20190101v005.fits.gz[GAUSFWHM1]',
            'xa_rsl_rmfparam_fordiagrmf.fits',
            'clobber=yes'
        ]
        ftcalc_inputs = [
            'xa_rsl_rmfparam_fordiagrmf.fits[GAUSFWHM1]',
            'xa_rsl_rmfparam_fordiagrmf.fits',
            'PIXEL0',
            '0.000000001',
            'rows=-',
            'clobber=yes'
        ]
        rslrmf_inputs = [
            'NONE',
            'newdiag',
            'whichrmf=S',
            'rmfparamfile=xa_rsl_rmfparam_fordiagrmf.fits'
            'clobber=yes'
        ]
        process = subprocess.Popen(['ftcopy', *ftcopy_inputs], text=True)
        process.wait()
        process = subprocess.Popen(['ftcalc', *ftcalc_inputs], text=True)
        process.wait()
        process = subprocess.Popen(['rslrmf', *rslrmf_inputs], text=True)
        process.wait()

        eventfile_fe55 = '{0}rsl_p0px5000_cl.evt.gz'.format(obsid)
        if pathlib.Path(eventfile_fe55).exists(): pathlib.Path(eventfile_fe55).unlink()
        os.symlink('{0}/resolve/event_cl/{1}'.format(eventdir, eventfile_fe55), eventfile_fe55)

        commands = [
            'xsel',
            'no',
            'read event {0}'.format(eventfile_fe55),
            './',
            'yes',
            'filter pha_cutoff 0 59999',
            'filter column "PIXEL={0}"'.format(pixel),
            'filter GRADE "{0}"'.format(grade),
            'extract spectrum',
            'save spec {0} clobber=yes'.format(specfile),
            'exit',
            'no'
        ]
        process = subprocess.Popen(['xselect'], stdin=subprocess.PIPE, text=True)
        results = process.communicate('\n'.join(commands))
        process.wait()

    def rsl_imgextract(self, eventfile, obsid, filter, mode='DET', bmin=4000, bmax=20000):
        commands = [
            'xsel',
            'no',
            'read event {0}'.format(eventfile),
            './',
            'yes',
            'set image {0}'.format(mode),
            'filter region exclude_calsources.reg',
            'filter pha_cutoff {0} {1}'.format(bmin, bmax),
            'extract image',
            'save image {0}rsl_p0px{1}_detimg.fits clobber=yes'.format(obsid, filter),
            'exit',
            'no'
        ]
        process = subprocess.Popen(['xselect'], stdin=subprocess.PIPE, text=True)
        results = process.communicate('\n'.join(commands))
        process.wait()

    def rsl_specextract(self, eventfile, specfile, pixel='0:11,13:26,28:35', grade='0:0'):
        commands = [
            'xsel',
            'no',
            'read event {0}'.format(eventfile),
            './',
            'yes',
            'filter pha_cutoff 0 59999',
            'filter column "PIXEL={0}"'.format(pixel),
            'filter GRADE "{0}"'.format(grade),
            'extract spectrum',
            'save spec {0} clobber=yes'.format(specfile),
            'exit',
            'no'
        ]
        process = subprocess.Popen(['xselect'], stdin=subprocess.PIPE, text=True)
        results = process.communicate('\n'.join(commands))
        process.wait()

    def rsl_lcextract(self, eventfile, obsid, bmin=4000, bmax=20000, binsize='128'):
        commands = [
            'xsel',
            'no',
            'read event {0}'.format(eventfile),
            './',
            'yes',
            'set image det',
            'filter pha_cutoff {0} {1}'.format(bmin, bmax),
            'set binsize {0}'.format(binsize),
            'extr curve exposure=0.8',
            'save curve {0}rsl_allpix_b{1}_lc.fits clobber=yes'.format(obsid, binsize),
            'exit',
            'no'
        ]
        process = subprocess.Popen(['xselect'], stdin=subprocess.PIPE, text=True)
        results = process.communicate('\n'.join(commands))
        process.wait()

    def rsl_mkrmf(self, infile, respfile, whichrmf, regmode='DET', resolist='0', regionfile='NONE', pixlist='0-11,13-26,28-35', eminin='0.0', dein='0.5', nchanin='60000', useingrd='no', eminout='0.0', deout='0.5', nchanout='60000', clobber='yes', rmfparamfile='CALDB'):
        outroot = "{0}".format(respfile.strip('_comb.rmf'))
        inputs = [
            'infile='+str(infile),
            'outfileroot='+str(outroot),
            'regmode='+str(regmode),
            'whichrmf='+str(whichrmf.strip('_comb')),
            'resolist='+str(resolist),
            'regionfile='+str(regionfile),
            'pixlist='+str(pixlist),
            'eminin='+str(eminin),
            'dein='+str(dein),
            'nchanin='+str(nchanin),
            'useingrd='+str(useingrd),
            'eminout='+str(eminout),
            'deout='+str(deout),
            'nchanout='+str(nchanout),
            'rmfparamfile='+str(rmfparamfile),
            'clobber='+str(clobber)
        ]
        if 'comb' in whichrmf: inputs += ['splitrmf=yes', 'elcbinfac=16', 'splitcomb=yes']
        process = subprocess.Popen(['rslmkrmf', *inputs], text=True)
        process.wait()

    def rsl_xaexpmap(self, ehkfile, gtifile, pixgtifile, outfile, logfile, instrume='RESOLVE', badimgfile='NONE', outmaptype='EXPOSURE', delta='20.0', numphi='1', stopsys='SKY', instmap='CALDB', qefile='CALDB', contamifile='CALDB', vigfile='CALDB', obffile='CALDB', fwfile='CALDB', gvfile='CALDB', maskcalsrc='yes', fwtype='FILE', specmode='MONO', specfile='spec.fits', specform='FITS', evperchan='DEFAULT', abund='1', cols='0', covfac='1', clobber='yes', chatter='1'):
        inputs = [
            'ehkfile='+str(ehkfile),
            'gtifile='+str(gtifile),
            'instrume='+str(instrume),
            'badimgfile='+str(badimgfile),
            'pixgtifile='+str(pixgtifile),
            'outfile='+str(outfile),
            'outmaptype='+str(outmaptype),
            'delta='+str(delta),
            'numphi='+str(numphi),
            'stopsys='+str(stopsys),
            'instmap='+str(instmap),
            'qefile='+str(qefile),
            'contamifile='+str(contamifile),
            'vigfile='+str(vigfile),
            'obffile='+str(obffile),
            'fwfile='+str(fwfile),
            'gvfile='+str(gvfile),
            'maskcalsrc='+str(maskcalsrc),
            'fwtype='+str(fwtype),
            'specmode='+str(specmode),
            'specfile='+str(specfile),
            'specform='+str(specform),
            'evperchan='+str(evperchan),
            'abund='+str(abund),
            'cols='+str(cols),
            'covfac='+str(covfac),
            'clobber='+str(clobber),
            'chatter='+str(chatter),
            'logfile='+str(logfile)
        ]
        process = subprocess.Popen(['xaexpmap', *inputs], text=True)
        process.wait()

    def rsl_xaarfgen(self, xrtevtfile, emapfile, respfile, ancrfile, regionfile, source_ra, source_dec, telescop='XRISM', instrume='RESOLVE', regmode='DET', sourcetype='POINT', erange='0.3 18.0 0 0', numphoton='300000', minphoton='100', teldeffile='CALDB', qefile='CALDB', contamifile='CALDB', obffile='CALDB', fwfile='CALDB', gatevalvefile='CALDB', onaxisffile='CALDB', onaxiscfile='CALDB', mirrorfile='CALDB', obstructfile='CALDB', frontreffile='CALDB', backreffile='CALDB', pcolreffile='CALDB', scatterfile='CALDB', mode='h', clobber='yes', seed='7', imgfile='NONE'):
        inputs = [
            'xrtevtfile='+str(xrtevtfile),
            'source_ra='+str(source_ra),
            'source_dec='+str(source_dec),
            'telescop='+str(telescop),
            'instrume='+str(instrume),
            'emapfile='+str(emapfile),
            'regmode='+str(regmode),
            'regionfile='+str(regionfile),
            'sourcetype='+str(sourcetype),
            'rmffile='+str(respfile),
            'erange='+str(erange),
            'outfile='+str(ancrfile),
            'numphoton='+str(numphoton),
            'minphoton='+str(minphoton),
            'teldeffile='+str(teldeffile),
            'qefile='+str(qefile),
            'contamifile='+str(contamifile),
            'obffile='+str(obffile),
            'fwfile='+str(fwfile),
            'gatevalvefile='+str(gatevalvefile),
            'onaxisffile='+str(onaxisffile),
            'onaxiscfile='+str(onaxiscfile),
            'mirrorfile='+str(mirrorfile),
            'obstructfile='+str(obstructfile),
            'frontreffile='+str(frontreffile),
            'backreffile='+str(backreffile),
            'pcolreffile='+str(pcolreffile),
            'scatterfile='+str(scatterfile),
            'mode='+str(mode),
            'clobber='+str(clobber),
            'seed='+str(seed),
            'imgfile='+str(imgfile)
        ]
        process = subprocess.Popen(['xaarfgen', *inputs], text=True)
        process.wait()

    def rsl_coordpnt(self, RA_NOM, DEC_NOM, PA_NOM, X0=3.5, Y0=3.5):
        inputs =[
            'input={0},{1}'.format(X0, Y0),
            'outfile=NONE',
            'telescop=XRISM',
            'instrume=RESOLVE',
            'teldeffile=CALDB',
            'startsys=DET',
            'stopsys=RADEC',
            'ra={0}'.format(RA_NOM),
            'dec={0}'.format(DEC_NOM),
            'roll={0}'.format(PA_NOM),
            'ranom={0}'.format(RA_NOM),
            'decnom={0}'.format(DEC_NOM),
            'clobber=yes'
        ]
        process = subprocess.Popen(['coordpnt', *inputs], stdout=subprocess.PIPE, text=True)
        process.wait()
        results = process.communicate()
        ra, dec = re.findall(r'([-\d\.]+)',results[0])
        return ra, dec

    def get_radec_nom(self, eventfile):
        process = subprocess.Popen(['fkeyprint', "{0}+0".format(eventfile),'RA_NOM'], stdout=subprocess.PIPE, text=True)
        process.wait()
        results = process.communicate()
        RA_NOM = re.search(r'RA_NOM\s*=\s*([-\d\.]+)',results[0]).group(1)
        process = subprocess.Popen(['fkeyprint', "{0}+0".format(eventfile), 'DEC_NOM'], stdout=subprocess.PIPE, text=True)
        process.wait()
        results = process.communicate()
        DEC_NOM = re.search(r'DEC_NOM\s*=\s*([-\d\.]+)',results[0]).group(1)
        process = subprocess.Popen(['fkeyprint', "{0}+0".format(eventfile), 'PA_NOM'], stdout=subprocess.PIPE, text=True)
        process.wait()
        results = process.communicate()
        PA_NOM = re.search(r'PA_NOM\s*=\s*([-\d\.]+)',results[0]).group(1)
        return RA_NOM, DEC_NOM, PA_NOM

    def ftgrouppha(self, infile, outfile, backfile, respfile, grouptype, groupscale):
        inputs = [
            'infile='+infile,
            'outfile='+outfile,
            'backfile='+backfile,
            'respfile='+respfile,
            'grouptype='+grouptype,
            'groupscale='+groupscale
        ]
        process = subprocess.Popen(['ftgrouppha', *inputs], text=True)
        process.wait()

    def bgd_rmf_arf(self, srcfile, backfile, respfile, ancrfile):
        process = subprocess.Popen(['fparkey', backfile, srcfile, 'BACKFILE'], text=True)
        process.wait()
        process = subprocess.Popen(['fparkey', respfile, srcfile, 'RESPFILE'], text=True)
        process.wait()
        process = subprocess.Popen(['fparkey', ancrfile, srcfile, 'ANCRFILE'], text=True)
        process.wait()

    def rsl_products(self):
        obsid = self.obsid
        filter = self.filter
        whichrmf = self.whichrmf
        eventdir = self.eventdir
        eventfile = '{0}rsl_p0px{1}_cl.evt.gz'.format(obsid, filter)
        regionfile = "region_RSL_det_27.reg"
        specfile = "{0}rsl_src.pha".format(obsid)
        outfile = "{0}rsl_srgr1.pha".format(obsid)
        backfile = "NONE"
        respfile = "{0}rsl_{1}.rmf".format(obsid, whichrmf)
        ancrfile = "{0}rsl_{1}.arf".format(obsid, whichrmf)
        grouptype = "min"
        groupscale = "1"
        self.rsl_copy(eventdir, obsid, filter)
        eventfile = self.rsl_rise_time_screenin(eventfile, obsid, filter)
        self.rsl_lcextract(eventfile, obsid)
        self.rsl_imgextract(eventfile, obsid, filter, mode='DET', bmin=4000, bmax=20000)
        self.rsl_specextract(eventfile, specfile)
        self.rsl_mkrmf(eventfile, respfile, whichrmf, rmfparamfile=rmfparamfile)

        ehkfile = '{0}.ehk.gz'.format(obsid)
        pixgtifile = '{0}rsl_px{1}_exp.gti.gz'.format(obsid, filter)
        emapfile = '{0}rsl_p0px{1}.expo'.format(obsid, filter)
        logfile = 'make_expo_{0}rsl_p0px{1}.log'.format(obsid, filter)
        self.rsl_xaexpmap(ehkfile=ehkfile, gtifile=eventfile, pixgtifile=pixgtifile, outfile=emapfile, logfile=logfile)

        RA_NOM, DEC_NOM, PA_NOM = self.get_radec_nom(eventfile)
        source_ra, source_dec = self.rsl_coordpnt(RA_NOM, DEC_NOM, PA_NOM, X0=3.5, Y0=3.5)
        xrtevtfile = 'raytrace_{0}rsl_p0px{1}_ptsrc.fits'.format(obsid, filter)
        self.rsl_xaarfgen(xrtevtfile=xrtevtfile, emapfile=emapfile, respfile=respfile, ancrfile=ancrfile, regionfile=regionfile, source_ra=source_ra, source_dec=source_dec)

        self.ftgrouppha(specfile, outfile, backfile, respfile, grouptype, groupscale)
        self.bgd_rmf_arf(outfile, backfile, respfile, ancrfile)

        whichrmf = "X_comb"
        respfile = "{0}rsl_{1}.rmf".format(obsid, whichrmf)
        ancrfile = "{0}rsl_{1}.arf".format(obsid, whichrmf)
        if not pathlib.Path(respfile).exists():
            self.rsl_mkrmf(eventfile, respfile, whichrmf, rmfparamfile=rmfparamfile)
            self.rsl_xaarfgen(xrtevtfile=xrtevtfile, emapfile=emapfile, respfile=respfile, ancrfile=ancrfile, regionfile=regionfile, source_ra=source_ra, source_dec=source_dec)

    def rsl_products_Ls(self):
        obsid = self.obsid
        filter = self.filter
        whichrmf = self.whichrmf
        eventdir = self.eventdir
        eventfile = '{0}rsl_p0px{1}_cl.evt.gz'.format(obsid, filter)
        regionfile = "region_RSL_det_27.reg"
        specfile = "{0}rsl_Ls_excluded_src.pha".format(obsid)
        outfile = "{0}rsl_Ls_excluded_srgr1.pha".format(obsid)
        backfile = "NONE"
        respfile = "{0}rsl_Ls_excluded_{1}.rmf".format(obsid, whichrmf)
        ancrfile = "{0}rsl_Ls_excluded_{1}.arf".format(obsid, whichrmf)
        grouptype = "min"
        groupscale = "1"
        self.rsl_copy(eventdir, obsid, filter)
        eventfile = self.rsl_rise_time_screenin_Ls_excluded(eventfile, obsid, filter)
        self.rsl_lcextract(eventfile, obsid)
        self.rsl_imgextract(eventfile, obsid, filter, mode='DET', bmin=4000, bmax=20000)
        self.rsl_specextract(eventfile, specfile)
        self.rsl_mkrmf(eventfile, respfile, whichrmf, rmfparamfile=rmfparamfile)

        ehkfile = '{0}.ehk.gz'.format(obsid)
        pixgtifile = '{0}rsl_px{1}_exp.gti.gz'.format(obsid, filter)
        emapfile = '{0}rsl_p0px{1}.expo'.format(obsid, filter)
        logfile = 'make_expo_{0}rsl_p0px{1}.log'.format(obsid, filter)
        self.rsl_xaexpmap(ehkfile=ehkfile, gtifile=eventfile, pixgtifile=pixgtifile, outfile=emapfile, logfile=logfile)

        RA_NOM, DEC_NOM, PA_NOM = self.get_radec_nom(eventfile)
        source_ra, source_dec = self.rsl_coordpnt(RA_NOM, DEC_NOM, PA_NOM, X0=3.5, Y0=3.5)
        xrtevtfile = 'raytrace_{0}rsl_p0px{1}_ptsrc.fits'.format(obsid, filter)
        self.rsl_xaarfgen(xrtevtfile=xrtevtfile, emapfile=emapfile, respfile=respfile, ancrfile=ancrfile, regionfile=regionfile, source_ra=source_ra, source_dec=source_dec)

        self.ftgrouppha(specfile, outfile, backfile, respfile, grouptype, groupscale)
        self.bgd_rmf_arf(outfile, backfile, respfile, ancrfile)

        whichrmf = "X_comb"
        respfile = "{0}rsl_Ls_excluded_{1}.rmf".format(obsid, whichrmf)
        ancrfile = "{0}rsl_Ls_excluded_{1}.arf".format(obsid, whichrmf)
        if not pathlib.Path(respfile).exists():
            self.rsl_mkrmf(eventfile, respfile, whichrmf, rmfparamfile=rmfparamfile)
            self.rsl_xaarfgen(xrtevtfile=xrtevtfile, emapfile=emapfile, respfile=respfile, ancrfile=ancrfile, regionfile=regionfile, source_ra=source_ra, source_dec=source_dec)


    def rsl_products_gain(self):
        obsid = self.obsid
        filter = self.filter
        whichrmf = self.whichrmf
        eventdir = self.eventdir
        regionfile = "region_RSL_det_27.reg"
        specfile = "{0}rsl_src.pha".format(obsid)
        outfile = "{0}rsl_srgr1.pha".format(obsid)
        backfile = "NONE"
        respfile = "{0}rsl_{1}.rmf".format(obsid, whichrmf)
        ancrfile = "{0}rsl_{1}.arf".format(obsid, whichrmf)
        grouptype = "min"
        groupscale = "1"
        self.rsl_copy(eventdir, obsid, filter)
        eventfile = '{0}rsl_p0px{1}_cl.evt.gz'.format(obsid, filter)
        eventfile = self.rsl_gain_gti(eventfile, eventdir, obsid, filter)
        eventfile = self.rsl_rise_time_screenin(eventfile, obsid, filter)
        self.rsl_lcextract(eventfile, obsid)
        self.rsl_imgextract(eventfile, obsid, filter, mode='DET', bmin=4000, bmax=20000)
        self.rsl_specextract(eventfile, specfile)
        self.rsl_mkrmf(eventfile, respfile, whichrmf, rmfparamfile=rmfparamfile)

        ehkfile = '{0}.ehk.gz'.format(obsid)
        pixgtifile = '{0}rsl_px{1}_exp.gti.gz'.format(obsid, filter)
        emapfile = '{0}rsl_p0px{1}.expo'.format(obsid, filter)
        logfile = 'make_expo_{0}rsl_p0px{1}.log'.format(obsid, filter)
        self.rsl_xaexpmap(ehkfile=ehkfile, gtifile=eventfile, pixgtifile=pixgtifile, outfile=emapfile, logfile=logfile)

        RA_NOM, DEC_NOM, PA_NOM = self.get_radec_nom(eventfile)
        source_ra, source_dec = self.rsl_coordpnt(RA_NOM, DEC_NOM, PA_NOM, X0=3.5, Y0=3.5)
        xrtevtfile = 'raytrace_{0}rsl_p0px{1}_ptsrc.fits'.format(obsid, filter)
        self.rsl_xaarfgen(xrtevtfile=xrtevtfile, emapfile=emapfile, respfile=respfile, ancrfile=ancrfile, regionfile=regionfile, source_ra=source_ra, source_dec=source_dec)

        self.ftgrouppha(specfile, outfile, backfile, respfile, grouptype, groupscale)
        self.bgd_rmf_arf(outfile, backfile, respfile, ancrfile)

        whichrmf = "X_comb"
        respfile = "{0}rsl_{1}.rmf".format(obsid, whichrmf)
        ancrfile = "{0}rsl_{1}.arf".format(obsid, whichrmf)
        if not pathlib.Path(respfile).exists():
            self.rsl_mkrmf(eventfile, respfile, whichrmf, rmfparamfile=rmfparamfile)
            self.rsl_xaarfgen(xrtevtfile=xrtevtfile, emapfile=emapfile, respfile=respfile, ancrfile=ancrfile, regionfile=regionfile, source_ra=source_ra, source_dec=source_dec)

    def rsl_products_gain_Ls(self):
        obsid = self.obsid
        filter = self.filter
        whichrmf = self.whichrmf
        eventdir = self.eventdir
        regionfile = "region_RSL_det_27.reg"
        specfile = "{0}rsl_Ls_excluded_src.pha".format(obsid)
        outfile = "{0}rsl_Ls_excluded_srgr1.pha".format(obsid)
        backfile = "NONE"
        respfile = "{0}rsl_Ls_excluded_{1}.rmf".format(obsid, whichrmf)
        ancrfile = "{0}rsl_Ls_excluded_{1}.arf".format(obsid, whichrmf)
        grouptype = "min"
        groupscale = "1"
        self.rsl_copy(eventdir, obsid, filter)
        eventfile = '{0}rsl_p0px{1}_cl.evt.gz'.format(obsid, filter)
        eventfile = self.rsl_gain_gti(eventfile, eventdir, obsid, filter)
        eventfile = self.rsl_rise_time_screenin_Ls_excluded(eventfile, obsid, filter)
        self.rsl_lcextract(eventfile, obsid)
        self.rsl_imgextract(eventfile, obsid, filter, mode='DET', bmin=4000, bmax=20000)
        self.rsl_specextract(eventfile, specfile)
        self.rsl_mkrmf(eventfile, respfile, whichrmf, rmfparamfile=rmfparamfile)

        ehkfile = '{0}.ehk.gz'.format(obsid)
        pixgtifile = '{0}rsl_px{1}_exp.gti.gz'.format(obsid, filter)
        emapfile = '{0}rsl_p0px{1}.expo'.format(obsid, filter)
        logfile = 'make_expo_{0}rsl_p0px{1}.log'.format(obsid, filter)
        self.rsl_xaexpmap(ehkfile=ehkfile, gtifile=eventfile, pixgtifile=pixgtifile, outfile=emapfile, logfile=logfile)

        RA_NOM, DEC_NOM, PA_NOM = self.get_radec_nom(eventfile)
        source_ra, source_dec = self.rsl_coordpnt(RA_NOM, DEC_NOM, PA_NOM, X0=3.5, Y0=3.5)
        xrtevtfile = 'raytrace_{0}rsl_p0px{1}_ptsrc.fits'.format(obsid, filter)
        self.rsl_xaarfgen(xrtevtfile=xrtevtfile, emapfile=emapfile, respfile=respfile, ancrfile=ancrfile, regionfile=regionfile, source_ra=source_ra, source_dec=source_dec)

        self.ftgrouppha(specfile, outfile, backfile, respfile, grouptype, groupscale)
        self.bgd_rmf_arf(outfile, backfile, respfile, ancrfile)

        whichrmf = "X_comb"
        respfile = "{0}rsl_Ls_excluded_{1}.rmf".format(obsid, whichrmf)
        ancrfile = "{0}rsl_Ls_excluded_{1}.arf".format(obsid, whichrmf)
        if not pathlib.Path(respfile).exists():
            self.rsl_mkrmf(eventfile, respfile, whichrmf, rmfparamfile=rmfparamfile)
            self.rsl_xaarfgen(xrtevtfile=xrtevtfile, emapfile=emapfile, respfile=respfile, ancrfile=ancrfile, regionfile=regionfile, source_ra=source_ra, source_dec=source_dec)


    def rsl_products_pixel(self, eventfile, pix):
        obsid = self.obsid
        filter = self.filter
        whichrmf = self.whichrmf
        pixel_map = self.pixel_map
        specfile = "{0}rsl_src_pix{1:02d}.pha".format(obsid, pix)
        respfile = "{0}rsl_{1}_pix{2:02d}.rmf".format(obsid, whichrmf, pix)
        ancrfile = "{0}rsl_{1}_pix{2:02d}.arf".format(obsid, whichrmf, pix)
        regionfile = 'region_RSL_det_pix{0:02d}.reg'.format(pix)
        with open(regionfile, "w") as f:
            f.write("physical\n")
            f.write("+box({0},{1},1,1)\n".format(*pixel_map[pix]))
        self.rsl_specextract(eventfile, specfile)
        self.rsl_mkrmf(eventfile, respfile, whichrmf, pixlist=pix)

        emapfile = '{0}rsl_p0px{1}.expo'.format(obsid, filter)
        RA_NOM, DEC_NOM, PA_NOM = self.get_radec_nom(eventfile)
        source_ra, source_dec = self.rsl_coordpnt(RA_NOM, DEC_NOM, PA_NOM, X0=3.5, Y0=3.5)
        xrtevtfile = 'raytrace_{0}rsl_p0px{1}_ptsrc.fits'.format(obsid, filter)
        self.rsl_xaarfgen(xrtevtfile=xrtevtfile, emapfile=emapfile, respfile=respfile, ancrfile=ancrfile, regionfile=regionfile, source_ra=source_ra, source_dec=source_dec)

    def rsl_products_pixel_by_pixel(self, eventfile):
        for pix in range(36):
            self.rsl_products_pixel(self, eventfile, pix)


if __name__ == "__main__":
    args = get_argument()
    obsid = args.obsid
    filter = args.filter
    whichrmf = args.whichrmf
    eventdir = args.eventdir
    productsdir = args.productsdir
    rsl = ResolveTools(obsid, filter, whichrmf, eventdir, productsdir)
    rsl.rsl_products()
