# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__docformat__ = 'restructuredtext en'

try:
    from qt.core import (Qt, QProgressDialog, QTimer, QSize, QDialog, QIcon,
                    QDialogButtonBox, QApplication, QTextBrowser, QVBoxLayout)
except ImportError:
    try:
        from PyQt5.Qt import (Qt, QProgressDialog, QTimer, QSize, QDialog, QIcon,
                        QDialogButtonBox, QApplication, QTextBrowser, QVBoxLayout)
    except ImportError:
        from PyQt4.Qt import (Qt, QProgressDialog, QTimer, QSize, QDialog, QIcon,
                        QDialogButtonBox, QApplication, QTextBrowser, QVBoxLayout)

from calibre.gui2.dialogs.message_box import MessageBox
from calibre_plugins.kindleunpack_plugin.__init__ import (PLUGIN_NAME, PLUGIN_VERSION)

class ProgressDialog(QProgressDialog):
    '''
    Used to process Multiple selections of AZW3/AZW4 into EPUBs/PDFs.
    '''
    def __init__(self, gui, books, callback_fn, db, target_format, attr, status_msg_type='books', action_type='Checking'):
        self.total_count = len(books)
        QProgressDialog.__init__(self, '', 'Cancel', 0, self.total_count, gui)
        self.setMinimumWidth(500)
        self.books, self.callback_fn, self.db, self.target_format, self.attr = books, callback_fn, db, target_format, attr
        self.action_type, self.status_msg_type = action_type, status_msg_type
        if attr == 'isKF8':
            self.kindle_type = 'KF8'
            self.goal = 'EPUB'
        elif attr == 'isPrintReplica':
            self.kindle_type = 'PrintReplica'
            self.goal = 'PDF'
        self.gui = gui
        zero = 0
        self.setWindowTitle('{0} {1} {2} ({3} issues)...'.format(self.action_type, self.total_count, self.status_msg_type, zero))
        self.i, self.successes, self.failures = 0, [], []
        QTimer.singleShot(0, self.do_multiple_book_action)
        self.exec_()

    def do_multiple_book_action(self):
        if self.wasCanceled():
            return self.do_close()
        if self.i >= self.total_count:
            return self.do_close()
        book_info = self.books[self.i]
        self.i += 1

        book_id, dtitle, format_dict = book_info[0], book_info[1], book_info[2]

        all_formats = self.db.formats(book_id, index_is_id=True, verify_formats=True)
        if all_formats is not None:
            all_formats = all_formats.split(',')
        else:
            all_formats = []

        self.setWindowTitle('{0} {1} {2}  ({3} issues)...'.format(self.action_type, self.total_count,
                                                                self.status_msg_type, len(self.failures)))
        self.setLabelText('{0}: {1}'.format(self.action_type, dtitle))

        if self.target_format in format_dict.keys():
            format = format_dict[self.target_format].get_format_details()

            if format['errors'] is not None:
                self.failures.append((2, dtitle, '{0}\'s {1} format might not be a valid mobi/kindlebook.'.format(dtitle, format)))
            else:
                kindle_obj = format['kindle_obj']

                if not kindle_obj.isEncrypted:
                    if getattr(kindle_obj, self.attr):
                        if format['goal_format'] not in all_formats:
                            success, error = self.callback_fn(kindle_obj, book_id, self.target_format, True)
                            if success:
                                self.successes.append((book_id, dtitle))
                            elif error is None:
                                self.failures.append((5, dtitle, '{0} already has a {1} format. Won\'t overwrite.'.format(dtitle, format['goal_format'])))
                            else:
                                self.failures.append((4, dtitle, 'Unknown error processing {0}\'s {1} format'.format(dtitle, self.target_format)))
                        else:
                            self.failures.append((5, dtitle, '{0} already has a {1} format. Won\'t overwrite.'.format(dtitle, format['goal_format'])))
                    else:
                        self.failures.append((3, dtitle, '{0}\'s {1} format is not a {2} book.'.format(dtitle, self.target_format, self.kindle_type)))
                else:
                    self.failures.append((2, dtitle, '{0} is encrypted.'.format(dtitle)))
        else:
            self.failures.append((1, dtitle, '{0} has no {1} format to work with.'.format(dtitle, self.target_format)))

        self.setValue(self.i)

        QTimer.singleShot(0, self.do_multiple_book_action)

    def do_close(self):
        self.hide()
        self.gui = None

    def get_results(self):
        return self.successes, self.failures


class ViewLog(QDialog):

    def __init__(self, title, html, parent=None):
        QDialog.__init__(self, parent)
        self.l = l = QVBoxLayout()
        self.setLayout(l)

        self.tb = QTextBrowser(self)
        QApplication.setOverrideCursor(Qt.WaitCursor)
        # Rather than formatting the text in <pre> blocks like the calibre
        # ViewLog does, instead just format it inside divs to keep style formatting
        html = html.replace('\t','&nbsp;&nbsp;&nbsp;&nbsp;')
        html = html.replace('> ','>&nbsp;')
        self.tb.setHtml('<div>{0}</div>'.format(html))
        QApplication.restoreOverrideCursor()
        l.addWidget(self.tb)

        self.bb = QDialogButtonBox(QDialogButtonBox.Ok)
        self.bb.accepted.connect(self.accept)
        self.bb.rejected.connect(self.reject)
        self.copy_button = self.bb.addButton(_('Copy to clipboard'),
                self.bb.ActionRole)
        self.copy_button.setIcon(QIcon(I('edit-copy.png')))
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        l.addWidget(self.bb)
        self.setModal(False)
        self.resize(QSize(700, 500))
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon(I('debug.png')))
        self.show()

    def copy_to_clipboard(self):
        txt = self.tb.toPlainText()
        QApplication.clipboard().setText(txt)


class ResultsSummaryDialog(MessageBox):

    def __init__(self, parent, title, msg, log=None, det_msg=''):
        '''
        :param log: An HTML or plain text log
        :param title: The title for this popup
        :param msg: The msg to display
        :param det_msg: Detailed message
        '''
        MessageBox.__init__(self, MessageBox.INFO, title, msg,
                det_msg=det_msg, show_copy_button=False,
                parent=parent)
        self.log = log
        self.vlb = self.bb.addButton(_('View log'), self.bb.ActionRole)
        self.vlb.setIcon(QIcon(I('debug.png')))
        self.vlb.clicked.connect(self.show_log)
        self.det_msg_toggle.setVisible(bool(det_msg))
        self.vlb.setVisible(True)

    def show_log(self):
        self.log_viewer = ViewLog(PLUGIN_NAME + ' v' + PLUGIN_VERSION, self.log,
                parent=self)
