# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__docformat__ = 'restructuredtext en'

#####################################################################
# Plug-in base class
#####################################################################

from calibre.customize import InterfaceActionBase

PLUGIN_NAME = 'KindleUnpack - The Plugin'
PLUGIN_DESCRIPTION = '\nUnpacks a Kindle Book/MOBI into its source components.'
PLUGIN_VERSION_TUPLE = (0, 81, 0)
PLUGIN_VERSION = '.'.join([str(x) for x in PLUGIN_VERSION_TUPLE])
PLUGIN_AUTHORS = \
"""DiapDealer.
Original mobiunpack.py, Copyright © 2009 Charles M. Hannum <root@ihack.net>.
Extensions / Improvements Copyright © 2009-2012 P. Durrant, K. Hendricks, S. Siebert, fandrieu, DiapDealer, nickredding, tkeo.\n"""

#####################################################################

class ExtractMobiAction(InterfaceActionBase):

    name                    = PLUGIN_NAME
    description             = PLUGIN_DESCRIPTION
    supported_platforms     = ['windows', 'osx', 'linux']
    author                  = PLUGIN_AUTHORS
    version                 = PLUGIN_VERSION_TUPLE
    minimum_calibre_version = (0, 8, 18)

    #: This field defines the GUI plugin class that contains all the code
    #: that actually does something. Its format is module_path:class_name
    #: The specified class must be defined in the specified module.
    actual_plugin           = 'calibre_plugins.kindleunpack_plugin.action:InterfacePlugin'

    def is_customizable(self):
        '''
        This method must return True to enable customization via
        Preferences->Plugins
        '''
        return True

    def config_widget(self):
        '''
        Implement this method and :meth:`save_settings` in your plugin to
        use a custom configuration dialog.

        This method, if implemented, must return a QWidget. The widget can have
        an optional method validate() that takes no arguments and is called
        immediately after the user clicks OK. Changes are applied if and only
        if the method returns True.

        If for some reason you cannot perform the configuration at this time,
        return a tuple of two strings (message, details), these will be
        displayed as a warning dialog to the user and the process will be
        aborted.

        The base class implementation of this method raises NotImplementedError
        so by default no user configuration is possible.
        '''
        if self.actual_plugin_:
            from calibre_plugins.kindleunpack_plugin.config import ConfigWidget
            return ConfigWidget(self.actual_plugin_)

    def save_settings(self, config_widget):
        '''
        Save the settings specified by the user with config_widget.

        :param config_widget: The widget returned by :meth:`config_widget`.
        '''
        config_widget.save_settings()
