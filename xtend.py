import datetime
import os
from pathlib import Path
import re
import shutil
import subprocess

class XtendTools:

    def __init__(self, obsid, dataclass, eventdir='..', productsdir='.'):
        self.obsid = obsid
        self.dataclass = dataclass
        self.eventdir = eventdir
        self.productsdir = productsdir
        self.TOOLS = os.environ.get("TOOLS", "")

        os.chdir(productsdir)
        now = datetime.datetime.now()
        pfiles_dir = "pfiles" + now.strftime('%Y%m%d%H%M%S')
        os.makedirs(pfiles_dir, exist_ok=True)
        pfiles_path = Path(pfiles_dir).resolve()
        self.pfiles_path = pfiles_path
        headas_syspfiles = os.environ.get("HEADAS", "") + "/syspfiles"
        pfiles_env = str(pfiles_path) + ";" + headas_syspfiles
        os.environ["PFILES"] = pfiles_env

    def __del__(self):
        shutil.rmtree(self.pfiles_path)

    def xtd_copy(self, eventdir, obsid, dataclass):
        eventfile = '{0}xtd_p0{1}_cl.evt.gz'.format(obsid, dataclass)
        bimgfile = '{0}xtd_p0{1}.bimg.gz'.format(obsid, dataclass)
        fpixfile = '{0}xtd_a0{1}.fpix.gz'.format(obsid, dataclass)
        ehkfile = '{0}.ehk.gz'.format(obsid)
        if os.path.islink(eventfile): os.unlink(eventfile)
        if os.path.islink(bimgfile): os.unlink(bimgfile)
        if os.path.islink(fpixfile): os.unlink(fpixfile)
        if os.path.islink(ehkfile): os.unlink(ehkfile)

        os.symlink('{0}/xtend/event_cl/{1}'.format(eventdir, eventfile), eventfile)
        os.symlink('{0}/xtend/event_uf/{1}'.format(eventdir, bimgfile), bimgfile)
        os.symlink('{0}/xtend/event_uf/{1}'.format(eventdir, fpixfile), fpixfile)
        os.symlink('{0}/auxil/{1}'.format(eventdir, ehkfile), ehkfile)

        with open("exclude_calsources.reg", "w") as f:
            f.write("physical\n")
            f.write("-circle(920.0,1530.0,92.0)\n")
            f.write("-circle(919.0,271.0,91.0)\n")

    def xtd_imgextract(self, eventfile, obsid, dataclass, mode='DET', bmin=83, bmax=1667):
        commands = ['']
        commands.append('xsel')
        commands.append('no')
        commands.append('read event {0}'.format(eventfile))
        commands.append('./')
        commands.append('yes')
        commands.append('set image {0}'.format(mode))
        commands.append('filter region exclude_calsources.reg')
        commands.append('filter pha_cutoff {0} {1}'.format(bmin, bmax))
        commands.append('extract image')
        commands.append('save image {0}xtd_p0{1}_detimg.fits clobber=yes'.format(obsid, dataclass))
        commands.append('exit')
        commands.append('no')

        process = subprocess.Popen(['xselect'], stdin=subprocess.PIPE, text=True)
        results = process.communicate('\n'.join(commands))
        process.wait()

    def xtd_specextract(self, eventfile, specfile):
        commands = []
        commands.append('xsel')
        commands.append('no')
        commands.append('read event {0}'.format(eventfile))
        commands.append('./')
        commands.append('yes')
        commands.append('set image det')
        commands.append('filter region region_xtd_src.reg')
        commands.append('extract spectrum')
        commands.append('save spec {0} clobber=yes'.format(specfile))
        commands.append('exit')
        commands.append('no')

        process = subprocess.Popen(['xselect'], stdin=subprocess.PIPE, text=True)
        results = process.communicate('\n'.join(commands))
        process.wait()

    def xtd_backextract(self, eventfile, backfile):
        commands = []
        commands.append('xsel')
        commands.append('no')
        commands.append('read event {0}'.format(eventfile))
        commands.append('./')
        commands.append('yes')
        commands.append('set image det')
        commands.append('filter region region_xtd_bgd.reg')
        commands.append('extract spectrum')
        commands.append('save spec {0} clobber=yes'.format(backfile))
        commands.append('exit')
        commands.append('no')

        process = subprocess.Popen(['xselect'], stdin=subprocess.PIPE, text=True)
        results = process.communicate('\n'.join(commands))
        process.wait()

    def xtd_srclcextract(self, eventfile, obsid, bmin=83, bmax=1667, binsize='128'):
        commands = []
        commands.append('xsel')
        commands.append('no')
        commands.append('read event {0}'.format(eventfile))
        commands.append('./')
        commands.append('yes')
        commands.append('set image det')
        commands.append('filter region region_xtd_src.reg')
        commands.append('filter pha_cutoff {0} {1}'.format(bmin, bmax))
        commands.append('set binsize {0}'.format(binsize))
        commands.append('extr curve exposure=0.6')
        commands.append('save curve {0}xtd_0p5to10keV_b{1}_src_lc.fits clobber=yes'.format(obsid, binsize))
        commands.append('exit')
        commands.append('no')

        process = subprocess.Popen(['xselect'], stdin=subprocess.PIPE, text=True)
        results = process.communicate('\n'.join(commands))
        process.wait()

    def xtd_bgdlcextract(self, eventfile, obsid, bmin=83, bmax=1667, binsize='128'):
        commands = []
        commands.append('xsel')
        commands.append('no')
        commands.append('read event {0}'.format(eventfile))
        commands.append('./')
        commands.append('yes')
        commands.append('set image det')
        commands.append('filter region region_xtd_bgd.reg')
        commands.append('filter pha_cutoff {0} {1}'.format(bmin, bmax))
        commands.append('set binsize {0}'.format(binsize))
        commands.append('extr curve exposure=0.6')
        commands.append('save curve {0}xtd_0p5to10keV_b{1}_bgd_lc.fits clobber=yes'.format(obsid, binsize))
        commands.append('exit')
        commands.append('no')

        process = subprocess.Popen(['xselect'], stdin=subprocess.PIPE, text=True)
        results = process.communicate('\n'.join(commands))
        process.wait()

    def xtd_mkrmf(self, specfile, respfile):
        infile = "{0}".format(specfile)
        inputs = [
            'infile='+infile,
            'outfile='+respfile,
            'rmfparam=CALDB',
            'eminin=200',
            'dein=2,24',
            'nchanin=5900,500',
            'eminout=0.0',
            'deout=6',
            'nchanout=4096',
            'clobber=yes',
        ]
        process = subprocess.Popen(['xtdrmf', *inputs], text=True)
        process.wait()

    def xtd_xaexpmap(self, eventfile, obsid, dataclass):
        inputs = [
            'ehkfile={0}.ehk.gz'.format(obsid),
            'gtifile={0}'.format(eventfile),
            'instrume=XTEND',
            'badimgfile={0}xtd_p0{1}.bimg.gz'.format(obsid, dataclass),
            'pixgtifile={0}xtd_a0{1}.fpix.gz'.format(obsid, dataclass),
            'outfile={0}xtd_a0{1}.expo'.format(obsid, dataclass),
            'outmaptype=EXPOSURE',
            'delta=20.0',
            'numphi=1',
            'stopsys=SKY',
            'instmap={0}/heasoft/xrism/xa_xtd_instmap_20190101v004.fits'.format(self.TOOLS),
            'qefile=CALDB',
            'contamifile=CALDB',
            'vigfile=CALDB',
            'obffile=CALDB',
            'fwfile=CALDB',
            'gvfile=CALDB',
            'maskcalsrc=yes',
            'fwtype=FILE',
            'specmode=MONO',
            'specfile=spec.fits',
            'specform=FITS',
            'evperchan=DEFAULT',
            'abund=1',
            'cols=0',
            'covfac=1',
            'clobber=yes',
            'chatter=1',
            'logfile=make_expo_{0}xtd_p0{1}.log'.format(obsid, dataclass)
        ]
        process = subprocess.Popen(['xaexpmap', *inputs], text=True)
        process.wait()

    def xtd_xaarfgen(self, eventfile, respfile, ancrfile, obsid, dataclass):
        RA_NOM, DEC_NOM, PA_NOM = self.get_radec_nom(eventfile)
        with open("region_xtd_src.reg", "r") as f:
            s = f.read()
            XDETX0=re.search(r'\(([\d\.]*),([\d\.]*),[\d\.]*,[\d\.]*,[\d\.]*\)', s).group(1)
            XDETY0=re.search(r'\(([\d\.]*),([\d\.]*),[\d\.]*,[\d\.]*,[\d\.]*\)', s).group(2)
        ra, dec = self.coordpnt(RA_NOM, DEC_NOM, PA_NOM, X0=XDETX0, Y0=XDETY0)
        inputs = [
            'xrtevtfile=raytrace_{0}xtd_p0{1}_boxreg_ptsrc.fits'.format(obsid, dataclass),
            'source_ra={0}'.format(ra),
            'source_dec={0}'.format(dec),
            'telescop=XRISM',
            'instrume=XTEND',
            'emapfile={0}xtd_a0{1}.expo'.format(obsid, dataclass),
            'regmode=DET',
            'regionfile=region_xtd_src.reg',
            'sourcetype=POINT',
            'rmffile={0}'.format(respfile),
            'erange=0.3 18.0 0 0',
            'outfile={0}'.format(ancrfile),
            'numphoton=300000',
            'minphoton=100',
            'teldeffile=CALDB',
            'qefile=CALDB',
            'contamifile=CALDB',
            'obffile=CALDB',
            'fwfile=CALDB',
            'onaxisffile=CALDB',
            'onaxiscfile=CALDB',
            'mirrorfile=CALDB',
            'obstructfile=CALDB',
            'frontreffile=CALDB',
            'backreffile=CALDB',
            'pcolreffile=CALDB',
            'scatterfile=CALDB',
            'mode=h',
            'clobber=yes',
            'seed=7',
            'imgfile=NONE'
        ]
        process = subprocess.Popen(['xaarfgen', *inputs], text=True)
        process.wait()

    def coordpnt(self, RA_NOM, DEC_NOM, PA_NOM, X0=3.5, Y0=3.5):
        inputs =[
            'input={0},{1}'.format(X0, Y0),
            'outfile=NONE',
            'telescop=XRISM',
            'instrume=XTEND',
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

    def xtd_products(self):
        obsid = self.obsid
        dataclass = self.dataclass
        eventdir = self.eventdir
        eventfile = '{0}xtd_p0{1}_cl.evt.gz'.format(obsid, dataclass)
        specfile = "{0}xtd_src.pi".format(obsid)
        outfile = "{0}xtd_srgr1.pi".format(obsid)
        backfile = "{0}xtd_bgd.pi".format(obsid)
        respfile = "{0}xtd_src.rmf".format(obsid)
        ancrfile = "{0}xtd_src.arf".format(obsid)
        grouptype = "min"
        groupscale = "1"
        self.xtd_copy(eventdir, obsid, dataclass)
        self.xtd_srclcextract(eventfile, obsid)
        self.xtd_bgdlcextract(eventfile, obsid)
        self.xtd_imgextract(eventfile, obsid, dataclass, mode='DET', bmin=4000, bmax=20000)
        self.xtd_specextract(eventfile, specfile)
        self.xtd_backextract(eventfile, backfile)
        self.xtd_mkrmf(eventfile, respfile)
        self.xtd_xaexpmap(eventfile, obsid, dataclass)
        self.xtd_xaarfgen(eventfile, respfile, ancrfile, obsid, dataclass)
        self.ftgrouppha(specfile, outfile, backfile, respfile, grouptype, groupscale)
        self.bgd_rmf_arf(outfile, backfile, respfile, ancrfile)
