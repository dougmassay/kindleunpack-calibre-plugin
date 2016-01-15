KindleUnpack the calibre Plugin
============

Open KindleBooks in Sigil

A calibre plugin based/wrapped around the KindleUnpack software. 
(python based software to unpack Amazon / Kindlegen generated ebooks)

Links
=====

* calibre website is at http://calibre-ebook.com
* The KindleUnpack python-based software can be found at https://github.com/kevinhendricks/KindleUnpack
* python-patch (used to help build the plugin) can be found at https://github.com/techtonik/python-patch

Building
========

First, clone the repo:

    $ git clone https://github.com/dougmassay/kindleunpack-calibre-plugin.git

Then you need to prepare the source by downloading some core files from the KindleUnpack project. I'm not going to track those files here since they're already maintained in another Git repository. There's a script in the 'setup_tools' folder that will download/patch what you need. Just cd into the 'setup_tools' folder and run the getkucore.py script with Python 2.7+ or 3.4+ (don't try to run the script from outside the 'setup_tools' folder).

    $ cd ./kindleunpack-calibre-plugin/setup_tools
    $ python getkucore.py
    $ cd ..
    
This will create a kindleunpackcore folder. You only need to prepare this folder once -- unless KindleUnpack is updated and you want to use the latest. In that case, just repeat those last 3 steps whenever you want to update the kindleunpackcore files. It will delete the folder and recreate it as necessary.

To create the plugin zip file, run the setup.py script (root of the repository tree) with Python

    $python setup.py

You can also add a -d (or --debug) option to setup.py. If calibre is installed and on your
path and you add the '-d' option, setup.py will attempt to:

    1) close calibre if it's open
    2) install the plugin using calibre-customize
    3) relaunch calibre in debug-mode
    
If all goes well, the plugin can now be run and any debug print statements/errors should print
to the terminal. If you have a complex calibre setup (or it's not on you path), you may need to
install the plugin manually to debug.

** Note if you're not using the debug option with setup.py, you can use Python2 or Python3 to build the plugin. But if if you're using the -d option to install the plugin and launch calibre, you must use Python2.


Contributing / Modifying
============
From here on out, a proficiency with developing / creating calibre plugins is assumed.
If you need a crash-course, an introduction to creating calibre plugins is available at
http://manual.calibre-ebook.com/creating_plugins.html.

Any changes to files in the kindleunpackcore folder will be ignored. The repository is setup to ignore this folder (meaning git won't track changes to them). If you have modifications to suggest for those files, do so upstream at https://github.com/kevinhendricks/KindleUnpack.

Any changes there can be pulled into this repository by running the getkucore.py script in the 'setup_tools' folder at any time.

The core plugin files (this is where most contributors will spend their time) are:

    > images/explode3.png
    > __init__.py
    > action.py
    > plugin-import-name-kindleunpack_plugin.txt 
    > config.py                                 
    > dialogs.py
    > mobi_stuff.py
    > utilities.py

It's important to note that any import statements in the above files that look like:
   
    from calibre_plugins.kindleunpack_plugin.kindleunpackcore.blah import blah

are actually referring to a 'blah' module / script in the kindleunpackcore directory.
These imports will only "work" in the context of a calibre plugin's structure and the calibre
environment. If you need to refer to or call those modules that's where they'll be. 
But as mentioned above ... go upstream if you have patches or pull requests for those files.

For example, if you need to import something from the kindleunpackcore/ directory (for example: 
compatibility_utils.py), you would use:

    from calibre_plugins.kindleunpack_plugin.kindleunpackcore.compatibility_utils import PY2

The rest of the scripts above (dialogs.py, etc...) can be imported using the prefix of:

    calibre_plugins.kindleunpack_plugin.



Files used for building/maintaining the plugin:

    > setup.py  -- this is used to build the plugin.
    > setup.cfg -- used for flake8 style checking. Use it to see if your code complies.
    > setup_tools/pythonpatch.py  -- used by setup.py to apply patches to upstream files if necessary. 
    > setup_tools/kindleunpack.patch  -- patch that will be applied to kindleunpackcore/kindleunpack.py
    > setup_tools/mobi_nav.patch  -- patch that will be applied to kindleunpackcore/mobi_nav.py


License Information
=======

###KindleUnpack the Calibre Plugin

    Licensed under the GPLv3.

###KindleUnpack (https://github.com/kevinhendricks/KindleUnpack)

    Based on initial mobipocket version Copyright © 2009 Charles M. Hannum <root@ihack.net>
    Extensive Extensions and Improvements Copyright © 2009-2014 
    By P. Durrant, K. Hendricks, S. Siebert, fandrieu, DiapDealer, nickredding, tkeo.
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, version 3.

###python-patch (https://github.com/techtonik/python-patch)

    Copyright © 2008-2015 anatoly techtonik
    Available under the terms of the MIT license (http://opensource.org/licenses/mit-license.php)

    Copyright (c) 2008-2015 anatoly techtonik

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights    
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    THE SOFTWARE.

