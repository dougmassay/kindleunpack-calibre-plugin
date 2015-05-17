# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__docformat__ = 'restructuredtext en'

import os
import struct
import re

import calibre_plugins.kindleunpack_plugin.config as cfg
import calibre_plugins.kindleunpack_plugin.kindleunpack.kindleunpack as _mu
from calibre_plugins.kindleunpack_plugin.kindleunpack.compatibility_utils import PY2, bstr, unicode_str
from calibre_plugins.kindleunpack_plugin.kindleunpack.mobi_split import mobi_split


if PY2:
    range = xrange

class SectionizerLight:
    """ Stolen from Mobi_Unpack and slightly modified. """
    def __init__(self, filename):
        self.data = open(filename, 'rb').read()
        if self.data[:3] == b'TPZ':
            self.ident = 'TPZ'
        else:
            self.palmheader = self.data[:78]
            self.ident = self.palmheader[0x3C:0x3C+8]
        try:
            self.num_sections, = struct.unpack_from(b'>H', self.palmheader, 76)
        except:
            return
        self.filelength = len(self.data)
        try:
            sectionsdata = struct.unpack_from(bstr('>%dL' % (self.num_sections*2)), self.data, 78) + (self.filelength, 0)
            self.sectionoffsets = sectionsdata[::2]
        except:
            pass

    def loadSection(self, section):
        before, after = self.sectionoffsets[section:section+2]
        return self.data[before:after]

class MobiHeaderLight:
    """ Stolen from Mobi_Unpack and slightly modified. """
    def __init__(self, sect, sectNumber):
        self.sect = sect
        self.start = sectNumber
        self.header = self.sect.loadSection(self.start)
        self.records, = struct.unpack_from(b'>H', self.header, 0x8)
        self.length, self.type, self.codepage, self.unique_id, self.version = struct.unpack(b'>LLLLL', self.header[20:40])
        self.mlstart = self.sect.loadSection(self.start+1)[0:4]
        self.crypto_type, = struct.unpack_from(b'>H', self.header, 0xC)

    def isEncrypted(self):
        return self.crypto_type != 0

    def isPrintReplica(self):
        return self.mlstart[0:4] == b'%MOP'

    # Standalone KF8 file
    def isKF8(self):
        return self.start != 0 or self.version == 8

    def isJointFile(self):
        # Check for joint MOBI/KF8
        for i in range(len(self.sect.sectionoffsets)-1):
            before, after = self.sect.sectionoffsets[i:i+2]
            if (after - before) == 8:
                data = self.sect.loadSection(i)
                if data == b'BOUNDARY':
                    return True
                    break
        return False


def makeFileNames(prefix, infile, outdir, kf8=False):
    if kf8:
        return os.path.join(outdir, prefix+os.path.splitext(os.path.basename(infile))[0] + '.azw3')
    return os.path.join(outdir, prefix+os.path.splitext(os.path.basename(infile))[0] + '.mobi')

class mobiProcessor:
    def __init__(self, infile):
        self.infile = infile
        self.sect = SectionizerLight(self.infile)
        if (self.sect.ident != b'BOOKMOBI' and self.sect.ident != b'TEXtREAd') or self.sect.ident == 'TPZ':
            raise Exception(_('Unrecognized Kindle/MOBI file format!'))
        mhl = MobiHeaderLight(self.sect, 0)
        self.version = mhl.version
        self.isEncrypted = mhl.isEncrypted()
        if self.sect.ident == b'TEXtREAd':
            self.isPrintReplica = False
            self.isComboFile = False
            self.isKF8 = False
            return
        self.isPrintReplica = mhl.isPrintReplica()
        self.isKF8 = mhl.isKF8()
        self.isComboFile = mhl.isJointFile()

        self.ePubVersion = cfg.plugin_prefs['Epub_Version']
        self.useHDImages = cfg.plugin_prefs['Use_HD_Images']

    def getPDFFile(self, outdir):
        _mu.unpackBook(self.infile, outdir)
        files = os.listdir(outdir)
        pdf = ''
        filefilter = re.compile('\.pdf$', re.IGNORECASE)
        files = filter(filefilter.search, files)
        if files:
            for filename in files:
                pdf = os.path.join(outdir, filename)
                break
        else:
            raise Exception(_('Problem locating unpacked pdf.'))
        if pdf=='':
            raise Exception(_('Problem locating unpacked pdf.'))
        if not os.path.exists(pdf):
            raise Exception(_('Problem locating unpacked pdf: {0}'.format(pdf)))
        return pdf

    def unpackMOBI(self, outdir):
        _mu.unpackBook(self.infile, outdir, epubver=self.ePubVersion, use_hd=self.useHDImages)

    def unpackEPUB(self, outdir):
        _mu.unpackBook(self.infile, outdir, epubver=self.ePubVersion, use_hd=self.useHDImages)
        kf8dir = os.path.join(outdir, 'mobi8')
        kf8BaseName = os.path.splitext(os.path.basename(self.infile))[0]
        epub = os.path.join(kf8dir, '{0}.epub'.format(kf8BaseName))
        if not os.path.exists(epub):
            raise Exception(_('Problem locating unpacked epub: {0}'.format(epub)))
        return epub

    def writeSplitCombo(self, outdir):
        mobi_to_split = mobi_split(unicode_str(self.infile))
        outMobi = makeFileNames('MOBI-', self.infile, outdir)
        outKF8 = makeFileNames('KF8-', self.infile, outdir, True)
        file(outMobi, 'wb').write(mobi_to_split.getResult7())
        file(outKF8, 'wb').write(mobi_to_split.getResult8())
