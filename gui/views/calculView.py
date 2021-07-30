from PyQt5.QtWidgets import QWidget, QMessageBox, QCheckBox, QFileDialog, QComboBox
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QThreadPool, QThread
import copy
import os
from pyqtgraph import LinearRegionItem, mkBrush, mkPen, SignalProxy, InfiniteLine, TextItem, ArrowItem
from PyQt5 import uic
import pyvisa as visa
from tools.pyqtWorker import Worker
from PyTektronixScope import TektronixScope
import logging
log = logging.getLogger(__name__)

calculViewUiPath = os.path.dirname(os.path.realpath(__file__)) + "{0}calculViewUI.ui".format(os.sep)
Ui_calculView, QtBaseClass = uic.loadUiType(calculViewUiPath)

SIGNAL_PLOT_TOGGLED = "plot.toggled.graphic"


class CalculView(QWidget, Ui_calculView):
    instruments_changed = pyqtSignal()

    def __init__(self, model=None, controller=None):
        super(CalculView, self).__init__()
        self.model = model
        self.setupUi(self)
        self.threadpool = QThreadPool()

        self.connect_buttons()


    # def create_threads(self, *args):
    #    self.acqWorker = Worker(self.manage_data_flow, *args)
    #   self.acqWorker.moveToThread(self.acqThread)
    #  self.acqThread.started.connect(self.acqWorker.run)

    def connect_buttons(self):
        self.OpenPButton.clicked.connect(self.search_file)
        #self.OverwritePButton.clicked.connect(self.inject_parameters_thread)

    def connect_signals(self):
        pass

    def search_file(self):
        name = QFileDialog.getOpenFileName(self, 'Open File', '', 'Txt Files (*.txt);;All Files (*)',
                                           options=QFileDialog.DontUseNativeDialog)
        if name[0] == '':
            log.info("File is not good")

        if name[1] == 'Txt Files (*.txt)' and name[0][-3:] != '.txt':
            name = name[0] + '.txt'
        else:
            name = name[0]

        text=open(name).read()
        self.PlainTextEdit.setPlainText(text)