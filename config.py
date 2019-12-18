# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__docformat__ = 'restructuredtext en'

import os, sys

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3
if PY3:
    text_type = str
    binary_type = bytes
else:
    range = xrange
    text_type = unicode
    binary_type = str

try:
    from PyQt5.Qt import (QWidget, QLabel, QLineEdit, QPushButton, QCheckBox,
                            QGroupBox, QVBoxLayout, QComboBox)
except ImportError:
    from PyQt4.Qt import (QWidget, QLabel, QLineEdit, QPushButton, QCheckBox,
                            QGroupBox, QVBoxLayout, QComboBox)

from calibre.utils.config import JSONConfig
from calibre.utils.filenames import expanduser
from calibre.gui2 import choose_dir, error_dialog

from calibre_plugins.kindleunpack_plugin.__init__ import PLUGIN_NAME, PLUGIN_VERSION

PLUGIN_ICONS = ['images/explode3.png', 'images/acrobat.png']

# This is where all preferences for this plugin will be stored.
plugin_prefs = JSONConfig('plugins/KindleUnpack_prefs')

# Set default preferences
plugin_prefs.defaults['Unpack_Folder'] = expanduser('~')
plugin_prefs.defaults['Always_Use_Unpack_Folder'] = False
plugin_prefs.defaults['Use_HD_Images'] = False
plugin_prefs.defaults['Epub_Version'] = '2'

class ConfigWidget(QWidget):

    def __init__(self, plugin_action):
        QWidget.__init__(self)
        self.plugin_action = plugin_action
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        # --- Directory Options ---
        directory_group_box = QGroupBox(_('Default Unpack Directory:'), self)
        layout.addWidget(directory_group_box)
        directory_group_box_layout = QVBoxLayout()
        directory_group_box.setLayout(directory_group_box_layout)

        # Directory path Textbox
        # Load the textbox with the current preference setting
        self.directory_txtBox = QLineEdit(plugin_prefs['Unpack_Folder'], self)
        self.directory_txtBox.setToolTip(_('<p>Default directory to extract files to'))
        directory_group_box_layout.addWidget(self.directory_txtBox)
        self.directory_txtBox.setReadOnly(True)

        # Folder select button
        directory_button = QPushButton(_('Select/Change Unpack Directory'), self)
        directory_button.setToolTip(_('<p>Select/Change directory to extract files to.'))
        # Connect button to the getDirectory function
        directory_button.clicked.connect(self.getDirectory)
        directory_group_box_layout.addWidget(directory_button)
        self.default_folder_check = QCheckBox(_('Always use the Default Unpack Directory'), self)
        self.default_folder_check.setToolTip(_('<p>When unchecked... you will be prompted to select a destination '+
                                                                                'directory for the extracted content each time you use Mobiunpack.'))
        directory_group_box_layout.addWidget(self.default_folder_check)
        # Load the checkbox with the current preference setting
        self.default_folder_check.setChecked(plugin_prefs['Always_Use_Unpack_Folder'])

        misc_group_box = QGroupBox(_('Default settings:'), self)
        layout.addWidget(misc_group_box)
        misc_group_box_layout = QVBoxLayout()
        misc_group_box.setLayout(misc_group_box_layout)

        self.use_hd_images = QCheckBox(_('Always use HD images if present'), self)
        self.use_hd_images.setToolTip(_('<p>When checked... any HD images present in the kindlebook '+
                                                                                'will be used for creating the ePub.'))
        misc_group_box_layout.addWidget(self.use_hd_images)
        # Load the checkbox with the current preference setting
        self.use_hd_images.setChecked(plugin_prefs['Use_HD_Images'])

        combo_label = QLabel('Select epub version output:', self)
        misc_group_box_layout.addWidget(combo_label)
        self.epub_version_combobox = QComboBox()
        self.epub_version_combobox.setToolTip(_('<p>Select the type of OPF file to create.'))
        misc_group_box_layout.addWidget(self.epub_version_combobox)
        self.epub_version_combobox.addItems(['Auto-detect', 'ePub2', 'ePub3'])
        if plugin_prefs['Epub_Version'] == 'A':
            self.epub_version_combobox.setCurrentIndex(0)
        else:
            self.epub_version_combobox.setCurrentIndex(int(plugin_prefs['Epub_Version'])-1)

    def save_settings(self):
        # Save current dialog sttings back to JSON config file
            plugin_prefs['Unpack_Folder'] = text_type(self.directory_txtBox.displayText())
            plugin_prefs['Always_Use_Unpack_Folder'] = self.default_folder_check.isChecked()
            plugin_prefs['Use_HD_Images'] = self.use_hd_images.isChecked()
            if text_type(self.epub_version_combobox.currentText()) == 'Auto-detect':
                plugin_prefs['Epub_Version'] = 'A'
            else:
                plugin_prefs['Epub_Version'] = text_type(self.epub_version_combobox.currentText())[4:]

    def getDirectory(self):
        c = choose_dir(self, _(PLUGIN_NAME + 'dir_chooser'),
                _('Select Default Directory To Unpack Kindle Book/Mobi To'))
        if c:
            self.directory_txtBox.setReadOnly(False)
            self.directory_txtBox.setText(c)
            self.directory_txtBox.setReadOnly(True)

    def validate(self):
        # This is just to catch the situation where somone might
        # manually enter a non-existent path in the Default path textbox.
        # Shouldn't be possible at this point.
        if not os.path.exists(self.directory_txtBox.text()):
            errmsg = '<p>The path specified for the Default Unpack folder does not exist.</p>' \
                        '<p>Your latest preference changes will <b>NOT</b> be saved!</p>' + \
                        '<p>You should configure again and make sure your settings are correct.'
            error_dialog(None, _(PLUGIN_NAME + ' v' + PLUGIN_VERSION),
                                    _(errmsg), show=True)
            return False
        return True
