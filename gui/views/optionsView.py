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

optionsViewUiPath = os.path.dirname(os.path.realpath(__file__)) + "{0}optionsViewUI.ui".format(os.sep)
Ui_optionsView, QtBaseClass = uic.loadUiType(optionsViewUiPath)


class OptionsView(QWidget, Ui_optionsView):
    instruments_connected = pyqtSignal()

    def __init__(self, model=None):
        super(OptionsView, self).__init__()
        self.model = model
        self.setupUi(self)
        self.threadpool = QThreadPool()
        self.rm = visa.ResourceManager()
        self.instrumentsList = None
        self.myOscilloStr = ""
        self.myAFGStr = ""

        self.update_comboBox()
        self.connect_instruments_thread()
        self.myOscillo = None
        self.myAFG = None
        self.USBPortsAFGComboBox.currentTextChanged.connect(self.connect_instruments_thread)
        self.USBPortsOscilloComboBox.currentTextChanged.connect(self.connect_instruments_thread)


        log.debug("Connecting optionsView gui Widgets")

    # def create_threads(self, *args):
    #    self.acqWorker = Worker(self.manage_data_flow, *args)
    #   self.acqWorker.moveToThread(self.acqThread)
    #  self.acqThread.started.connect(self.acqWorker.run)

    def connect_buttons(self):
        self.RefreshPButton.clicked.connect(self.update_combobox)

    def update_comboBox(self):
        log.debug("Updating USBPortsList")
        try:
            self.rm = visa.ResourceManager()
            self.instrumentsList = self.rm.list_resources()
            self.USBPortsAFGComboBox.clear()
            self.USBPortsOscilloComboBox.clear()
            self.USBPortsAFGComboBox.addItems(self.instrumentsList)
            self.USBPortsOscilloComboBox.addItems(self.instrumentsList)
        except:
            pass

    def connect_instruments_thread(self):
        worker = Worker(self.connect_instruments)
        self.threadpool.start(worker)

    def connect_instruments(self, progress_callback):
        log.debug("Connection to oscilloscope")
        self.myOscilloStr = (str(self.USBPortsOscilloComboBox.currentText()))
        try:
            self.myOscillo = self.rm.open_resource(self.myOscilloStr)
            return self.myOscillo
        except:
            log.info("Error, couldnt connect to oscillo")
            pass
        self.myAFGStr = str(self.USBPortsAFGComboBox.currentText())
        try:
            self.myAFG = self.rm.open_resource(self.myAFGStr)
            return self.myAFG
        except:
            log.info("Error, couldnt connect the AAFG")
            pass
        print(self.myAFG, self.myOscillo)

    def get_data(self, channel):
        # self.myOscillo.read_data_one_channel(channel, x_axis_out=False)
        pass

    def inject_parameters(self):
        pass
