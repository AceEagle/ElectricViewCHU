from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import Qt, pyqtSignal
import logging
import os
from PyQt5 import uic

log = logging.getLogger(__name__)

ConnectionErrorOscilloDialogUiPath = os.path.dirname(os.path.realpath(__file__)) + '{0}ConnectionErrorOscilloDialogUI.ui'.format(os.sep)
Ui_connectionErrorOscilloDialog, QtBaseClass = uic.loadUiType(ConnectionErrorOscilloDialogUiPath)


class ConnectionErrorOscilloDialog(QDialog, Ui_connectionErrorOscilloDialog):

    s_windowClose = pyqtSignal()

    def __init__(self):
        super(ConnectionErrorOscilloDialog, self).__init__()
        self.setupUi(self)
        self.setAttribute(Qt.WA_AlwaysStackOnTop)

    def closeEvent(self, event):
        self.s_windowClose.emit()