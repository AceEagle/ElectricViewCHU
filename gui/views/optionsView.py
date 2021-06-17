from PyQt5.QtWidgets import QWidget, QMessageBox, QCheckBox, QFileDialog, QComboBox
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QThread
import copy
import os
from pyqtgraph import LinearRegionItem, mkBrush, mkPen, SignalProxy, InfiniteLine, TextItem, ArrowItem
from PyQt5 import uic
import pyvisa as visa
from tools.pyqtWorker import Worker
from PyTektronixScope import TektronixScope
import logging


log = logging.getLogger(__name__)

optionsViewUiPath = os.path.dirname(os.path.realpath(__file__)) + "{0}optionsViewUI.ui".format(os.sep)
Ui_optionsView, QtBaseClass = uic.loadUiType(optionsViewUiPath)


class OptionsView(QWidget, Ui_optionsView):
    s_data_changed = pyqtSignal(dict)
    s_data_acquisition_done = pyqtSignal()

    def __init__(self, model=None):
        super(OptionsView, self).__init__()
        self.model = model
        self.setupUi(self)

        self.rm = visa.ResourceManager()
        self.oscillatorList = self.rm.list_resources()


        self.update_comboBox()
        self.connect_oscillo()
        self.myOscillo = None
#        self.create_threads()

        log.debug("Connecting optionsView gui Widgets")

    # def create_threads(self, *args):
    #    self.acqWorker = Worker(self.manage_data_flow, *args)
    #   self.acqWorker.moveToThread(self.acqThread)
    #  self.acqThread.started.connect(self.acqWorker.run)

    def update_comboBox(self):
        log.debug("Updating USBPortsList")
        self.USBPortsComboBox.addItems(self.oscillatorList)

    def connect_oscillo(self):
        log.debug("Connection to oscilloscope")
        #self.myOscillo = TektronixScope(str(self.USBPortsComboBox.currentText()))

    def get_data(self, channel):
        #self.myOscillo.read_data_one_channel(channel, x_axis_out=False)
        pass
