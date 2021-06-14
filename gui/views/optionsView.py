from PyQt5.QtWidgets import QWidget, QMessageBox, QCheckBox, QFileDialog
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QThread
import copy
import os
from pyqtgraph import LinearRegionItem, mkBrush, mkPen, SignalProxy, InfiniteLine, TextItem, ArrowItem
from PyQt5 import uic
import pyvisa as visa


import logging


log = logging.getLogger(__name__)

optionsViewUiPath = os.path.dirname(os.path.realpath(__file__)) + "{0}optionsViewUI.ui".format(os.sep)
Ui_optionsView, QtBaseClass = uic.loadUiType(optionsViewUiPath)


class OptionsView(QWidget, Ui_optionsView):
    s_data_changed = pyqtSignal(dict)
    s_data_acquisition_done = pyqtSignal()

    def __init__(self, model=None):
        super(OptionsView, self).__init__()
        self.setupUi(self)
        self.model = model
        self.plotItem = None
        self.dataPlotItem = None

        self.rm = visa.ResourceManager()
        self.oscillatorList = self.rm.list_resources()

        self.connect_widgets()

    def connect_widgets(self):
        self.USBPortsList.addIteam(self.oscillatorList[i])


    def connect_signals(self):
        pass