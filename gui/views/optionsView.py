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
        self.nbDataList = ["1000", "10000", "100000", "1M", "10M"]
        self.modeList = ["Continuous", "Sweep", "Modulation", "Burst"]
        self.waveformList = ["Sine", "Square", "Ramp", "Pulse", "Arb"]
        self.acquisitionList = ["Auto (Fastest)", "1s", "5s", "10s", "30s", "1min", "5min", "10min", "30min"]
        self.acquisitionDict = {
            "Auto (Fastest)" : None,
            "1s": 1,
            "5s": 5,
            "10s": 10,
            "30s": 30,
            "1min": 60,
            "5min": 300,
            "10min": 600,
            "30min": 1800
        }
        self.mode = ""
        self.waveForm = ""
        self.channelListe = ["CH1", "CH2", "CH3", "CH4"]
        self.channels = {"voltage" : "", "charge" : "", "current" : ""}

        self.connect_buttons()
        self.update_communication_combobox()
        self.initialise_combobox()
        self.connect_combobox_signals()
        self.update_spinbox_signals()
        log.info("Connecting optionsView GUI Widgets")

    def connect_buttons(self):
        self.ConnectToInstrumentsPButton.clicked.connect(self.connect_instruments)
        self.RefreshPButton.clicked.connect(self.update_communication_combobox)
        self.InjectPButton.clicked.connect(self.inject_parameters_thread)

    def connect_signals(self):
        pass

    def connect_combobox_signals(self):
        self.AFGModeComboBox.currentIndexChanged.connect(self.update_buttons_values_thread)
        self.AFGWaveFormComboBox.currentIndexChanged.connect(self.update_buttons_values_thread)

    def update_spinbox_signals(self):
        self.ElectrodesSurfaceDSpinBox.valueChanged.connect(self.update_buttons_values_thread)
        self.CapacitanceDSpinBox.valueChanged.connect(self.update_buttons_values_thread)
        self.AFGFrequencyDSpinBox.valueChanged.connect(self.update_buttons_values_thread)
        self.AFGPercentageSpinBox.valueChanged.connect(self.update_buttons_values_thread)
        self.TriggerIntervalDSpinBox.valueChanged.connect(self.update_buttons_values_thread)

    def initialise_combobox(self):
        self.AcquisitionComboBox.addItems(self.acquisitionList)
        self.AcquisitionComboBox.setCurrentText("Auto (Fastest)")
        self.VoltageComboBox.addItems(self.channelListe)
        self.VoltageComboBox.setCurrentText("CH1")
        self.ChargeComboBox.addItems(self.channelListe)
        self.ChargeComboBox.setCurrentText("CH2")
        self.CurrentComboBox.addItems(self.channelListe)
        self.CurrentComboBox.setCurrentText("CH3")
        self.AFGModeComboBox.addItems(self.modeList)
        self.AFGModeComboBox.setCurrentText("Burst")
        self.AFGWaveFormComboBox.addItems(self.waveformList)
        self.AFGModeComboBox.setCurrentText("Sine")
        self.NbDataPointsComboBox.addItems(self.nbDataList)
        self.AFGModeComboBox.setCurrentText("100000")
        self.AFGFrequencyDSpinBox.setValue(10.00)
        self.AFGPercentageSpinBox.setValue(50)
        self.TriggerIntervalDSpinBox.setValue(10.00)
        self.ElectrodesSurfaceDSpinBox.setValue(28.31)
        self.CapacitanceDSpinBox.setValue(0.22)

    def update_buttons_values_thread(self):
        worker = Worker(self.update_buttons_values)
        self.threadpool.start(worker)

    def update_buttons_values(self, progress_callback):
        self.acquisition = self.acquisitionDict[self.AcquisitionComboBox.currentText()]
        self.mode = self.AFGModeComboBox.currentText()
        self.waveForm = self.AFGWaveFormComboBox.currentText()
        self.surface = self.ElectrodesSurfaceDSpinBox.value()
        self.frequency = self.AFGFrequencyDSpinBox.value()
        self.cyclePercentage = self.AFGPercentageSpinBox.value()
        self.triggerInterval = self.TriggerIntervalDSpinBox.value()
        self.nbDataPoints = self.NbDataPointsComboBox.currentText()
        self.capacitance = self.CapacitanceDSpinBox.value()
        self.channels["voltage"] = self.VoltageComboBox.currentText()
        self.channels["charge"] = self.ChargeComboBox.currentText()
        self.channels["current"] = self.CurrentComboBox.currentText()

    def update_communication_combobox(self):
        self.model.new_resource_manager()
        try:
            log.debug("Updating USBPortsList")
            self.instrumentsList = self.model.rm.list_resources()
            self.USBPortsAFGComboBox.clear()
            self.USBPortsOscilloComboBox.clear()
            self.USBPortsAFGComboBox.addItems(self.instrumentsList)
            self.USBPortsOscilloComboBox.addItems(self.instrumentsList)
        except:
            log.debug("Updating USBPortsList")
            self.USBPortsAFGComboBox.clear()
            self.USBPortsOscilloComboBox.clear()

    def connect_instruments(self):
        myOscilloStr = (str(self.USBPortsOscilloComboBox.currentText()))
        myAFGStr = str(self.USBPortsAFGComboBox.currentText())
        self.model.connect_oscillo(myOscilloStr)
        self.model.connect_afg(myAFGStr)

    def inject_parameters_thread(self):
        worker = Worker(self.inject_parameters, self.mode, self.frequency,
                        self.waveForm, self.cyclePercentage, self.triggerInterval,
                        self.nbDataPoints, self.surface, self.capacitance, self.channels, self.acquisition)
        self.threadpool.start(worker)

    def inject_parameters(self, mode, freq, wave, cycle, trigInt, nbData, surface, capacitance, channels, acquisition, progress_callback):
        self.model.change_channels(channels)
        self.model.inject_AFG(mode, freq, wave, cycle)
        self.model.inject_Oscillo(nbData)
        self.model.change_surface_and_trigInt(surface, trigInt, capacitance, acquisition)

    def give_AFG_and_Oscillo(self):
        return self.model.instrumentsDict["myOscillo"], self.model.instrumentsDict["myOscillo"]

