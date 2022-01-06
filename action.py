# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__docformat__ = 'restructuredtext en'

import os

from functools import partial

try:
    from qt.core import QMenu, QToolButton
except ImportError:
    try:
        from PyQt5.Qt import QMenu, QToolButton
    except ImportError:
        from PyQt4.Qt import QMenu, QToolButton

from calibre.gui2 import choose_dir, info_dialog, open_local_file
from calibre.gui2.actions import InterfaceAction

from calibre.ptempfile import PersistentTemporaryDirectory
from calibre_plugins.kindleunpack_plugin.__init__ import (PLUGIN_NAME,
                                PLUGIN_VERSION, PLUGIN_DESCRIPTION)
import calibre_plugins.kindleunpack_plugin.config as cfg
from calibre_plugins.kindleunpack_plugin.dialogs import ProgressDialog, ResultsSummaryDialog
# from calibre_plugins.kindleunpack_plugin.mobi_stuff import mobiProcessor
from calibre_plugins.kindleunpack_plugin.utilities import (get_icon, KindleFormats, set_plugin_icon_resources,
                                showErrorDlg, create_menu_item, create_menu_action_unique, build_log)


class InterfacePlugin(InterfaceAction):
    name = 'KindleUnpack'
    action_spec = ('KindleUnpack', None,
            _(PLUGIN_DESCRIPTION), None)
    popup_type = QToolButton.InstantPopup
    # dont_add_to = frozenset(['menubar-device', 'toolbar-device', 'context-menu-device'])
    dont_add_to = frozenset(['context-menu-device'])
    action_type = 'current'

    def genesis(self):
        self.menu = QMenu(self.gui)
        icon_resources = self.load_resources(cfg.PLUGIN_ICONS)
        set_plugin_icon_resources(cfg.PLUGIN_NAME, icon_resources)

        self.qaction.setMenu(self.menu)
        self.qaction.setIcon(get_icon(cfg.PLUGIN_ICONS[0]))
        # Setup hooks so that we only enable the relevant submenus for available formats for the selection.
        self.menu.aboutToShow.connect(self.about_to_show_menu)

    def about_to_show_menu(self):
        book_ids = self.gui.library_view.get_selected_ids()
        if len(book_ids) > 1:
            self.build_multiple_book_menus(book_ids)
        elif len(book_ids):
            self.build_single_book_menus(book_ids[0])

    def build_multiple_book_menus(self, book_ids):
        '''
        If multiple books are selected, the only choices are to
        extract PDFs from AZW4 formats and EPUBs from AZW3 format.
        '''
        m = self.menu
        m.clear()

        tool_tip = 'Convert the KF8 portions of the selected AZW3s to ePubs and add them to their respective books.'
        create_menu_action_unique(self, m, _('KF8 to ePubs')+'...', 'mimetypes/epub.png', _(tool_tip),
                                                 False, triggered=partial(self.multi_dispatcher, book_ids, u'AZW3'))

        tool_tip = 'Extract the PDFs from the AZW4 formats and add them to their respective books.'
        create_menu_action_unique(self, m, _('Extract PDFs')+'...', 'mimetypes/pdf.png', _(tool_tip),
                                                 False, triggered=partial(self.multi_dispatcher, book_ids, u'AZW4'))

        m.addSeparator()
        tool_tip = 'Configure the KindleUnpack plugin\'s settings.'
        create_menu_action_unique(self, m, _('Customize plugin')+'...', 'config.png', _(tool_tip),
                                  None, triggered=self.show_configuration)
        self.gui.keyboard.finalize()

    def build_single_book_menus(self, book_id):
        '''
        Build the menus that change on the fly based on selected ebook's
        formats and their various properties.
        '''
        m = self.menu
        m.clear()
        kindle_formats = ['MOBI', 'AZW', 'AZW3', 'AZW4', 'PRC']
        book_list = self.gatherKindleFormats([book_id], kindle_formats)
        if not book_list:
            tool_tip = 'No suitable format to unpack.'
            error_menu = create_menu_item(self, m, _(tool_tip)+'...', None, _(tool_tip), None, None)
            error_menu.setEnabled(False)
            m.addSeparator()
            tool_tip = 'Configure the KindleUnpack plugin\'s settings.'
            create_menu_action_unique(self, m, _('Customize plugin')+'...', 'config.png', _(tool_tip),
                                      None, triggered=self.show_configuration)
            self.gui.keyboard.finalize()
            return

        format_dict = book_list[0][2]
        for format in format_dict.keys():
            format_details = format_dict[format].get_format_details()
            # Weird and unlikely possiblity that there is no file on disk for this format at this point.
            if format_details['errors'] is not None and format_details['errors'] == 'path':
                tool_tip = 'No file on disk. Can\'t unpack.'
                mnu_msg = '{0} Has no file associated with it.'.format(format)
                error_menu = create_menu_item(self, m, _(mnu_msg)+'...', None, _(tool_tip),
                                            None, None)
                error_menu.setEnabled(False)
                continue
            # Topaz format. Punt.
            elif format_details['errors'] is not None and format_details['errors'] == 'topaz':
                tool_tip = 'Can\'t unpack Topaz books.'
                mnu_msg = '{0} format is a Topaz book. Can\'t unpack.'.format(format)
                error_menu = create_menu_item(self, m, _(mnu_msg)+'...', None, _(tool_tip),
                                        None, None)
                error_menu.setEnabled(False)
                continue
            # Unknown error. Very likely not a valid kindlebook file. Exact error found in format_details['errors'].
            elif format_details['errors'] is not None:
                tool_tip = 'Unknown issues with this format.'
                mnu_msg = '{0} format might not be a valid mobi/kindlebook.'.format(format)
                error_menu = create_menu_item(self, m, _(mnu_msg)+'...', None, _(tool_tip),
                                            None, None)
                error_menu.setEnabled(False)
                continue

            kindle_obj = format_details['kindle_obj']

            mnu_img = 'drm-unlocked.png'
            mnu_tip = 'This {0} file is DRM-Free.'.format(format)
            if kindle_obj.isEncrypted:
                print('isEncrypted = {0}'.format(kindle_obj.isEncrypted))
                mnu_tip = 'This {0} file has DRM... can\'t unpack.'.format(format)
                mnu_img = 'drm-locked.png'
            ac = create_menu_item(self, m, _(format), mnu_img, _(mnu_tip), None)
            sm = QMenu()
            ac.setMenu(sm)
            # Standard unpack to external folder ... disable menu if kindlebook encrypted.
            tool_tip = 'Unpack the {0}\'s source components'.format(format)
            unpack_menu = create_menu_action_unique(self, sm, _('Unpack')+' {0}'.format(format), 'images/explode3.png',
                                                _(tool_tip), False, triggered=partial(self.unpack_ebook, kindle_obj))
            if kindle_obj.isEncrypted:
                unpack_menu.setEnabled(False)

            # Extract PDF file from AZW4
            if kindle_obj.isPrintReplica:
                tool_tip = 'Extract the PDF from the Print Replica format and add it to the library.'
                create_menu_action_unique(self, sm, _('Extract PDF')+'...', 'mimetypes/pdf.png', _(tool_tip), False,
                                            triggered=partial(self.extract_element, kindle_obj, book_id, u'AZW4', False))

            # Offer to split kindlegen dual format output.
            if kindle_obj.isComboFile:
                tool_tip = 'Split the combo KF8/MOBI file into its two components.'
                create_menu_action_unique(self, sm, _('Split KF8/MOBI')+'...', 'edit-cut.png', _(tool_tip),
                                            False, triggered=partial(self.combo_split, kindle_obj))

            # Extract ePub from the unpacked contents and add to current book's formats.
            convert_menu = None
            if kindle_obj.isKF8 or kindle_obj.isComboFile:
                tool_tip = 'Convert standalone KF8 file to its original ePub.'
                convert_menu = create_menu_action_unique(self, sm, _('KF8 to ePub')+'...', 'mimetypes/epub.png', _(tool_tip),
                                            False, triggered=partial(self.extract_element, kindle_obj, book_id, u'AZW3', False))
            if kindle_obj.isEncrypted and convert_menu is not None:
                convert_menu.setEnabled(False)

        # Add menu item to go to plugin configuration.
        m.addSeparator()
        tool_tip = 'Configure the KindleUnpack plugin\'s settings.'
        create_menu_action_unique(self, m, _('Customize plugin')+'...', 'config.png', _(tool_tip),
                                  None, triggered=self.show_configuration)
        self.gui.keyboard.finalize()
        return

    def update_db(self, bookfile, format, book_id):
        '''
        Update the calibre ebook entry with the extracted EPUB/PDF format.
        (never overwriting a pre-existing one)
        '''
        db = self.gui.library_view.model().db
        stream = lopen(bookfile, 'rb')
        return db.add_format(book_id, format, stream, index_is_id=True, replace=False, notify=True)

    def show_configuration(self):
        '''
        Show plugin's configuration widget.
        '''
        self.interface_action_base_plugin.do_user_config(self.gui)

    def directoryChooser(self):
        '''
        Select a folder, or use the one specified in the config widget.
        '''
        if cfg.plugin_prefs['Always_Use_Unpack_Folder']:
            return cfg.plugin_prefs['Unpack_Folder']
        else:
            return choose_dir(self.gui, _(PLUGIN_NAME + 'dir_chooser'),
                _('Select Directory To Unpack Kindle/Mobi Book To'))

    def gatherKindleFormats(self, book_ids, target_formats, goal_format=None):
        '''
        Gathers all the kindle formats for the book(s) and uses the KindleFormats class
        in utlities.py to collect details about each one. Including an initialized
        mobiProcessor object.
        '''
        db = self.gui.library_view.model().db
        books_info = []
        for book_id in book_ids:
            title = db.get_metadata(book_id, index_is_id=True, get_user_categories=False).title
            book = KindleFormats(book_id, db, target_formats, goal_format)
            details = book.get_formats()
            if details:
                books_info.append((book_id, title, details))
        return books_info

    def multi_dispatcher(self, book_ids, target_format):
        '''
        Prepares the necessaries to feed to ProgressDialog in dialogs.py
        '''
        db = self.gui.library_view.model().db
        if target_format == 'AZW3':
            attr = 'isKF8'
            goal_format = 'EPUB'
            status_msg_type='KF8 books'
            action_type='Unpacking ePubs from'
        elif target_format == 'AZW4':
            attr = 'isPrintReplica'
            goal_format = 'PDF'
            status_msg_type='Print Replica books'
            action_type='Extracting PDFs from'
        books_info = self.gatherKindleFormats(book_ids, [target_format], goal_format)
        # If we have stuff ... send it on its way to the pretty ProgressDialog.
        if books_info:
            d = ProgressDialog(self.gui, books_info, self.extract_element, db, target_format, attr,
                                   status_msg_type=status_msg_type, action_type=action_type)
            if d.wasCanceled():
                return
            successes, failures = d.get_results()
            if successes:
                ids_to_highlight = []
                for i in successes:
                    ids_to_highlight.append(i[0])
                self.highlight_entries(ids_to_highlight)
            title = PLUGIN_NAME + ' v' + PLUGIN_VERSION
            plural = '' if len(successes) == 1 else 's'
            msg = '<p>{0} {2} format{3} added to library. {1} not added. See log for details'.format(len(successes), len(failures), goal_format, plural)
            log = build_log(failures, successes, target_format, goal_format, status_msg_type[:-1])
            # print (log)
            sd = ResultsSummaryDialog(self.gui, title, msg, log)
            sd.exec_()
        else:
            return info_dialog(None, _(PLUGIN_NAME + ' v' + PLUGIN_VERSION),
                '<p>Nothing to do. Perhaps no books selected had {0} formats.'.format(target_format), show=True)

    def highlight_entries(self, ids_to_highlight):
        # self.gui.library_view.model().books_added(len(ids_to_highlight))
        # self.gui.library_view.model().refresh()
        # self.gui.tags_view.recount()
        # self.gui.library_view.model().set_highlight_only(True)
        self.gui.library_view.select_rows(ids_to_highlight)
        return

    def unpack_ebook(self, kindle_obj):
        '''
        Unpack kindlebook to external folder.
        '''
        outdir = self.directoryChooser()
        if outdir:
            try:
                kindle_obj.unpackMOBI(outdir)
            except Exception as e:
                return showErrorDlg(str(e), self.gui, True)
            open_local_file(outdir)

    def extract_element(self, kindle_obj, book_id, target, quiet=False):
        '''
        ExtractPDFs/EPUBs from AZW4/AZW3 format(s).
        '''
        outdir = PersistentTemporaryDirectory()
        errmsg = ''
        if target == 'AZW3':
            errmsg = 'An'
            format = 'EPUB'
            try:
                bookfile = kindle_obj.unpackEPUB(outdir)
            except Exception as e:
                if quiet:
                    return False, str(e)
                return showErrorDlg(str(e), self.gui, True)
        elif target == 'AZW4':
            errmsg = 'A'
            format = 'PDF'
            try:
                bookfile = kindle_obj.getPDFFile(outdir)
            except Exception as e:
                if quiet:
                    return False, str(e)
                return showErrorDlg(str(e), self.gui, True)

        if os.path.exists(bookfile):
            if not self.update_db(bookfile, format, book_id):
                errmsg += ' {0} format already exists for this book in this library! No attempt to overwrite it will be made.'.format(format)
                if quiet:
                    return False, None
                return showErrorDlg(errmsg, self.gui)
            current_idx = self.gui.library_view.currentIndex()
            if current_idx.isValid():
                self.gui.library_view.model().current_changed(current_idx, current_idx)
            if quiet:
                return True, None
            return info_dialog(None, _(PLUGIN_NAME + ' v' + PLUGIN_VERSION),
            '<p>{0} successfully unpacked and added to ebook\'s formats in library.'.format(format), show=True)

        errmsg = 'Couldn\'t find {0} in unpacked kindlebook.'.format(format)
        if quiet:
            return False, errmsg
        return showErrorDlg(errmsg, self.gui)

    def combo_split(self, kindle_obj):
        '''
        Split kindlegen output into its AZW3/MOBI pieces.
        '''
        outdir = self.directoryChooser()
        if outdir:
            try:
                kindle_obj.writeSplitCombo(outdir)
            except Exception as e:
                return showErrorDlg(str(e), self.gui, True)
            open_local_file(outdir)
