#! /usr/bin/env python3

from argparse import ArgumentParser
import datetime
import os
import pathlib
import re
import shutil
import subprocess
import sys

HEADAS = '/home/ogawa/work/tools/heasoft/heasoft-6.34/x86_64-pc-linux-gnu-libc2.31'
CALDB = '/home/ogawa/work/tools/caldb'

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
    argparser.add_argument('-oi', '--obsid', default=None, help='OBSID')
    argparser.add_argument('-fi', '--filter', default='1000', help='Filter ID')
    argparser.add_argument('-wr', '--whichrmf', default='S', help='RMF size')
    argparser.add_argument('-ed', '--eventsdir', default='..', help='Eventfile directory path')
    argparser.add_argument('-pd', '--productsdir', default='.', help='Products directory path')
    argparser.add_argument('--lsexclude', action='store_true', help='Flag for excluding Ls')
    argparser.add_argument('--rslnxbgen', action='store_true', help='Flag for rslnxbgen')
    return argparser.parse_args()

class ResolveTools:

    def __init__(self, obsid, filter, whichrmf, eventsdir='..', productsdir='.'):
        self.obsid = obsid
        self.filter = filter
        self.whichrmf = whichrmf
        self.eventsdir =  pathlib.Path(eventsdir).resolve()
        self.productsdir =  pathlib.Path(productsdir).resolve()
        self.eventfile = '{0}rsl_p0px{1}_cl.evt.gz'.format(obsid, filter)
        self.eventfile_noLs = None
        self.eventfile_for_rmf = None
        self.ehkfile = '{0}.ehk.gz'.format(obsid)
        self.optgrppifile = None

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
        self.logfile = pathlib.Path(productsdir).resolve().joinpath("run_" + now.strftime('%Y%m%d%H%M%S') + ".log")

    def __del__(self):
        shutil.rmtree(self.pfiles_path)

    def rsl_copy(self, eventsdir, obsid, filter):
        eventsdir = pathlib.Path(eventsdir).resolve()
        eventfile = '{0}rsl_p0px{1}_cl.evt.gz'.format(obsid, filter)
        pixgtifile = '{0}rsl_px{1}_exp.gti.gz'.format(obsid, filter)
        ehkfile = '{0}.ehk.gz'.format(obsid)

        orgevtfile = eventsdir.joinpath('resolve/event_cl/{0}'.format(eventfile))
        orgpixgtifile = eventsdir.joinpath('resolve/event_uf/{0}'.format(pixgtifile))
        orgehkfile = eventsdir.joinpath('auxil/{0}'.format(ehkfile))

        if not orgevtfile.exists():
            print(str(orgevtfile) + ' does not exist.')
        elif not orgpixgtifile.exists():
            print(str(orgpixgtifile) + ' does not exist.')
        elif not orgehkfile.exists():
            print(str(orgehkfile) + ' does not exist.')
        else:
            if pathlib.Path(eventfile).exists() or pathlib.Path(eventfile).is_symlink(): pathlib.Path(eventfile).unlink()
            if pathlib.Path(pixgtifile).exists() or pathlib.Path(pixgtifile).is_symlink(): pathlib.Path(pixgtifile).unlink()
            if pathlib.Path(ehkfile).exists() or pathlib.Path(ehkfile).is_symlink(): pathlib.Path(ehkfile).unlink()

            os.symlink(orgevtfile, eventfile)
            os.symlink(orgpixgtifile, pixgtifile)
            os.symlink(orgehkfile, ehkfile)

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

    def rsl_rise_time_screening(self, eventfile, obsid, filter):
        if not os.path.isfile(eventfile):
            print(str(eventfile) + ' does not exist.')
            return 1
        else:
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
            with open(self.logfile, "a") as o:
                print(*process.args, sep=" ", file=o)
            process.wait()
            self.eventfile = outfile
            return outfile

    def rsl_rise_time_screening_Ls_excluded(self, eventfile, obsid, filter):
        if not os.path.isfile(eventfile):
            print(str(eventfile) + ' does not exist.')
            return 1
        else:
            infile = eventfile + "[EVENTS][(PI>=600) && ((((RISE_TIME+0.00075*DERIV_MAX)>46)&&((RISE_TIME+0.00075*DERIV_MAX)<58))&&ITYPE<4)&&STATUS[4]==b0]"
            outfile = "{0}rsl_p0px{1}_cl2_Ls_excluded.evt".format(obsid, filter)
            inputs = [
                'infile='+infile,
                'outfile='+outfile,
                'copyall=yes',
                'clobber=yes',
                'history=yes'
            ]
            process = subprocess.Popen(['ftcopy', *inputs], text=True)
            with open(self.logfile, "a") as o:
                print(*process.args, sep=" ", file=o)
            process.wait()
            self.eventfile = outfile
            return outfile

    def rsl_remove_Ls(self, eventfile, obsid, filter):
        if not os.path.isfile(eventfile):
            print(str(eventfile) + ' does not exist.')
            return 1
        else:
            infile = eventfile + "[EVENTS][ITYPE<4]"
            outfile = "{0}rsl_p0px{1}_cl2_woLs.evt".format(obsid, filter)
            inputs = [
                'infile='+infile,
                'outfile='+outfile,
                'copyall=yes',
                'clobber=yes',
                'history=yes'
            ]
            process = subprocess.Popen(['ftcopy', *inputs], text=True)
            with open(self.logfile, "a") as o:
                print(*process.args, sep=" ", file=o)
            process.wait()
            self.eventfile_noLs = outfile
            return outfile

    def rsl_evtfile_for_rmf(self, eventfile, obsid, filter):
        if not os.path.isfile(eventfile):
            print(str(eventfile) + ' does not exist.')
            return 1
        else:
            infile = eventfile + "[EVENTS][(PI>=6000)&&(PI<=20000)]"
            outfile = "{0}rsl_p0px{1}_cl2_woLs_rmf.evt".format(obsid, filter)
            inputs = [
                'infile='+infile,
                'outfile='+outfile,
                'copyall=yes',
                'clobber=yes',
                'history=yes'
            ]
            process = subprocess.Popen(['ftcopy', *inputs], text=True)
            with open(self.logfile, "a") as o:
                print(*process.args, sep=" ", file=o)
            process.wait()
            self.eventfile_for_rmf = outfile
            return outfile

    def rsl_gain_gti(self, eventfile, eventsdir, obsid, filter):
        eventsdir = pathlib.Path(eventsdir).resolve()
        eventfile_fe55 = '{0}rsl_p0px5000_uf.evt.gz'.format(obsid)
        if pathlib.Path(eventfile_fe55).exists(): pathlib.Path(eventfile_fe55).unlink()
        os.symlink('{0}/resolve/event_uf/{1}'.format(eventsdir, eventfile_fe55), eventfile_fe55)
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
        with open(self.logfile, "a") as o:
            print(*process.args, sep=" ", file=o)
        process.wait()
        process = subprocess.Popen(['rslgain', *rslgain_inputs], text=True)
        with open(self.logfile, "a") as o:
            print(*process.args, sep=" ", file=o)
        process.wait()
        process = subprocess.Popen(['rslpha2pi', *rslpha2pi_inputs], text=True)
        with open(self.logfile, "a") as o:
            print(*process.args, sep=" ", file=o)
        process.wait()

        self.eventfile = outfile
        return outfile

    def calspec(self, eventsdir, specfile, obsid, pixel='0:11,13:26,28:35', grade='0:0'):
        eventsdir = pathlib.Path(eventsdir).resolve()
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
        os.symlink('{0}/resolve/event_cl/{1}'.format(eventsdir, eventfile_fe55), eventfile_fe55)

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

    def rsl_imgextract(self, eventfile, obsid, filter, mode='DET', bmin=4000, bmax=19999):
        if not os.path.isfile(eventfile):
            print(str(eventfile) + ' does not exist.')
            return 1
        else:
            commands = [
                'xsel',
                'no',
                'read event {0}'.format(eventfile),
                './',
                'yes',
                'set image {0}'.format(mode),
                'filter pha_cutoff {0} {1}'.format(bmin, bmax),
                'extract image',
                'save image {0}rsl_p0px{1}_detimg.fits clobber=yes'.format(obsid, filter),
                'exit',
                'no'
            ]
            process = subprocess.Popen(['xselect'], stdin=subprocess.PIPE, text=True)
            results = process.communicate('\n'.join(commands))
            with open(self.logfile, "a") as o:
                print("xselect <<EOF\n{}\nEOF".format('\n'.join(commands)), file=o)
            process.wait()

    def rsl_specextract(self, eventfile, specfile, pixel='0:11,13:26,28:35', grade='0:0'):
        if not os.path.isfile(eventfile):
            print(str(eventfile) + ' does not exist.')
            return 1
        else:
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
            with open(self.logfile, "a") as o:
                print("xselect <<EOF\n{}\nEOF".format('\n'.join(commands)), file=o)
            process.wait()

    def rsl_lcextract(self, eventfile, obsid, bmin=4000, bmax=19999, binsize='128'):
        if not os.path.isfile(eventfile):
            print(str(eventfile) + ' does not exist.')
            return 1
        else:
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
            with open(self.logfile, "a") as o:
                print("xselect <<EOF\n{}\nEOF".format('\n'.join(commands)), file=o)
            process.wait()

    def rsl_mkrmf(self, infile, respfile, whichrmf, regmode='DET', resolist='0', regionfile='NONE', pixlist='0-11,13-26,28-35', eminin='0.0', dein='0.5', nchanin='60000', useingrd='no', eminout='0.0', deout='0.5', nchanout='60000', clobber='yes', rmfparamfile='CALDB'):
        if not os.path.isfile(infile):
            print(str(infile) + ' does not exist.')
            return 1
        else:
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
            process = subprocess.Popen(['punlearn', 'rslmkrmf'], text=True)
            with open(self.logfile, "a") as o:
                print(*process.args, sep=" ", file=o)
            process.wait()
            process = subprocess.Popen(['rslmkrmf', *inputs], text=True)
            with open(self.logfile, "a") as o:
                print(*process.args, sep=" ", file=o)
            process.wait()

    def rsl_xaexpmap(self, ehkfile, gtifile, pixgtifile, outfile, logfile, instrume='RESOLVE', badimgfile='NONE', outmaptype='EXPOSURE', delta='20.0', numphi='1', stopsys='SKY', instmap='CALDB', qefile='CALDB', contamifile='CALDB', vigfile='CALDB', obffile='CALDB', fwfile='CALDB', gvfile='CALDB', maskcalsrc='yes', fwtype='FILE', specmode='MONO', specfile='spec.fits', specform='FITS', evperchan='DEFAULT', abund='1', cols='0', covfac='1', clobber='yes', chatter='1'):
        if not os.path.isfile(ehkfile):
            print(str(ehkfile) + ' does not exist.')
            return 1
        elif not os.path.isfile(gtifile):
            print(str(gtifile) + ' does not exist.')
            return 1
        elif not os.path.isfile(pixgtifile):
            print(str(pixgtifile) + ' does not exist.')
            return 1
        else:
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
            process = subprocess.Popen(['punlearn', 'xaexpmap'], text=True)
            with open(self.logfile, "a") as o:
                print(*process.args, sep=" ", file=o)
            process.wait()
            process = subprocess.Popen(['xaexpmap', *inputs], text=True)
            with open(self.logfile, "a") as o:
                print(*process.args, sep=" ", file=o)
            process.wait()

    def rsl_xaarfgen(self, xrtevtfile, emapfile, respfile, ancrfile, regionfile, source_ra, source_dec, telescop='XRISM', instrume='RESOLVE', regmode='DET', sourcetype='POINT', erange='0.3 18.0 0 0', numphoton='600000', minphoton='100', teldeffile='CALDB', qefile='CALDB', contamifile='CALDB', obffile='CALDB', fwfile='CALDB', gatevalvefile='CALDB', onaxisffile='CALDB', onaxiscfile='CALDB', mirrorfile='CALDB', obstructfile='CALDB', frontreffile='CALDB', backreffile='CALDB', pcolreffile='CALDB', scatterfile='CALDB', mode='h', clobber='yes', seed='7', imgfile='NONE'):
        if not os.path.isfile(emapfile):
            print(str(emapfile) + ' does not exist.')
            return 1
        elif not os.path.isfile(respfile):
            print(str(respfile) + ' does not exist.')
            return 1
        elif not os.path.isfile(regionfile):
            print(str(regionfile) + ' does not exist.')
            return 1
        else:
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
            process = subprocess.Popen(['punlearn', 'xaarfgen'], text=True)
            with open(self.logfile, "a") as o:
                print(*process.args, sep=" ", file=o)
            process.wait()
            process = subprocess.Popen(['xaarfgen', *inputs], text=True)
            with open(self.logfile, "a") as o:
                print(*process.args, sep=" ", file=o)
            process.wait()

    def rsl_nxbgen(self, cl_evt, ehkfile, nxb_ehk, nxb_evt):
        if not os.path.isfile(nxb_ehk):
            print(str(nxb_ehk) + ' does not exist.')
            return 1
        elif not os.path.isfile(nxb_evt):
            print(str(nxb_evt) + ' does not exist.')
            return 1
        elif not os.path.isfile(cl_evt):
            print(str(cl_evt) + ' does not exist.')
            return 1
        else:
            inputs = [
                'infile='+str(nxb_ehk),
                'outfile='+str('ehkSelA.gti'),
                'expr='+str('T_SAA_SXS>0 && ELV<-5 && DYE_ELV>5'),
                'compact='+str('no'),
                'time='+str('TIME'),
                'clobber=yes'
            ]
            process = subprocess.Popen(['maketime', *inputs], text=True)
            with open(self.logfile, "a") as o:
                print(*process.args, sep=" ", file=o)
            process.wait()

            inputs = [
                'infile='+str(ehkfile),
                'outfile='+str('ehkSelB.gti'),
                'expr='+str('T_SAA_SXS>0 && DYE_ELV>5 && CORTIME>6'),
                'compact='+str('no'),
                'time='+str('TIME'),
                'clobber=yes'
            ]
            process = subprocess.Popen(['maketime', *inputs], text=True)
            with open(self.logfile, "a") as o:
                print(*process.args, sep=" ", file=o)
            process.wait()

            inputs = [
                'filename='+str(nxb_evt),
                #'eventsout='+str('merged_nxb_resolve_gtifix_ehkSel.evt'),
                'eventsout='+str('NXBv2_trendmerge_wGTI_EHK_VCLno27_fix_ehkSel.evt'),
                'imgfile='+str('NONE'),
                'phafile='+str('NONE'),
                'fitsbinlc='+str('NONE'),
                'regionfile='+str('NONE'),
                'timefile='+str('ehkSelA.gti'),
                'xcolf='+str('X'),
                'ycolf='+str('Y'),
                'tcol='+str('TIME'),
                'ecol='+str('PI'),
                'xcolh='+str('DETX'),
                'ycolh='+str('DETX'),
                'clobber=yes'
            ]
            process = subprocess.Popen(['extractor', *inputs], text=True)
            with open(self.logfile, "a") as o:
                print(*process.args, sep=" ", file=o)
            process.wait()

            inputs = [
                'filename='+str(cl_evt),
                'eventsout='+str('src_cl_ehkSel.evt'),
                'imgfile='+str('NONE'),
                'phafile='+str('NONE'),
                'fitsbinlc='+str('NONE'),
                'regionfile='+str('NONE'),
                'timefile='+str('ehkSelB.gti'),
                'xcolf='+str('X'),
                'ycolf='+str('Y'),
                'tcol='+str('TIME'),
                'ecol='+str('PI'),
                'xcolh='+str('DETX'),
                'ycolh='+str('DETX'),
                'clobber=yes'
            ]
            process = subprocess.Popen(['extractor', *inputs], text=True)
            with open(self.logfile, "a") as o:
                print(*process.args, sep=" ", file=o)
            process.wait()

            inputs = [
                'infile='+str('src_cl_ehkSel.evt[EVENTS]'),
                'outfile='+str('src_cl_ehkSel_evSel.evt'),
                'expression='+str('(PI>=600) && ((RISE_TIME+0.00075*DERIV_MAX)>46) && ((RISE_TIME+0.00075*DERIV_MAX)<58) && (ITYPE==0) && (STATUS[4]==b0) && (PIXEL!=27)'),
                'clobber=yes'
            ]
            process = subprocess.Popen(['ftselect', *inputs], text=True)
            with open(self.logfile, "a") as o:
                print(*process.args, sep=" ", file=o)
            process.wait()

            inputs = [
                'infile='+str('src_cl_ehkSel_evSel.evt'),
                'ehkfile='+str(ehkfile),
                'regfile='+str('NONE'),
                'pixels='+str('-'),
                'innxbfile='+str('NXBv2_trendmerge_wGTI_EHK_VCLno27_fix_ehkSel.evt'),
                'innxbehk='+str(nxb_ehk),
                'database='+str('LOCAL'),
                'db_location='+str('./'),
                'timefirst='+str('-150'),
                'timelast='+str('+150'),
                'SORTCOL='+str('CORTIME'),
                'sortbin='+str('0,6,8,10,12,99'),
                'expr='+str('(PI>=600) && ((RISE_TIME+0.00075*DERIV_MAX)>46) && ((RISE_TIME+0.00075*DERIV_MAX)<58) && (ITYPE==0) && (STATUS[4]==b0) && (PIXEL!=27)'),
                'outpifile='+str('rslnxb.pi'),
                'outnxbfile='+str('rslnxb.evt'),
                'outnxbehk='+str('rslnxb.ehk'),
                'clobber=yes'
            ]
            process = subprocess.Popen(['rslnxbgen', *inputs], text=True)
            with open(self.logfile, "a") as o:
                print(*process.args, sep=" ", file=o)
            process.wait()

            process = subprocess.Popen(['fparkey', '1', 'rslnxb.pi', 'BACKSCAL'], text=True)
            with open(self.logfile, "a") as o:
                print(*process.args, sep=" ", file=o)
            process.wait()

            if self.optgrppifile != None:
                self.ftrbnrmf("newdiag60000.rmf.gz", "newdiag60000_obin1.rmf", phafile=self.optgrppifile, cmpmode="phafile")


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
        with open(self.logfile, "a") as o:
            print(*process.args, sep=" ", file=o)
        process.wait()
        results = process.communicate()
        ra, dec = re.findall(r'([-\d\.]+)',results[0])
        return ra, dec

    def get_radec_nom(self, eventfile):
        if not os.path.isfile(eventfile):
            print(str(eventfile) + ' does not exist.')
            return 0, 0, 0
        else:
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

    def rsl_make_region(self, outroot, RA_NOM, DEC_NOM, PA_NOM, pixlist="0:11,13:26,28:35"):
        inputs =[
            'instrume=RESOLVE',
            'ra={0}'.format(RA_NOM),
            'dec={0}'.format(DEC_NOM),
            'roll={0}'.format(PA_NOM),
            'pixlist={0}'.format(pixlist),
            'outroot={0}'.format(outroot),
            'clobber=yes'
        ]
        process = subprocess.Popen(['xamkregion', *inputs], stdout=subprocess.PIPE, text=True)
        with open(self.logfile, "a") as o:
            print(*process.args, sep=" ", file=o)
        process.wait()

    def ftgrouppha(self, infile, outfile, backfile, respfile, grouptype, groupscale):
        if not os.path.isfile(infile):
            print(str(infile) + ' does not exist.')
            return 1
        else:
            inputs = [
                'infile='+infile,
                'outfile='+outfile,
                'backfile='+backfile,
                'respfile='+respfile,
                'grouptype='+grouptype,
                'groupscale='+groupscale
            ]
            process = subprocess.Popen(['ftgrouppha', *inputs], text=True)
            with open(self.logfile, "a") as o:
                print(*process.args, sep=" ", file=o)
            process.wait()

    def ftrbnrmf(self, infile, outfile, phafile="none", cmpmode="none", ecmpmode="none", inarffile="none", outarffile="none"):
        if not os.path.isfile(infile):
            print(str(infile) + ' does not exist.')
            return 1
        else:
            inputs = [
                'infile='+infile,
                'outfile='+outfile,
                'cmpmode='+cmpmode,
                'ecmpmode='+ecmpmode,
                'inarffile='+inarffile,
                'outarffile='+outarffile,
                'phafile='+phafile,
                'clobber=yes'
            ]
            process = subprocess.Popen(['ftrbnrmf', *inputs], text=True)
            with open(self.logfile, "a") as o:
                print(*process.args, sep=" ", file=o)
            process.wait()

    def ftrbnpha(self, infile, outfile, phafile):
        if not os.path.isfile(infile):
            print(str(infile) + ' does not exist.')
            return 1
        else:
            inputs = [
                'infile='+infile,
                'outfile='+outfile,
                'phafile='+phafile,
                'properr=no',
                'error=poiss-0',
                'clobber=yes'
            ]
            process = subprocess.Popen(['ftrbnpha', *inputs], text=True)
            with open(self.logfile, "a") as o:
                print(*process.args, sep=" ", file=o)
            process.wait()

    def fparkey(self, value, fitsfile, keyword, comm=" ", add="no", insert='0'):
        inputs = [
            'value='+str(value),
            'fitsfile='+str(fitsfile),
            'keyword='+str(keyword),
            'comm='+str(comm),
            'add='+str(add),
            'insert='+str(insert)
        ]
        process = subprocess.Popen(['fparkey', *inputs], text=True)
        with open(self.logfile, "a") as o:
            print(*process.args, sep=" ", file=o)
        process.wait()

    def bgd_rmf_arf(self, srcfile, backfile, respfile, ancrfile):
        if not os.path.isfile(srcfile):
            print(str(srcfile) + ' does not exist.')
            return 1
        else:
            self.fparkey(backfile, srcfile, 'BACKFILE')
            self.fparkey(respfile, srcfile, 'RESPFILE')
            self.fparkey(ancrfile, srcfile, 'ANCRFILE')

    def optrbin_comb(self, specfile, backfile, respfile, ancrfile):
        if not os.path.isfile(specfile):
            print(str(specfile) + ' does not exist.')
            return 1
        else:
            outgrppifile = pathlib.PurePath(specfile).stem + "_grpobin1.pi"
            outrmffile = pathlib.PurePath(respfile).stem + "_obin1.rmf"
            respfile1 = respfile.replace("_comb", "")
            respfile2 = respfile.replace("_comb", "_elc")
            outrmffile1 = pathlib.PurePath(respfile1).stem + "_obin1.rmf"
            outrmffile2 = pathlib.PurePath(respfile2).stem + "_obin1.rmf"
            outpifile = pathlib.PurePath(specfile).stem + "_obin1.pi"

            self.ftgrouppha(specfile, outgrppifile, backfile, respfile, "optmin", "1")
            self.bgd_rmf_arf(outgrppifile, backfile, respfile, ancrfile)
            self.ftrbnrmf(respfile1, outrmffile1, phafile=outgrppifile, cmpmode="phafile")
            self.ftrbnrmf(respfile2, outrmffile2, phafile=outgrppifile, cmpmode="phafile")
            shutil.copy(outrmffile1, outrmffile)
            process = subprocess.Popen(['ftappend', outrmffile2+"[EBOUNDS]", outrmffile], text=True)
            with open(self.logfile, "a") as o:
                print(*process.args, sep=" ", file=o)
            process.wait()
            process = subprocess.Popen(['ftappend', outrmffile2+"[MATRIX]", outrmffile], text=True)
            with open(self.logfile, "a") as o:
                print(*process.args, sep=" ", file=o)
            process.wait()
            self.fparkey("EBOUNDS", outrmffile+"[1]", "EXTENSION", add="yes")
            self.fparkey("1", outrmffile+"[1]", "EXTVER", add="yes")
            self.fparkey("MATRIX", outrmffile+"[2]", "EXTENSION", add="yes")
            self.fparkey("1", outrmffile+"[2]", "EXTVER", add="yes")
            self.fparkey("EBOUNDS", outrmffile+"[3]", "EXTENSION", add="yes")
            self.fparkey("2", outrmffile+"[3]", "EXTVER", add="yes")
            self.fparkey("MATRIX", outrmffile+"[4]", "EXTENSION", add="yes")
            self.fparkey("2", outrmffile+"[4]", "EXTVER", add="yes")
            self.ftrbnpha(specfile, outpifile, outgrppifile)
            self.bgd_rmf_arf(outpifile, backfile, outrmffile, ancrfile)

            self.optgrppifile = outgrppifile


    def optrbin(self, specfile, backfile, respfile, ancrfile):
        if not os.path.isfile(specfile):
            print(str(specfile) + ' does not exist.')
            return 1
        else:
            outgrppifile = pathlib.PurePath(specfile).stem + "_grpobin1.pi"
            outrmffile = pathlib.PurePath(respfile).stem + "_obin1.rmf"
            outpifile = pathlib.PurePath(specfile).stem + "_obin1.pi"

            self.ftgrouppha(specfile, outgrppifile, backfile, respfile, "optmin", "1")
            self.bgd_rmf_arf(outgrppifile, backfile, respfile, ancrfile)
            self.ftrbnrmf(respfile, outrmffile, phafile=outgrppifile, cmpmode="phafile")
            self.ftrbnpha(specfile, outpifile, outgrppifile)
            self.bgd_rmf_arf(outpifile, backfile, outrmffile, ancrfile)

            self.optgrppifile = outgrppifile

    def rsl_products(self):
        obsid = self.obsid
        filter = self.filter
        whichrmf = self.whichrmf
        eventsdir = self.eventsdir
        eventfile = '{0}rsl_p0px{1}_cl.evt.gz'.format(obsid, filter)
        regionfile = "region_RSL_det_27.reg"
        specfile = "{0}rsl_src.pi".format(obsid)
        outfile = "{0}rsl_srgr1.pi".format(obsid)
        backfile = "NONE"
        respfile = "{0}rsl_{1}.rmf".format(obsid, whichrmf)
        ancrfile = "{0}rsl_{1}.arf".format(obsid, whichrmf)
        grouptype = "min"
        groupscale = "1"
        self.rsl_copy(eventsdir, obsid, filter)
        eventfile = self.rsl_rise_time_screening(eventfile, obsid, filter)
        self.rsl_lcextract(eventfile, obsid)
        self.rsl_imgextract(eventfile, obsid, filter, mode='DET', bmin=4000, bmax=19999)
        self.rsl_specextract(eventfile, specfile)
        self.rsl_mkrmf(eventfile, respfile, whichrmf)

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
        if 'comb' in whichrmf:
            self.optrbin_comb(specfile, backfile, respfile, ancrfile)
        else:
            self.optrbin(specfile, backfile, respfile, ancrfile)

        self.rsl_make_region(obsid+'rsl', RA_NOM, DEC_NOM, PA_NOM)

    def rsl_products_Ls(self):
        obsid = self.obsid
        filter = self.filter
        whichrmf = self.whichrmf
        eventsdir = self.eventsdir
        eventfile = '{0}rsl_p0px{1}_cl.evt.gz'.format(obsid, filter)
        regionfile = "region_RSL_det_27.reg"
        specfile = "{0}rsl_woLs_src.pi".format(obsid)
        outfile = "{0}rsl_woLs_srgr1.pi".format(obsid)
        backfile = "NONE"
        respfile = "{0}rsl_woLs_{1}.rmf".format(obsid, whichrmf)
        ancrfile = "{0}rsl_woLs_{1}.arf".format(obsid, whichrmf)
        grouptype = "min"
        groupscale = "1"
        self.rsl_copy(eventsdir, obsid, filter)
        eventfile = self.rsl_rise_time_screening(eventfile, obsid, filter)
        eventfile = self.rsl_remove_Ls(eventfile, obsid, filter)
        self.rsl_specextract(eventfile, specfile)
        self.rsl_lcextract(eventfile, obsid)
        self.rsl_imgextract(eventfile, obsid, filter, mode='DET', bmin=4000, bmax=19999)
        eventfile_rmf = self.rsl_evtfile_for_rmf(eventfile, obsid, filter)
        self.rsl_mkrmf(eventfile_rmf, respfile, whichrmf)

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
        if 'comb' in whichrmf:
            self.optrbin_comb(specfile, backfile, respfile, ancrfile)
        else:
            self.optrbin(specfile, backfile, respfile, ancrfile)

        self.rsl_make_region(obsid+'rsl', RA_NOM, DEC_NOM, PA_NOM)

    def rsl_products_gain(self):
        obsid = self.obsid
        filter = self.filter
        whichrmf = self.whichrmf
        eventsdir = self.eventsdir
        regionfile = "region_RSL_det_27.reg"
        specfile = "{0}rsl_src.pi".format(obsid)
        outfile = "{0}rsl_srgr1.pi".format(obsid)
        backfile = "NONE"
        respfile = "{0}rsl_{1}.rmf".format(obsid, whichrmf)
        ancrfile = "{0}rsl_{1}.arf".format(obsid, whichrmf)
        grouptype = "min"
        groupscale = "1"
        self.rsl_copy(eventsdir, obsid, filter)
        eventfile = '{0}rsl_p0px{1}_cl.evt.gz'.format(obsid, filter)
        eventfile = self.rsl_gain_gti(eventfile, eventsdir, obsid, filter)
        eventfile = self.rsl_rise_time_screening(eventfile, obsid, filter)
        self.rsl_lcextract(eventfile, obsid)
        self.rsl_imgextract(eventfile, obsid, filter, mode='DET', bmin=4000, bmax=19999)
        self.rsl_specextract(eventfile, specfile)
        self.rsl_mkrmf(eventfile, respfile, whichrmf)

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

    def rsl_products_gain_Ls(self):
        obsid = self.obsid
        filter = self.filter
        whichrmf = self.whichrmf
        eventsdir = self.eventsdir
        regionfile = "region_RSL_det_27.reg"
        specfile = "{0}rsl_Ls_excluded_src.pi".format(obsid)
        outfile = "{0}rsl_Ls_excluded_srgr1.pi".format(obsid)
        backfile = "NONE"
        respfile = "{0}rsl_Ls_excluded_{1}.rmf".format(obsid, whichrmf)
        ancrfile = "{0}rsl_Ls_excluded_{1}.arf".format(obsid, whichrmf)
        grouptype = "min"
        groupscale = "1"
        self.rsl_copy(eventsdir, obsid, filter)
        eventfile = '{0}rsl_p0px{1}_cl.evt.gz'.format(obsid, filter)
        eventfile = self.rsl_gain_gti(eventfile, eventsdir, obsid, filter)
        eventfile = self.rsl_rise_time_screening_Ls_excluded(eventfile, obsid, filter)
        self.rsl_lcextract(eventfile, obsid)
        self.rsl_imgextract(eventfile, obsid, filter, mode='DET', bmin=4000, bmax=19999)
        self.rsl_specextract(eventfile, specfile)
        self.rsl_mkrmf(eventfile, respfile, whichrmf)

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

    def rsl_products_pixel(self, eventfile, pix):
        obsid = self.obsid
        filter = self.filter
        whichrmf = self.whichrmf
        pixel_map = self.pixel_map
        specfile = "{0}rsl_src_pix{1:02d}.pi".format(obsid, pix)
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
    eventsdir = args.eventsdir
    productsdir = args.productsdir
    rsl = ResolveTools(obsid, filter, whichrmf, eventsdir, productsdir)
    if args.lsexclude:
        rsl.rsl_products_Ls()
    else:
        rsl.rsl_products()
    if args.rslnxbgen:
        shutil.copy('/home/ogawa/work/tools/heasoft/xrism/newdiag60000.rmf.gz', rsl.productsdir)
        rsl.rsl_nxbgen(rsl.eventfile, rsl.ehkfile, nxb_ehk='NXBv2_merged_sorted_fix.ehk.gz', nxb_evt='NXBv2_trendmerge_wGTI_EHK_VCLno27_fix.evt')
