#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

import os
import sys
import re
import glob
import shutil
import inspect
import pythonpatch
import zipfile
from subprocess import Popen, PIPE, STDOUT

SCRIPT_DIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
KU_DIR = os.path.join(SCRIPT_DIR, 'kindleunpack')
CORE_LIB_DIR = os.path.join(SCRIPT_DIR, 'core_subtree', 'lib')

PLUGIN_DIRS = ['images', 'kindleunpack']

PLUGIN_FILES = ['__init__.py',
            'action.py',
            'config.py',
            'dialogs.py',
            'mobi_stuff.py',
            'plugin-import-name-kindleunpack_plugin.txt',
            'utilities.py'
]

def findVersion():
    pattern = r'PLUGIN_VERSION_TUPLE = \((\d+),\s?(\d+),\s?(\d+)\)'
    with open('__init__.py', 'r') as fd:
        data = fd.read()
    match = re.search(pattern, data)
    if match is not None:
        return '{}{}{}'.format(match.group(1), match.group(2), match.group(3))
    return '0XXX'

# Find version info from __init__.py and build zip file name from it
VERS_INFO =  findVersion()
PLUGIN_NAME = os.path.join(SCRIPT_DIR, 'kindle_unpack_v{}_plugin.zip'.format(VERS_INFO))


def calibreWrapper(*cmd):
    process = Popen(list(cmd), stdout=PIPE, stderr=STDOUT)

    # Poll process for new output until finished
    while True:
        nextline = process.stdout.readline()
        if nextline == '' and process.poll() is not None:
            break
        sys.stdout.write(nextline)
        sys.stdout.flush()

    output = process.communicate()[0]
    exitCode = process.returncode

    if (exitCode == 0):
        return output
    else:
        pass

# recursive zip creation support routine
def zipUpDir(myzip, tdir, localname):
    currentdir = tdir
    if localname != "":
        currentdir = os.path.join(currentdir,localname)
    dir_contents = os.listdir(currentdir)
    for entry in dir_contents:
        afilename = entry
        localfilePath = os.path.join(localname, afilename)
        realfilePath = os.path.join(currentdir, entry)
        if os.path.isfile(realfilePath):
            myzip.write(realfilePath, localfilePath, zipfile.ZIP_DEFLATED)
        elif os.path.isdir(realfilePath):
            zipUpDir(myzip, tdir, localfilePath)

def removePreviousKU(rmzip=False):
    # Remove kindleunpack folder an contents if it exists
    if os.path.exists(KU_DIR) and os.path.isdir(KU_DIR):
        shutil.rmtree(KU_DIR)

    if rmzip:
        print ('Removing any leftover zip files ...')
        for each in glob.glob('kindle_unpack_v*_plugin.zip'):
            path = os.path.join(SCRIPT_DIR, each)
            if os.path.exists(path):
                os.remove(path)


if __name__ == "__main__":
    from optparse import OptionParser

    opt = OptionParser(usage='python %prog [options]')
    opt.add_option('-d', '--debug', action='store_true', dest='debugmode', help='Install/debug plugin using calibre')
    (options, args) = opt.parse_args()
    
    print('Removing any previous build leftovers ...')
    removePreviousKU(rmzip=True)

    # Copy lib directory from KindleUnpack repo as 'kindleunpack' (temporarily)
    print ('Copying upstream \'lib\' directory to temporary \'kindleunpack\' ...')
    try:
        shutil.copytree(CORE_LIB_DIR, KU_DIR)
    except:
        sys.exit('Couldn\'t copy necessary core_subtree/lib directory!')

    # Patch kindleunpack.py
    print ('Attempting to patch upstream file(s) ...')
    patchfiles = glob.glob('*.patch')
    for patch in patchfiles:
        parsedPatchSet = pythonpatch.fromfile(patch)
        if parsedPatchSet is not False:
            if parsedPatchSet.apply():
                print(parsedPatchSet.diffstat())
            else:
                sys.exit('Cannot patch upstream file(s)!')
        else:
            sys.exit('Cannot patch upstream file(s)!')

    print ('Creating {} ...'.format(os.path.basename(PLUGIN_NAME)))
    files = os.listdir(SCRIPT_DIR)
    outzip = zipfile.ZipFile(PLUGIN_NAME, 'w')
    for entry in files:
        filepath = os.path.join(SCRIPT_DIR, entry)
        if os.path.isfile(filepath) and entry in PLUGIN_FILES:
            outzip.write(filepath, entry ,zipfile.ZIP_DEFLATED)
        elif os.path.isdir(filepath) and entry in PLUGIN_DIRS:
            zipUpDir(outzip, SCRIPT_DIR, entry)
    outzip.close()
    
    print ('Plugin successfully created!')

    print('Removing temporary \'kindleunpack\' directory ...')
    removePreviousKU()

    if options.debugmode:
        print('\nAttempting to install plugin and launch calibre ...')
        print('If successful, debug output should print to terminal.')
        args= ['calibre-debug', '-s']
        result = calibreWrapper(*args)
        args= ['calibre-customize', '-a', PLUGIN_NAME]
        result = calibreWrapper(*args)
        args= ['calibre-debug', '-g']
        result = calibreWrapper(*args)
