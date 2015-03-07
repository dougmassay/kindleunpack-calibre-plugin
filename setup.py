#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

import os
import re
import shutil
import inspect
import patch
import zipfile


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

# Remove kindleunpack folder an contents if it exists
if os.path.exists(KU_DIR) and os.path.isdir(KU_DIR):
    shutil.rmtree(KU_DIR)

# Remove existing plugin zipfile if it exists
if os.path.exists(PLUGIN_NAME):
    os.remove(PLUGIN_NAME)

# Copy lib directory from KindleUnpack repo as 'kindleunpack' (temporarily)
shutil.copytree(CORE_LIB_DIR, KU_DIR)

# Patch kindleunpack.py
parsedPatchSet = patch.fromfile('ku.patch')
if parsedPatchSet is not False:
    if parsedPatchSet.apply():
        print(parsedPatchSet.diffstat())
    else:
        print ('Cannot patch necessary file!')
else:
    print ('Cannot patch necessary file!')

files = os.listdir(SCRIPT_DIR)
outzip = zipfile.ZipFile(PLUGIN_NAME, 'w')
for entry in files:
    filepath = os.path.join(SCRIPT_DIR, entry)
    if os.path.isfile(filepath) and entry in PLUGIN_FILES:
        outzip.write(filepath, entry ,zipfile.ZIP_DEFLATED)
    elif os.path.isdir(filepath) and entry in PLUGIN_DIRS:
        zipUpDir(outzip, SCRIPT_DIR, entry)
outzip.close()

# Remove kindleunpack folder an contents if it exists
if os.path.exists(KU_DIR) and os.path.isdir(KU_DIR):
    shutil.rmtree(KU_DIR)
