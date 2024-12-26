#! /usr/bin/env python3

from argparse import ArgumentParser
import datetime
import os
import pathlib
import re
import math
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
    argparser = ArgumentParser(description='This is the Xtend data reduction program.')
    argparser.add_argument('-oi', '--obsid', default='xa000162000', help='OBSID')
    argparser.add_argument('-dc', '--dataclass', default='31100010', help='Filter ID')
    argparser.add_argument('-ed', '--eventsdir', default='..', help='Eventfile directory path')
    argparser.add_argument('-pd', '--productsdir', default='.', help='Products directory path')
    argparser.add_argument('--imgonly', action='store_true', help='Flag for only image')
    return argparser.parse_args()

class XtendTools:

    def __init__(self, obsid, dataclass, eventsdir='..', productsdir='.'):
        self.obsid = obsid
        self.dataclass = dataclass
        self.eventsdir =  pathlib.Path(eventsdir).resolve()
        self.productsdir =  pathlib.Path(productsdir).resolve()

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

    def xtd_copy(self, eventsdir, obsid, dataclass):
        eventsdir = pathlib.Path(eventsdir).resolve()
        eventfile = '{0}xtd_p0{1}_cl.evt.gz'.format(obsid, dataclass)
        bimgfile = '{0}xtd_p0{1}.bimg.gz'.format(obsid, dataclass)
        fpixfile = '{0}xtd_a0{1}.fpix.gz'.format(obsid, dataclass)
        ehkfile = '{0}.ehk.gz'.format(obsid)

        orgevtfile = eventsdir.joinpath('xtend/event_cl/{0}'.format(eventfile))
        orgbimgfile = eventsdir.joinpath('xtend/event_uf/{0}'.format(bimgfile))
        orgfpixfile = eventsdir.joinpath('xtend/event_uf/{0}'.format(fpixfile))
        orgehkfile = eventsdir.joinpath('auxil/{0}'.format(ehkfile))

        if not orgevtfile.exists():
            print(str(orgevtfile) + ' does not exist.')
        elif not orgbimgfile.exists():
            print(str(orgbimgfile) + ' does not exist.')
        #elif not orgfpixfile.exists():
        #    print(str(orgfpixfile) + ' does not exist.')
        elif not orgehkfile.exists():
            print(str(orgehkfile) + ' does not exist.')
        else:

            if pathlib.Path(eventfile).exists() or pathlib.Path(eventfile).is_symlink(): pathlib.Path(eventfile).unlink()
            if pathlib.Path(bimgfile).exists() or pathlib.Path(bimgfile).is_symlink(): pathlib.Path(bimgfile).unlink()
            if pathlib.Path(fpixfile).exists() or pathlib.Path(fpixfile).is_symlink(): pathlib.Path(fpixfile).unlink()
            if pathlib.Path(ehkfile).exists() or pathlib.Path(ehkfile).is_symlink(): pathlib.Path(ehkfile).unlink()

            os.symlink(orgevtfile, eventfile)
            os.symlink(orgbimgfile, bimgfile)
            os.symlink(orgfpixfile, fpixfile)
            os.symlink(orgehkfile, ehkfile)

            with open("exclude_calsources.reg", "w") as f:
                f.write("physical\n")
                f.write("-circle(920.0,1530.0,92.0)\n")
                f.write("-circle(919.0,271.0,91.0)\n")

    def xtd_imgextract(self, eventfile, obsid, dataclass, mode='sky', bmin=83, bmax=1665):
        if not os.path.isfile(eventfile):
            print(str(eventfile) + ' does not exist.')
            return 1
        elif not os.path.isfile("exclude_calsources.reg"):
            print('exclude_calsources.reg does not exist.')
            return 1
        else:
            commands = [
                'xsel',
                'no',
                'read event {0}'.format(eventfile),
                './',
                'yes',
                'set image {0}'.format(mode),
                #'filter region exclude_calsources.reg',
                'filter pha_cutoff {0} {1}'.format(bmin, bmax),
                'extract image',
                'save image {0}xtd_p0{1}_{2}img.fits clobber=yes'.format(obsid, dataclass, mode),
                'exit',
                'no'
            ]
            process = subprocess.Popen(['xselect'], stdin=subprocess.PIPE, text=True)
            results = process.communicate('\n'.join(commands))
            with open(self.logfile, "a") as o:
                print("xselect <<EOF\n{}\nEOF".format('\n'.join(commands)), file=o)
            process.wait()

    def xtd_specextract(self, eventfile, specfile, regionfile, mode='sky'):
        if not os.path.isfile(eventfile):
            print(str(eventfile) + ' does not exist.')
            return 1
        elif not os.path.isfile(regionfile):
            print(str(regionfile) + ' does not exist.')
            return 1
        else:
            commands = [
                'xsel',
                'no',
                'read event {0}'.format(eventfile),
                './',
                'yes',
                'set image {0}'.format(mode),
                'filter region {0}'.format(regionfile),
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

    def xtd_lcextract(self, eventfile, outfile, regionfile, bmin='83', bmax='1665', binsize='128', mode='sky'):
        if not os.path.isfile(eventfile):
            print(str(eventfile) + ' does not exist.')
            return 1
        elif not os.path.isfile(regionfile):
            print(str(regionfile) + ' does not exist.')
            return 1
        else:
            commands = [
                'xsel',
                'no',
                'read event {0}'.format(eventfile),
                './',
                'yes',
                'set image {0}'.format(mode),
                'filter region {0}'.format(regionfile),
                'filter pha_cutoff {0} {1}'.format(bmin, bmax),
                'set binsize {0}'.format(binsize),
                'extr curve exposure=0.6',
                'save curve {0} clobber=yes'.format(outfile),
                'exit',
                'no'
            ]
            process = subprocess.Popen(['xselect'], stdin=subprocess.PIPE, text=True)
            results = process.communicate('\n'.join(commands))
            with open(self.logfile, "a") as o:
                print("xselect <<EOF\n{}\nEOF".format('\n'.join(commands)), file=o)
            process.wait()

    def xtd_mkrmf(self, infile, outfile, rmfparam='CALDB', eminin='200', dein='2,24', nchanin='5900,500', eminout='0.0', deout='6', nchanout='4096' ,clobber='yes'):
        if not os.path.isfile(infile):
            print(str(infile) + ' does not exist.')
            return 1
        else:
            inputs = [
                'infile='+str(infile),
                'outfile='+str(outfile),
                'rmfparam='+str(rmfparam),
                'eminin='+str(eminin),
                'dein='+str(dein),
                'nchanin='+str(nchanin),
                'eminout='+str(eminout),
                'deout='+str(deout),
                'nchanout='+str(nchanout),
                'clobber='+str(clobber)
            ]
            process = subprocess.Popen(['punlearn', 'xtdrmf'], text=True)
            with open(self.logfile, "a") as o:
                print(*process.args, sep=" ", file=o)
            process.wait()
            process = subprocess.Popen(['xtdrmf', *inputs], text=True)
            with open(self.logfile, "a") as o:
                print(*process.args, sep=" ", file=o)
            process.wait()

    def xtd_xaexpmap(self, ehkfile, gtifile, badimgfile, pixgtifile, outfile, logfile, instrume='XTEND', outmaptype='EXPOSURE', delta='20.0', numphi='1', stopsys='SKY', instmap='CALDB', qefile='CALDB', contamifile='CALDB', vigfile='CALDB', obffile='CALDB', fwfile='CALDB', gvfile='CALDB', maskcalsrc='yes', fwtype='FILE', specmode='MONO', specfile='spec.fits', specform='FITS', evperchan='DEFAULT', abund='1', cols='0', covfac='1', clobber='yes', chatter='1'):
        if not os.path.isfile(ehkfile):
            print(str(ehkfile) + ' does not exist.')
            return 1
        elif not os.path.isfile(gtifile):
            print(str(gtifile) + ' does not exist.')
            return 1
        elif not os.path.isfile(badimgfile):
            print(str(badimgfile) + ' does not exist.')
            return 1
        elif not os.path.isfile(pixgtifile) and pixgtifile!='NONE':
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

    def xtd_xaarfgen(self, xrtevtfile, respfile, ancrfile, source_ra, source_dec, emapfile, telescop='XRISM', instrume='XTEND', regmode='READEC', regionfile='region_xtd_src.reg', sourcetype='POINT', erange='0.3 18.0 0 0', numphoton='600000', minphoton='100', teldeffile='CALDB', qefile='CALDB', contamifile='CALDB', obffile='CALDB', fwfile='CALDB', onaxisffile='CALDB', onaxiscfile='CALDB', mirrorfile='CALDB', obstructfile='CALDB', frontreffile='CALDB', backreffile='CALDB', pcolreffile='CALDB', scatterfile='CALDB', mode='h', clobber='yes', seed='7', imgfile='NONE'):
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

    def coordpnt(self, RA_NOM, DEC_NOM, PA_NOM, X0=3.5, Y0=3.5, mode="SKY"):
        inputs =[
            'input={0},{1}'.format(X0, Y0),
            'outfile=NONE',
            'telescop=XRISM',
            'instrume=XTEND',
            'teldeffile=CALDB',
            'startsys={0}'.format(mode),
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

    def xtd_make_region(self, srcregionfile, bgdregionfile, RA_NOM, DEC_NOM, PA_NOM, dataclass):
        if dataclass[0:3] == '300':
            with open(srcregionfile, "w") as f:
                f.write("fk5\n")
                f.write('circle({0},{1},150")\n'.format(RA_NOM, DEC_NOM))
            with open(bgdregionfile, "w") as f:
                RA = float(RA_NOM) - math.cos(float(PA_NOM)-math.pi*0.5) * 5/60 *3
                DEC = float(DEC_NOM) - math.sin(float(PA_NOM)-math.pi*0.5) * 5/60 *3
                f.write("fk5\n")
                f.write('circle({0},{1},150")\n'.format(RA, DEC))
        else:
            with open(srcregionfile, "w") as f:
                f.write("fk5\n")
                f.write('box({0},{1},120.000",300.000",{2})\n'.format(RA_NOM, DEC_NOM, PA_NOM))
            with open(bgdregionfile, "w") as f:
                f.write("fk5\n")
                RA = float(RA_NOM) - math.cos(float(PA_NOM)-math.pi*0.5) * 5/60 *3
                DEC = float(DEC_NOM) - math.sin(float(PA_NOM)-math.pi*0.5) * 5/60 *3
                f.write('box({0},{1},120.000",300.000",{2})\n'.format(RA, DEC, PA_NOM))
        return 0

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
            process.wait()

    def xtd_products(self):
        obsid = self.obsid
        dataclass = self.dataclass
        eventsdir = self.eventsdir
        eventfile = '{0}xtd_p0{1}_cl.evt.gz'.format(obsid, dataclass)
        specfile = "{0}xtd_src.pi".format(obsid)
        outfile = "{0}xtd_srgr30.pi".format(obsid)
        backfile = "{0}xtd_bgd.pi".format(obsid)
        respfile = "{0}xtd_src.rmf".format(obsid)
        ancrfile = "{0}xtd_src.arf".format(obsid)
        binsize = "128"
        srclcfile = "{0}xtd_0p5to10keV_b{1}_src_lc.fits".format(obsid, binsize)
        bgdlcfile = "{0}xtd_0p5to10keV_b{1}_bgd_lc.fits".format(obsid, binsize)
        grouptype = "min"
        groupscale = "30"
        srcregionfile = "region_xtd_src.reg"
        bgdregionfile = "region_xtd_bgd.reg"
        self.xtd_copy(eventsdir, obsid, dataclass)
        self.xtd_imgextract(eventfile, obsid, dataclass, mode='sky')
        self.xtd_lcextract(eventfile, srclcfile, srcregionfile, binsize=binsize, mode='sky')
        self.xtd_lcextract(eventfile, bgdlcfile, bgdregionfile, binsize=binsize, mode='sky')
        self.xtd_specextract(eventfile, specfile, srcregionfile, mode='sky')
        self.xtd_specextract(eventfile, backfile, bgdregionfile, mode='sky')
        self.xtd_mkrmf(specfile, respfile)

        ehkfile = '{0}.ehk.gz'.format(obsid)
        badimgfile = '{0}xtd_p0{1}.bimg.gz'.format(obsid, dataclass)
        pixgtifile = '{0}xtd_a0{1}.fpix.gz'.format(obsid, dataclass)
        emapfile = '{0}xtd_a0{1}.expo'.format(obsid, dataclass)
        logfile = 'make_expo_{0}xtd_p0{1}.log'.format(obsid, dataclass)
        self.xtd_xaexpmap(ehkfile=ehkfile, gtifile=eventfile, badimgfile=badimgfile, pixgtifile='NONE', outfile=emapfile, logfile=logfile)

        RA_NOM, DEC_NOM, PA_NOM = self.get_radec_nom(eventfile)
        if not os.path.isfile(srcregionfile): sys.exit(str(srcregionfile) + ' does not exist.')
        with open(srcregionfile, "r") as f:
            s = f.read()
            XTDX0=re.search(r'\(([\d\.]*),([\d\.]*),.+\)', s).group(1)
            XTDY0=re.search(r'\(([\d\.]*),([\d\.]*),.+\)', s).group(2)
        #source_ra, source_dec = self.coordpnt(RA_NOM, DEC_NOM, PA_NOM, X0=XTDX0, Y0=XTDY0, mode='SKY')
        source_ra = XTDX0
        source_dec = XTDY0
        xrtevtfile = 'raytrace_{0}xtd_p0{1}_boxreg_ptsrc.fits'.format(obsid, dataclass)
        self.xtd_xaarfgen(xrtevtfile=xrtevtfile, emapfile=emapfile, respfile=respfile, ancrfile=ancrfile, source_ra=source_ra, source_dec=source_dec, regmode='RADEC')

        self.ftgrouppha(specfile, outfile, backfile, respfile, grouptype, groupscale)
        self.bgd_rmf_arf(outfile, backfile, respfile, ancrfile)

    def xtd_img(self):
        obsid = self.obsid
        dataclass = self.dataclass
        eventsdir = self.eventsdir
        eventfile = '{0}xtd_p0{1}_cl.evt.gz'.format(obsid, dataclass)
        srcregionfile = "region_xtd_src.reg"
        bgdregionfile = "region_xtd_bgd.reg"
        self.xtd_copy(eventsdir, obsid, dataclass)
        self.xtd_imgextract(eventfile, obsid, dataclass)
        RA_NOM, DEC_NOM, PA_NOM = self.get_radec_nom(eventfile)
        self.xtd_make_region(srcregionfile, bgdregionfile, RA_NOM, DEC_NOM, PA_NOM, dataclass)
        self.rsl_make_region(obsid+'rsl', RA_NOM, DEC_NOM, PA_NOM)




if __name__ == "__main__":
    args = get_argument()
    obsid = args.obsid
    dataclass = args.dataclass
    eventsdir = args.eventsdir
    productsdir = args.productsdir
    xtd = XtendTools(obsid, dataclass, eventsdir, productsdir)
    if args.imgonly:
        xtd.xtd_img()
    else:
        xtd.xtd_products()
