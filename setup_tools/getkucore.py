#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab

from __future__ import unicode_literals, division, absolute_import, print_function

import os
import sys
import shutil
import inspect
import glob
import zipfile
import pythonpatch

if sys.version_info >= (3,):
    import urllib
else:
    import urllib2

SCRIPT_DIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
SOURCE_DIR = os.path.dirname(SCRIPT_DIR)
COMMIT_SHA = 'f90cd5d2a9ee49094c4d99b732ad214c9ee2fc7e'
# REMOTE_URL = 'https://github.com/kevinhendricks/KindleUnpack/archive/master.zip'
REMOTE_URL = 'https://github.com/kevinhendricks/KindleUnpack/archive/{}.zip'.format(COMMIT_SHA)
# FILE_NAME = os.path.join(SCRIPT_DIR, REMOTE_URL.split('/')[-1])
FILE_NAME = os.path.join(SCRIPT_DIR, 'KindleUnpack-{}'.format(REMOTE_URL.split('/')[-1]))
# CORE_DIR = 'KindleUnpack-master/lib/'
CORE_DIR = 'KindleUnpack-{}/lib'.format(COMMIT_SHA)
CORE_EXCLUDES = ['askfolder_ed.py', 'mobiml2xhtml.py', 'prefs.py', 'scrolltextwidget.py']
TARGET_DIR = os.path.join(SOURCE_DIR, 'kindleunpackcore')

def retrieveKindleUnpack():
    if os.path.exists(FILE_NAME) and os.path.isfile(FILE_NAME):
        os.remove(FILE_NAME)
    if sys.version_info >= (3,):
        def reporthook(blocknum, blocksize, totalsize):
            readsofar = blocknum * blocksize
            if totalsize > 0:
                percent = readsofar * 1e2 / totalsize
                s = "\r%5.1f%% %*d / %d" % (
                    percent, len(str(totalsize)), readsofar, totalsize)
                sys.stderr.write(s)
                if readsofar >= totalsize:  # near the end
                    sys.stderr.write("\n")
            else:  # total size is unknown
                sys.stderr.write("read %d\n" % (readsofar,))
        urllib.request.urlretrieve(REMOTE_URL, FILE_NAME, reporthook)
    else:
        u = urllib2.urlopen(REMOTE_URL)
        meta = u.info()
        file_size = int(meta.getheaders("Content-Length")[0])
        with open(FILE_NAME, 'wb') as f:
            print('Downloading: %s Bytes: %s' % (FILE_NAME, file_size))
            file_size_dl = 0
            block_sz = 8192
            while True:
                buffer = u.read(block_sz)
                if not buffer:
                    break
                file_size_dl += len(buffer)
                f.write(buffer)
                status = r'%10d  [%3.2f%%]' % (file_size_dl, file_size_dl * 100. / file_size)
                status = status + chr(8)*(len(status)+1)
                print(status),


retrieveKindleUnpack()

if os.path.exists(TARGET_DIR) and os.path.isdir(TARGET_DIR):
    shutil.rmtree(TARGET_DIR)
os.mkdir(TARGET_DIR)

with zipfile.ZipFile(FILE_NAME) as zip_file:
    for member in zip_file.namelist():
        if member.startswith(CORE_DIR):
            name = os.path.basename(member)
            if not name or name in CORE_EXCLUDES:
                continue
            source = zip_file.open(member)
            target = open(os.path.join(TARGET_DIR, name), "wb")
            with source, target:
                shutil.copyfileobj(source, target)

# Patch kindleunpack.py, mobi_nav.py
print('Attempting to patch KindleUnpack file(s) ...')
patchfiles = glob.glob('*.patch')
for patch in patchfiles:
    parsedPatchSet = pythonpatch.fromfile(patch)
    if parsedPatchSet is not False:
        if parsedPatchSet.apply():
            print(parsedPatchSet.diffstat())
        else:
            os.chdir('..')
            sys.exit('Cannot apply patch to KindleUnpack file(s)!')
    else:
        os.chdir('..')
        sys.exit('Cannot parse patch file(s)!')

if os.path.exists(FILE_NAME) and os.path.isfile(FILE_NAME):
    os.remove(FILE_NAME)
