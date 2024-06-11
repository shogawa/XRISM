import datetime
import os
from pathlib import Path
import re
import shutil
import subprocess

class ResolveTools:

    def __init__(self, obsid, filter, whichrmf, eventdir='../', productsdir='./'):
        self.obsid = obsid
        self.filter = filter
        self.whichrmf = whichrmf
        self.eventdir = eventdir
        self.productsdir = productsdir

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

    def rsl_copy(self, eventdir, obsid, filter):
        eventfile = '{0}rsl_p0px{1}_cl.evt.gz'.format(obsid, filter)
        pixgtifile = '{0}rsl_px{1}_exp.gti.gz'.format(obsid, filter)
        ehkfile = '{0}.ehk.gz'.format(obsid)
        if os.path.islink(eventfile): os.unlink(eventfile)
        if os.path.islink(pixgtifile): os.unlink(pixgtifile)
        if os.path.islink(ehkfile): os.unlink(ehkfile)

        os.symlink('{0}/resolve/event_cl/{1}'.format(eventdir, eventfile), eventfile)
        os.symlink('{0}/resolve/event_uf/{1}'.format(eventdir, pixgtifile), pixgtifile)
        os.symlink('{0}/auxil/{1}'.format(eventdir, ehkfile), ehkfile)

        with open("region_RSL_det.reg", "w") as f:
            f.write("physical\n")
            f.write("+box(4,1,5,1.00000000)\n")
            f.write("+box(3.5,2,6,1.00000000)\n")
            f.write("+box(3.5,3,6,1.00000000)\n")
            f.write("+box(3.5,4,6,1.00000000)\n")
            f.write("+box(3.5,5,6,1.00000000)\n")
            f.write("+box(3.5,6,6,1.00000000)\n")

        with open("region_RSL_det_27.reg", "w") as f:
            f.write("physical\n")
            f.write("+box(4,1,5,1.00000000)\n")
            f.write("+box(3.5,2,6,1.00000000)\n")
            f.write("+box(3.5,3,6,1.00000000)\n")
            f.write("+box(3,4,5,1.00000000)\n")
            f.write("+box(3.5,5,6,1.00000000)\n")
            f.write("+box(3.5,6,6,1.00000000)\n")

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
        os.symlink('{0}/resolve/event_uf/{1}rsl_p0px5000_uf.evt.gz'.format(eventdir, obsid), '{0}rsl_p0px5000_uf.evt.gz'.format(obsid))
        outfile = '{0}rsl_p0px{1}_cl_gain.evt'.format(obsid, filter)
        mgtime_inputs = [
            'ingtis="{0}rsl_p0px5000_uf.evt.gz[2],{0}rsl_p0px5000_uf.evt.gz[6]"'.format(obsid),
            'outgti=Fe55track.gti',
            'merge=AND'
        ]

        rslgain_inputs = [
            'infile={0}rsl_p0px5000_uf.evt.gz'.format(obsid, filter),
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

    def rsl_imgextract(self, eventfile, obsid, filter, mode='DET', bmin=4000, bmax=20000):
        commands = ['']
        commands.append('xsel')
        commands.append('no')
        commands.append('read event {0}'.format(eventfile))
        commands.append('./')
        commands.append('yes')
        commands.append('set image {0}'.format(mode))
        commands.append('filter pha_cutoff {0} {1}'.format(bmin, bmax))
        commands.append('extract image')
        commands.append('save image {0}rsl_p0px{1}_detimg.fits clobber=yes'.format(obsid, filter))
        commands.append('exit')
        commands.append('no')

        process = subprocess.Popen(['xselect'], stdin=subprocess.PIPE, text=True)
        results = process.communicate('\n'.join(commands))
        process.wait()

    def rsl_specextract(self, eventfile, specfile):
        commands = []
        commands.append('xsel')
        commands.append('no')
        commands.append('read event {0}'.format(eventfile))
        commands.append('./')
        commands.append('yes')
        commands.append('filter pha_cutoff 0 59999')
        commands.append('filter column "PIXEL=0:11,13:26,28:35"')
        commands.append('filter GRADE "0:0"')
        commands.append('extract spectrum')
        commands.append('save spec {0} clobber=yes'.format(specfile))
        commands.append('exit')
        commands.append('no')

        process = subprocess.Popen(['xselect'], stdin=subprocess.PIPE, text=True)
        results = process.communicate('\n'.join(commands))
        process.wait()

    def rsl_lcextract(self, eventfile, obsid, bmin=4000, bmax=20000, binsize='128'):
        commands = []
        commands.append('xsel')
        commands.append('no')
        commands.append('read event {0}'.format(eventfile))
        commands.append('./')
        commands.append('yes')
        commands.append('set image det')
        commands.append('filter pha_cutoff {0} {1}'.format(bmin, bmax))
        commands.append('set binsize {0}'.format(binsize))
        commands.append('extr curve exposure=0.8')
        commands.append('save curve {0}rsl_allpix_b{1}_lc.fits clobber=yes'.format(obsid, binsize))
        commands.append('exit')
        commands.append('no')

        process = subprocess.Popen(['xselect'], stdin=subprocess.PIPE, text=True)
        results = process.communicate('\n'.join(commands))
        process.wait()

    def rsl_mkrmf(self, eventfile, respfile, whichrmf):
        infile = "{0}".format(eventfile)
        outroot = "{0}".format(respfile.strip('_comb.rmf'))
        inputs = [
            'infile='+infile,
            'outfileroot='+outroot,
            'regmode=DET',
            'whichrmf='+whichrmf,
            'resolist=0',
            'regionfile=NONE',
            'pixlist=0-11,13-26,28-35',
            'eminin=0.0',
            'dein=0.5',
            'nchanin=60000',
            'useingrd=no',
            'eminout=0.0',
            'deout=0.5',
            'nchanout=60000',
            'clobber=yes'
        ]
        if 'comb' in whichrmf: inputs + ['splitrmf=yes', 'elcbinfac=16', 'splitcomb=yes']
        process = subprocess.Popen(['rslmkrmf', *inputs], text=True)
        process.wait()

    def rsl_xaexpmap(self, eventfile, obsid, filter):
        inputs = [
            'ehkfile={0}.ehk.gz'.format(obsid),
            'gtifile={0}'.format(eventfile),
            'instrume=RESOLVE',
            'badimgfile=NONE',
            'pixgtifile={0}rsl_px{1}_exp.gti.gz'.format(obsid, filter),
            'outfile={0}rsl_p0px{1}.expo'.format(obsid, filter),
            'outmaptype=EXPOSURE',
            'delta=20.0',
            'numphi=1',
            'stopsys=SKY',
            'instmap=CALDB',
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
            'logfile=make_expo_{0}rsl_p0px{1}.log'.format(obsid, filter)
        ]
        process = subprocess.Popen(['xaexpmap', *inputs], text=True)
        process.wait()

    def rsl_xaarfgen(self, eventfile, respfile, ancrfile, obsid, filter, regionfile):
        RA_NOM, DEC_NOM, PA_NOM = self.get_radec_nom(eventfile)
        ra, dec = self.rsl_coordpnt(RA_NOM, DEC_NOM, PA_NOM, X0=3.5, Y0=3.5)
        inputs = [
            'xrtevtfile=raytrace_{0}rsl_p0px{1}_ptsrc.fits'.format(obsid, filter),
            'source_ra={0}'.format(ra),
            'source_dec={0}'.format(dec),
            'telescop=XRISM',
            'instrume=RESOLVE',
            'emapfile={0}rsl_p0px{1}.expo'.format(obsid, filter),
            'regmode=DET',
            'regionfile={0}'.format(regionfile),
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
            'gatevalvefile=CALDB',
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
        self.rsl_mkrmf(eventfile, respfile, whichrmf)
        self.rsl_xaexpmap(eventfile, obsid, filter)
        self.rsl_xaarfgen(eventfile, respfile, ancrfile, obsid, filter, regionfile)
        self.ftgrouppha(specfile, outfile, backfile, respfile, grouptype, groupscale)
        self.bgd_rmf_arf(outfile, backfile, respfile, ancrfile)

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
        self.rsl_mkrmf(eventfile, respfile, obsid, whichrmf)
        self.rsl_xaexpmap(eventfile, obsid, filter)
        self.rsl_xaarfgen(eventfile, respfile, ancrfile, obsid, filter, regionfile)
        self.ftgrouppha(specfile, outfile, backfile, respfile, grouptype, groupscale)
        self.bgd_rmf_arf(outfile, backfile, respfile, ancrfile)


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
        self.rsl_mkrmf(eventfile, respfile, obsid, whichrmf)
        self.rsl_xaexpmap(eventfile, obsid, filter)
        self.rsl_xaarfgen(eventfile, respfile, ancrfile, obsid, filter, regionfile)
        self.ftgrouppha(specfile, outfile, backfile, respfile, grouptype, groupscale)
        self.bgd_rmf_arf(outfile, backfile, respfile, ancrfile)

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
        self.rsl_mkrmf(eventfile, respfile, obsid, whichrmf)
        self.rsl_xaexpmap(eventfile, obsid, filter)
        self.rsl_xaarfgen(eventfile, respfile, ancrfile, obsid, filter, regionfile)
        self.ftgrouppha(specfile, outfile, backfile, respfile, grouptype, groupscale)
        self.bgd_rmf_arf(outfile, backfile, respfile, ancrfile)