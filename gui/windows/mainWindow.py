from gui.dialog.helpDialog import HelpDialog
from gui.views.filterView import FilterView
from gui.views.lensView import LensView
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QVBoxLayout, QTabWidget, QAction, QApplication
from PyQt5.QtCore import Qt, pyqtSlot, QFile, QTextStream
import logging
import os
from PyQt5 import uic

log = logging.getLogger(__name__)

MainWindowPath = os.path.dirname(os.path.realpath(__file__)) + '{}mainWindowUi.ui'.format(os.sep)
Ui_MainWindow, QtBaseClass = uic.loadUiType(MainWindowPath)