from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal, QThreadPool
import os
from PyQt5 import uic
from tools.pyqtWorker import Worker
import logging
log = logging.getLogger(__name__)

optionsViewUiPath = os.path.dirname(os.path.realpath(__file__)) + "{0}optionsViewUI.ui".format(os.sep)
Ui_optionsView, QtBaseClass = uic.loadUiType(optionsViewUiPath)

SIGNAL_PLOT_TOGGLED = "plot.toggled.graphic"


class OptionsView(QWidget, Ui_optionsView):
    instruments_changed = pyqtSignal()

    def __init__(self, model=None, controller=None):
        super(OptionsView, self).__init__()
        self.model = model
        self.setupUi(self)
        self.threadpool = QThreadPool()
        self.instrumentsList = None
        self.myOscilloStr = ""
        self.myAFGStr = ""
        self.modeList = ["Continuous", "Sweep", "Modulation", "Burst"]
        self.waveformList = ["Sine", "Square", "Ramp", "Pulse", "Arb"]
        self.mode = ""
        self.waveForm = ""

        self.connect_buttons()
        self.update_communication_combobox()
        self.initialise_combobox()
        self.connect_combobox_signals()

        log.info("Connecting optionsView GUI Widgets")

    def connect_buttons(self):
        self.RefreshPButton.clicked.connect(self.update_communication_combobox)
        self.InjectButton.clicked.connect(self.inject_parameters_thread)

    def connect_signals(self):
        pass

    def connect_combobox_signals(self):
        self.AFGModeComboBox.currentIndexChanged.connect(self.update_buttons_values_thread)
        self.AFGWaveFormComboBox.currentIndexChanged.connect(self.update_buttons_values_thread)
        self.USBPortsAFGComboBox.currentIndexChanged.connect(self.connect_instruments_thread)
        self.USBPortsOscilloComboBox.currentIndexChanged.connect(self.connect_instruments_thread)

    def initialise_combobox(self):
        self.AFGModeComboBox.addItems(self.modeList)
        self.AFGWaveFormComboBox.addItems(self.waveformList)

    def update_buttons_values_thread(self):
        worker = Worker(self.update_buttons_values)
        self.threadpool.start(worker)

    def update_buttons_values(self, progress_callback):
        self.mode = self.AFGModeComboBox.currentText()
        self.waveForm = self.AFGWaveFormComboBox.currentText()
        print(self.mode, self.waveForm)

    def update_communication_combobox(self):
        self.model.new_resource_manager()
        try:
            log.debug("Updating USBPortsList")
            self.instrumentsList = self.model.rm.list_resources()
            self.USBPortsAFGComboBox.clear()
            self.USBPortsOscilloComboBox.clear()
            self.USBPortsAFGComboBox.addItems(self.instrumentsList)
            self.USBPortsOscilloComboBox.addItems(self.instrumentsList)
            self.connect_instruments_thread()
        except:
            log.debug("Updating USBPortsList")
            self.USBPortsAFGComboBox.clear()
            self.USBPortsOscilloComboBox.clear()

    def connect_instruments_thread(self):
        myOscilloStr = (str(self.USBPortsOscilloComboBox.currentText()))
        myAFGStr = str(self.USBPortsAFGComboBox.currentText())
        worker = Worker(self.model.connect_instruments, myOscilloStr, myAFGStr)
        self.threadpool.start(worker)

    def inject_parameters_thread(self):
        worker = Worker(self.inject_parameters, self.AFGModeComboBox.currentText(), self.AFGFrequencyDSpinBox.value(), self.AFGWaveFormComboBox.currentText(), self.cycle, self.trigInt, self.nbData, self.trigLevel)
        self.threadpool.start(worker)

    def inject_parameters(self, mode, freq, wave, cycle, trigInt, nbData, trigLevel, progress_callback):
        self.model.inject_AFG(mode, freq, wave, cycle, trigInt)
        self.model.inject_Oscillo(nbData, trigLevel)

    def give_AFG_and_Oscillo(self):
        return self.model.myAFG, self.model.myOscillo

