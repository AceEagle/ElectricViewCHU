import time

from gui.dialog.ConnectionErrorOscilloDialog import ConnectionErrorOscilloDialog
from gui.dialog.ConnectionErrorAFGDialog import ConnectionErrorAFGDialog
import numpy as np
import json
from tools.pyqtWorker import Worker
from PyQt5.QtCore import pyqtSignal, QObject, QThreadPool
import logging
from Data import Data
import pyvisa as visa

log = logging.getLogger(__name__)

SIGNAL_PLOT_TOGGLED = "plot.toggled.graphic"


class PlasmaAnalyser(QObject):
    s_data_changed = pyqtSignal(dict)
    instruments_connected = pyqtSignal(list)

    def __init__(self):
        super(PlasmaAnalyser, self).__init__()
        self.instrumentsDict = {"myOscillo": None, "myAFG": None}
        self.surface = 0
        self.x1, self.x2, self.x3 = 1, 1, 1
        self.worker1finished, self.worker2finished, self.worker3finished = False, False, False
        self.calcul1finished, self.calcul2finished, self.calcul3finished, self.calcul4finished, self.calcul5finished, self.calcul6finished = False, False, False, False, False, False
        self.timeList = []
        self.timeList, self.xList1, self.xList2, self.xList3 = [], [], [], []
        self.vcc, self.falsevcc = 0, 0

        self.connectionErrorOscilloDialog = ConnectionErrorOscilloDialog()
        self.connectionErrorAFGDialog = ConnectionErrorAFGDialog()
        self.threadpool = QThreadPool()
        self.rm = visa.ResourceManager()
        self.savedStatusDataDict = {}
        self.create_empty_savedStatusDataDict()
        self.connect_to_signals()

    def change_channels(self, channeldict):
        self.voltageCh = channeldict["voltage"]
        self.chargeCh = channeldict["charge"]
        self.currentCh = channeldict["current"]

    def load_parameters(self, jsonFilePath):
        with open(jsonFilePath) as f:
            parametersFile = json.load(f)
        self.parameters = parametersFile[0]
        return self.parameters

    def new_resource_manager(self):
        log.info("New Resource Manager")
        self.rm.close()
        self.rm = visa.ResourceManager()

    def connect_oscillo(self, oscilloStr):
        log.info("Connection to instruments")
        try:
            self.instrumentsDict["myOscillo"] = self.rm.open_resource(oscilloStr)
            log.debug(self.instrumentsDict["myOscillo"])
        except:
            self.connectionErrorOscilloDialog.exec_()

    def connect_afg(self, afgStr):
        log.info("Connection to instruments")
        try:
            self.instrumentsDict["myAFG"] = self.rm.open_resource(afgStr)
            log.debug(self.instrumentsDict["myAFG"])
        except:
            self.connectionErrorAFGDialog.exec_()

    def inject_AFG(self, mode, freq, wave, cycle):
        self.instrumentsDict["myAFG"].write(f"SOURce1:{mode}:MODE")
        self.instrumentsDict["myAFG"].write(f":SOURCE:FREQUENCY {freq}KHZ")
        self.instrumentsDict["myAFG"].write(f"SOURce1:FUNCtion:{wave}")
        if cycle != 0:
            self.instrumentsDict["myAFG"].write(f"SOURce1:BURSt:NCYCles {cycle}")

    def inject_Oscillo(self, nbData):
        self.instrumentsDict["myOscillo"].write(f"HORizontal:RECOrdlength {nbData}")
        self.nbData = nbData

    def change_surface_and_trigInt(self, surface, trigInt, capacitance, acquisition):
        self.surface = float(surface)
        self.trigInterval = float(trigInt)
        self.capacitance = float(capacitance) * 1E-6
        self.acquisition = acquisition

    def get_oscillo(self):
        return self.self.instrumentsDict["myOscillo"]

    def get_afg(self):
        return self.self.instrumentsDict["myAFG"]

    def create_empty_savedStatusDataDict(self):
        for graphic in Data().graphics:
            self.savedStatusDataDict[graphic] = {}
            self.savedStatusDataDict[graphic]["data"] = {"x":[], "y":[]}

    def connect_to_signals(self):
        pass

    def send_data_to_plot(self, graphics=None):
        self.max1 = max(self.dataCH1)
        self.min1 = min(self.dataCH1)
        log.info("sending data")
        self.s_data_changed.emit(self.savedStatusDataDict)
        if self.launch_state is True:
            if self.acquisition is not None:
                log.debug("Sleep time")
                time.sleep(self.acquisition)
            worker = Worker(self.launch_propagation)
            self.threadpool.start(worker)

    def launch_propagation(self, progress_callback):
        self.launch_state = True
        log.info("=== === === SIMULATION STARTED === === ===")
        if self.acquisition is not None:
            time.sleep(self.acquisition)
        else:
            self.get_data_thread()

    def stop_propagation(self, progress_callback):
        self.launch_state = False
        log.info("=== === === SIMULATION STOPPED === === ===")

    def reset_save_status(self, progress_callback):
        self.create_empty_savedStatusDataDict()
        self.xList1.clear(), self.xList2.clear(), self.xList3.clear()
        self.x1 = 0
        self.x2 = 0
        self.x3 = 0
        self.send_data_to_plot()
        log.info("=== === === SIMULATION RESETED === === ===")

    def thread_to_true1(self):
        self.worker1finished = True
        self.wait_for_3threads()

    def thread_to_true2(self):
        self.worker2finished = True
        self.wait_for_3threads()

    def thread_to_true3(self):
        self.worker3finished = True
        self.wait_for_3threads()

    def calcul_to_true1(self):
        self.calcul1finished = True
        self.wait_for_6threads()

    def calcul_to_true2(self):
        self.calcul2finished = True
        self.wait_for_6threads()

    def calcul_to_true3(self):
        self.calcul3finished = True
        self.wait_for_6threads()

    def calcul_to_true4(self):
        self.calcul4finished = True
        self.wait_for_6threads()

    def calcul_to_true5(self):
        self.calcul5finished = True
        self.wait_for_6threads()

    def calcul_to_true6(self):
        self.calcul6finished = True
        self.wait_for_6threads()

    def wait_for_6threads(self):
        if self.calcul1finished is True and self.calcul2finished is True and self.calcul3finished is True and self.calcul4finished is True and self.calcul5finished is True and self.calcul6finished is True:
            self.calcul1finished, self.calcul2finished, self.calcul3finished, self.calcul4finished, self.calcul5finished, self.calcul6finished = False, False, False, False, False, False
            self.send_data_to_plot()
        else:
            pass

    def wait_for_3threads(self):
        if self.worker1finished is True and self.worker2finished is True:
            self.worker1finished, self.worker2finished, self.worker3finished = False, False, False
            self.save_status()
        else:
            pass

    def get_data_thread(self):
        self.instrumentsDict["myOscillo"].write("ACQuire:STATE ON")
        self.instrumentsDict["myOscillo"].write("HORizontal:SCAle 1E-3")
        self.instrumentsDict["myOscillo"].write("HORizontal:DELay:MODe OFF")
        self.instrumentsDict["myOscillo"].write("HORizontal:POSition 0")
        self.frequency = float(self.instrumentsDict["myAFG"].query(":SOURCE:FREQUENCY?"))
        self.cycles = float(self.instrumentsDict["myAFG"].query("SOURce1:BURSt:NCYCles?"))


        self.instrumentsDict["myOscillo"].write(f":DATa:ENCdg ASCIi;:DATa:SOURce {self.voltageCh}")
        self.instrumentsDict["myOscillo"].write("ACQuire:STATE OFF")

        self.x1zero = float(self.instrumentsDict["myOscillo"].query(":WFMOutpre:XZEro?"))
        self.x1incr = float(self.instrumentsDict["myOscillo"].query(":WFMOutpre:XINcr?"))
        self.y1zero = float(self.instrumentsDict["myOscillo"].query(":WFMOutpre:YZEro?"))
        self.y1mult = float(self.instrumentsDict["myOscillo"].query(":WFMOutpre:YMUlt?"))
        self.dataCH1 = self.instrumentsDict["myOscillo"].query_ascii_values("CURVe?")
        log.debug(len(self.dataCH1))

        self.instrumentsDict["myOscillo"].write(f"DATa:SOURce {self.chargeCh}")
        self.x2zero = float(self.instrumentsDict["myOscillo"].query(":WFMOutpre:XZEro?"))
        self.x2incr = float(self.instrumentsDict["myOscillo"].query(":WFMOutpre:XINcr?"))
        self.y2zero = float(self.instrumentsDict["myOscillo"].query(":WFMOutpre:YZEro?"))
        self.y2mult = float(self.instrumentsDict["myOscillo"].query(":WFMOutpre:YMUlt?"))
        self.dataCH2 = self.instrumentsDict["myOscillo"].query_ascii_values("CURVe?")
        log.debug(len(self.dataCH2))

        self.instrumentsDict["myOscillo"].write(f"DATa:SOURce {self.currentCh}")
        self.x3zero = float(self.instrumentsDict["myOscillo"].query(":WFMOutpre:XZEro?"))
        self.x3incr = float(self.instrumentsDict["myOscillo"].query(":WFMOutpre:XINcr?"))
        self.y3zero = float(self.instrumentsDict["myOscillo"].query(":WFMOutpre:YZEro?"))
        self.y3mult = float(self.instrumentsDict["myOscillo"].query(":WFMOutpre:YMUlt?"))
        self.dataCH3 = self.instrumentsDict["myOscillo"].query_ascii_values("CURVe?")

        self.instrumentsDict["myOscillo"].write("ACQuire:STATE ON")

        workerch1 = Worker(self.convert_strlist_to_intlist1, self.dataCH1)
        workerch2 = Worker(self.convert_strlist_to_intlist2, self.dataCH2)
        workerch3 = Worker(self.convert_strlist_to_intlist3, self.dataCH3)

        workerch1.signals.finished.connect(self.thread_to_true1)
        workerch2.signals.finished.connect(self.thread_to_true2)
        workerch3.signals.finished.connect(self.thread_to_true3)

        self.threadpool.start(workerch1)
        self.threadpool.start(workerch2)
        self.threadpool.start(workerch3)


    def convert_x_into_real_data_1(self):
        self.x1 += 1
        return self.x1zero + (self.x1incr * (self.x1 - 1))

    def convert_y_into_real_data_1(self, data):
        return self.y1zero + (data * self.y1mult)


    def convert_x_into_real_data_2(self):
        self.x2 += 1
        return self.x2zero + (self.x2incr * (self.x2 - 1))

    def convert_y_into_real_data_2(self, data):
        return self.capacitance * (self.y2zero + (data * self.y2mult))


    def convert_x_into_real_data_3(self):
        self.x3 += 1
        return self.x3zero + (self.x3incr * (self.x3 - 1))

    def convert_y_into_real_data_3(self, data):
        return self.y3zero + (data * self.y3mult)

    def convert_strlist_to_intlist1(self, string, progress_callback):
        self.xList1 = []
        yconverted = list(map(self.convert_y_into_real_data_1, self.dataCH1))
        for x in range(len(yconverted)):
            self.xList1.append(float(self.convert_x_into_real_data_1()))
        self.dataCH1 = yconverted

    def convert_strlist_to_intlist2(self, string, progress_callback):
        self.xList2 = []
        yconverted = list(map(self.convert_y_into_real_data_2, self.dataCH2))
        for x in range(len(yconverted)):
            self.xList2.append(self.convert_x_into_real_data_2())
        self.dataCH2 = yconverted

    def convert_strlist_to_intlist3(self, string, progress_callback):
        self.xList3 = []
        yconverted = list(map(self.convert_y_into_real_data_3, self.dataCH3))
        for x in range(len(yconverted)):
            self.xList3.append(self.convert_x_into_real_data_3())
        self.dataCH3 = yconverted

    def save_status(self):
        worker1 = Worker(self.calcul_graph1)
        worker2 = Worker(self.calcul_graph2, self.surface)
        worker3 = Worker(self.calcul_graph3, self.cycles, self.surface, )
        worker4 = Worker(self.calcul_graph4)
        worker5 = Worker(self.calcul_graph5)
        worker6 = Worker(self.calcul_graph6)

        worker1.signals.finished.connect(self.calcul_to_true1)
        worker2.signals.finished.connect(self.calcul_to_true2)
        worker3.signals.finished.connect(self.calcul_to_true3)
        worker4.signals.finished.connect(self.calcul_to_true4)
        worker5.signals.finished.connect(self.calcul_to_true5)
        worker6.signals.finished.connect(self.calcul_to_true6)

        self.threadpool.start(worker1)
        self.threadpool.start(worker2)
        self.threadpool.start(worker3)
        self.threadpool.start(worker4)
        self.threadpool.start(worker5)
        self.threadpool.start(worker6)

        for x1 in self.cycles:
            x2 = x1 + 1
            self.falsevcc += max(self.dataCH1[self.t2*x1:self.t2*x2])-min(self.dataCH1[self.t2*x1:self.t2*x2])
        self.vcc = self.falsevcc/self.cycles

    def calcul_graph1(self, progress_callback):
        self.savedStatusDataDict["Voltage"]["data"]["x"].extend(self.xList1)
        self.savedStatusDataDict["Voltage"]["data"]["y"].extend(self.dataCH1)
        log.debug("calcul 1")

    def calcul_graph2(self, surface, progress_callback):
        ptlist = self.frequency * np.trapz(self.dataCH1, x=self.dataCH2) / surface
        self.savedStatusDataDict["Power (m)"]["data"]["x"].append(self.x2)
        self.savedStatusDataDict["Power (m)"]["data"]["y"].append(ptlist)
        log.debug("calcul 2")

    def calcul_graph3(self, cycles, surface, progress_callback):
        log.info(len(self.dataCH1))
        log.info(len(self.dataCH2))
        ptlist = self.frequency * np.trapz(self.dataCH1, x=self.dataCH2) / (surface * cycles)
        self.savedStatusDataDict["Power (t)"]["data"]["x"].append(self.x3)
        self.savedStatusDataDict["Power (t)"]["data"]["y"].append(ptlist)
        log.debug("calcul 3")

    #def calcul_graph4(self, progress_callback):
     #   semi2 = self.dataCH2[:int((len(self.dataCH2) / 2))]
      #  semi2len = len(semi2)
       # self.t2 = int((semi2len/self.cycles))
        #print(semi2len+(self.t2*2))
        #print(-(semi2len+self.t2))
        #datach2T = self.dataCH2[-(semi2len+(self.t2*2)):-(semi2len+self.t2)]
        #datach1T = self.dataCH1[-(semi2len+(self.t2*2)):-(semi2len+self.t2)]
        #self.savedStatusDataDict["Lissajous"]["data"]["y"] = datach2T
        #self.savedStatusDataDict["Lissajous"]["data"]["x"] = datach1T
        #log.debug("calcul 4")

    def calcul_graph4(self, progress_callback):
        self.savedStatusDataDict["Lissajous asymetria"]["data"]["y"] = (self.dataCH2)
        self.savedStatusDataDict["Lissajous asymetria"]["data"]["x"] = (self.dataCH1)
        log.debug("calcul 5")

    def calcul_graph5(self, progress_callback):
        self.savedStatusDataDict["Lissajous asymetria"]["data"]["y"] = (self.dataCH2)
        self.savedStatusDataDict["Lissajous asymetria"]["data"]["x"] = (self.dataCH1)
        log.debug("calcul 5")

    def calcul_graph6(self, progress_callback):
        self.savedStatusDataDict["Charge asymetria"]["data"]["x"].extend(self.xList2)
        self.savedStatusDataDict["Charge asymetria"]["data"]["y"].extend(self.dataCH2)
        log.debug("calcul 6")
