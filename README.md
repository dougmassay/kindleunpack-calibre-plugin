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

You can also add a '-d (or --debug) option to setup.py. If calibre is installed and on your
path and you add the '-d' option, setup.py will attempt to:

    1) close calibre if it's open
    2) install the plugin using calibre-customize
    3) relaunch calibre in debug-mode

    $ python setup.py -d

If all goes well, the plugin can now be run and any debug print statements/errors should print
to the terminal. If you have a complex calibre setup (or it's not on you path), you may need to
install the plugin manually to debug.

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

It's important to note that any import statements in the above files that look like:
   
    from calibre_plugins.kindleunpack_plugin.kindleunpack.blah import blah

are actually referring to a 'blah' module / script in the core_subtree/lib directory.
These imports will only "work" in the context of a calibre plugin's structure and the calibre
environment. If you need to refer to or call those modules that's where they'll be. 
But as mentioned above ... go upstream if you have patches or pull requests for those files.

For example, if you need to import something from the core_subtree/lib/compatibility_utils.py
script, you would use:

    from calibre_plugins.kindleunpack_plugin.kindleunpack.compatibility_utils import mobi_split


Files used for building/maintaining the plugin:

    > setup.py  -- this is used to configure/build the plugin.
    > setup.cfg -- used for flake8 style checking. Use it to see if your code complies.
    > pythonpatch.py  -- used by setup.py to apply patches to upstream files if necessary. 
    > ku.patch  -- patch that setup.py will apply to a temp copy of the upstream kindleunpack.py file.
    > compat_utils.patch  -- patch for the upstream compatibilities.py file.



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
    Available under the terms of the MIT license (http://opensource.org/licenses/mit-license.php)



