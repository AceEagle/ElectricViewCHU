from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import Qt, pyqtSignal
import logging
import os
from PyQt5 import uic

log = logging.getLogger(__name__)

ConnectionErrorDialogUiPath = os.path.dirname(os.path.realpath(__file__)) + '{0}ConnectionErrorDialogUI.ui'.format(os.sep)
Ui_connectionErrorDialog, QtBaseClass = uic.loadUiType(ConnectionErrorDialogUiPath)


class ConnectionErrorDialog(QDialog, Ui_connectionErrorDialog):

    s_windowClose = pyqtSignal()

    def __init__(self):
        super(ConnectionErrorDialog, self).__init__()
        self.setupUi(self)
        self.setAttribute(Qt.WA_AlwaysStackOnTop)

    def closeEvent(self, event):
        self.s_windowClose.emit()