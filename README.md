KindleUnpack the calibre Plugin
============

A calibre plugin based/wrapped around the KindleUnpack software. 
(python based software to unpack Amazon / Kindlegen generated ebooks)

Links
=====

* calibre website is at http://calibre-ebook.com
* The KindleUnpack python-based software can be found at https://github.com/kevinhendricks/KindleUnpack
* python-patch (used to help build the plugin) can be found at http://code.google.com/p/python-patch/

Building
========

To build the plugin, clone the repo, cd into it and run the setup.py script with python (2.x-only for now):

    $ git clone https://github.com/dougmassay/kindleunpack-calibre-plugin
    $ cd ./kindleunpack-calibre-plugin
    $ python setup.py

This will create the plugin's zip file by copying/patching the files it needs to function.
At this point, the plugin can be installed using calibre's standard preferences/plugin interface.

Contributing / Modifying
============
From here on out, a proficiency with developing / creating calibre plugins is assumed.
If you need a crash-course, an introduction to creating calibre plugins is available at
http://manual.calibre-ebook.com/creating_plugins.html.


The core_subtree/ directory is a subtree representing the entire python2and3 branch of KindleUnpack -- the
python software the plugin is based upon. No pull-requests or patches will be accepted for any of
its contents. If you have modifications to suggest for those files, do so upstream at https://github.com/kevinhendricks/KindleUnpack.
Any changes there will eventually be pulled into this repository.

The core plugin files (this is where most contributors will spend their time):

    > images/explode3.png
    > __init__.py
    > action.py
    > plugin-import-name-kindleunpack_plugin.txt 
    > config.py                                 
    > dialogs.py
    > mobi_stuff.py
    > utilities.py

Files used for building/maintaining the plugin:

    > setup.py  -- this is used to configure/build the plugin.
    > setup.cfg -- used for flake8 style checking. Use it to see if your code complies.
    > patch.py  -- used by setup.py to apply patches to upstream files if necessary. 
    > ku.patch  -- patch that setup.py will apply to a temp copy of the upstream kindleunpack.py file.



License Information
=======

KindleUnpack the Calibre Plugin

    Licensed under the GPLv3.

KindleUnpack (https://github.com/kevinhendricks/KindleUnpack)

    Based on initial mobipocket version Copyright © 2009 Charles M. Hannum <root@ihack.net>
    Extensive Extensions and Improvements Copyright © 2009-2014 
    By P. Durrant, K. Hendricks, S. Siebert, fandrieu, DiapDealer, nickredding, tkeo.
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, version 3.

python-patch (https://code.google.com/p/python-patch/)

    Copyright © 2008-2012 anatoly techtonik
    Available under the terms of [MIT license](http://opensource.org/licenses/mit-license.php)



