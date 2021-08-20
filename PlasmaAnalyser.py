import random
import time
import math
import numpy as np
import matplotlib.pyplot as plt
import json
from tools.threadWorker import Worker
from PyQt5.QtCore import pyqtSignal, QObject, QThreadPool, QMutex, QThread
import datetime
import logging
from pydispatch import dispatcher
from Data import Data
import pyvisa as visa
from scipy import integrate
from operator import methodcaller
import re

log = logging.getLogger(__name__)

SIGNAL_PLOT_TOGGLED = "plot.toggled.graphic"


class PlasmaAnalyser(QObject):
    # s_data_changed = pyqtSignal(dict, list, int)
    s_data_changed = pyqtSignal(dict)
    instruments_connected = pyqtSignal(list)

    def __init__(self):
        super(PlasmaAnalyser, self).__init__()

        self.rm = visa.ResourceManager()
        self.savedStatusDataDict = {}
        self.create_empty_savedStatusDataDict()
        self.connect_to_signals()
        self.instrumentsDict = {"myOscillo": None, "myAFG": None}
        self.xList = []
        self.x1, self.x2, self.x3 = 1, 1, 1
        self.dataTest = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.dataCH1, self.dataCH2, self.dataCH3 = None, None, None
        self.worker1finished, self.worker2finished, self.worker3finished = False, False, False
        self.calcul1finished, self.calcul2finished, self.calcul3finished, self.calcul4finished, self.calcul5finished, self.calcul6finished = False, False, False, False, False, False
        self.timeList, self.xList1, self.xList2, self.xList3 = [], [], [], []
        self.cycles = 1
        self.surface = 1
        self.frequency = 1

        self.create_threads()
        self.create_workers()
        self.connect_threads()

    def create_threads(self):
        self.qthreadch1 = QThread()
        self.qthreadch2 = QThread()
        self.qthreadch3 = QThread()

        self.qthreadcal1 = QThread()
        self.qthreadcal2 = QThread()
        self.qthreadcal3 = QThread()
        self.qthreadcal4 = QThread()
        self.qthreadcal5 = QThread()
        self.qthreadcal6 = QThread()

    def create_workers(self):
        self.workerch1 = Worker(self.convert_strlist_to_intlist1, self.dataTest)
        self.workerch2 = Worker(self.convert_strlist_to_intlist2, self.dataTest)
        self.workerch3 = Worker(self.convert_strlist_to_intlist3, self.dataTest)

        self.workercal1 = Worker(self.calcul_graph1)
        self.workercal2 = Worker(self.calcul_graph2, self.surface)
        self.workercal3 = Worker(self.calcul_graph3, self.cycles, self.surface, )
        self.workercal4 = Worker(self.calcul_graph4)
        self.workercal5 = Worker(self.calcul_graph5)
        self.workercal6 = Worker(self.calcul_graph6)

        self.workerch1.signals.finished.connect(self.thread_to_true1)
        self.workerch2.signals.finished.connect(self.thread_to_true2)
        self.workerch3.signals.finished.connect(self.thread_to_true3)

        self.workercal1.signals.finished.connect(self.calcul_to_true1)
        self.workercal2.signals.finished.connect(self.calcul_to_true2)
        self.workercal3.signals.finished.connect(self.calcul_to_true3)
        self.workercal4.signals.finished.connect(self.calcul_to_true4)
        self.workercal5.signals.finished.connect(self.calcul_to_true5)
        self.workercal6.signals.finished.connect(self.calcul_to_true6)

    def connect_threads(self):
        self.workerch1.moveToThread(self.qthreadch1)
        self.qthreadch1.started.connect(self.workerch1.run)

        self.workerch2.moveToThread(self.qthreadch2)
        self.qthreadch2.started.connect(self.workerch2.run)

        self.workerch3.moveToThread(self.qthreadch3)
        self.qthreadch3.started.connect(self.workerch3.run)

        self.workercal1.moveToThread(self.qthreadcal1)
        self.qthreadcal1.started.connect(self.workercal1.run)

        self.workercal2.moveToThread(self.qthreadcal2)
        self.qthreadcal2.started.connect(self.workercal2.run)

        self.workercal3.moveToThread(self.qthreadcal3)
        self.qthreadcal3.started.connect(self.workercal3.run)

        self.workercal4.moveToThread(self.qthreadcal4)
        self.qthreadcal4.started.connect(self.workercal4.run)

        self.workercal5.moveToThread(self.qthreadcal5)
        self.qthreadcal5.started.connect(self.workercal5.run)

        self.workercal6.moveToThread(self.qthreadcal6)
        self.qthreadcal6.started.connect(self.workercal6.run)

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
        log.info("Connection to oscillo")
        self.instrumentsDict["myOscillo"] = self.rm.open_resource(oscilloStr)
        log.debug(self.instrumentsDict["myOscillo"])

    def connect_afg(self, afgStr):
        log.info("Connection to afg")
        self.instrumentsDict["myAFG"] = self.rm.open_resource(afgStr)
        log.debug(self.instrumentsDict["myAFG"])

    def inject_AFG(self, mode, freq, wave, cycle):
        self.instrumentsDict["myAFG"].write(f"SOURce1:{mode}:MODE")
        self.instrumentsDict["myAFG"].write(f":SOURCE:FREQUENCY {freq}KHZ")
        self.instrumentsDict["myAFG"].write(f"SOURce1:FUNCtion:{wave}")
        if cycle != 0:
            self.instrumentsDict["myAFG"].write(f"SOURce1:BURSt:NCYCles {cycle}")

    def inject_Oscillo(self, nbData):
        # log.debug(f"HORizontal:RECOrdlength {nbData}")
        self.instrumentsDict["myOscillo"].write(f"HORizontal:RECOrdlength {nbData}")

    def change_surface_and_trigInt(self, surface, trigInt, capacitance):
        self.surface = float(surface)
        self.trigInterval = float(trigInt)
        self.capacitance = float(capacitance) * 1E-6

    def get_oscillo(self):
        return self.self.instrumentsDict["myOscillo"]

    def get_afg(self):
        return self.self.instrumentsDict["myAFG"]

    def create_empty_savedStatusDataDict(self):
        for graphic in Data().graphics:
            self.savedStatusDataDict[graphic] = {}
            self.savedStatusDataDict[graphic]["data"] = {"x": [], "y": []}
        # log.debug(self.savedStatusDataDict)

    def connect_to_signals(self):
        pass

    def send_data_to_plot(self, graphics=None):
        # self.s_data_changed.emit(self.savedStatusDataDict, self.dataCH1, self.frequency)
        #self.max1 = max(self.dataCH1)
        #self.min1 = min(self.dataCH1)
        # voltageCurrentPhaseShift = self.xList1[self.dataCH1.index(max(self.dataCH1[:self.nbData/self.cycles]))] - self.xList3[self.dataCH3.index(max(self.dataCH3[:self.nbData/self.cycles]))]
        log.debug(self.savedStatusDataDict["Voltage"]["data"]["y"])
        self.s_data_changed.emit(self.savedStatusDataDict)
        log.info("sending data to main thread")

    def launch_propagation(self, statusSignal):
        # self.init_oscillo()
        self.launch_state = True
        log.info("=== === === SIMULATION STARTED === === ===")
        while self.launch_state == True:
            self.get_data_thread()

    def init_oscillo(self):
        self.nbData = int(self.instrumentsDict["myOscillo"].query("HORizontal:RECOrdlength?"))
        self.instrumentsDict["myOscillo"].write("HORizontal:SCAle 1E-3")
        self.instrumentsDict["myOscillo"].write("HORizontal:DELay:MODe OFF")
        self.instrumentsDict["myOscillo"].write("HORizontal:POSition 0")
        self.frequency = float(self.instrumentsDict["myAFG"].query(":SOURCE:FREQUENCY?"))
        # log.debug(self.frequency)
        self.cycles = float(self.instrumentsDict["myAFG"].query("SOURce1:BURSt:NCYCles?"))
        # log.debug(self.cycles)

    def stop_propagation(self, statusSignal):
        self.launch_state = False
        log.info("=== === === SIMULATION STOPPED === === ===")

    def reset_save_status(self, statusSignal):
        self.create_empty_savedStatusDataDict()
        self.xList1.clear(), self.xList2.clear(), self.xList3.clear()
        self.x1 = 0
        self.x2 = 0
        self.x3 = 0
        self.send_data_to_plot()
        log.info("=== === === SIMULATION RESETED === === ===")

    def get_data_thread(self):
        self.surface = 28
        self.cycles = 50
        self.nbData = 10
        self.frequency = 10000
        # self.nbData = int(self.instrumentsDict["myOscillo"].query("HORizontal:RECOrdlength?"))
        # self.instrumentsDict["myOscillo"].write("HORizontal:SCAle 1E-3")
        # self.instrumentsDict["myOscillo"].write("HORizontal:DELay:MODe OFF")
        # self.instrumentsDict["myOscillo"].write("HORizontal:POSition 0")
        # self.frequency = float(self.instrumentsDict["myAFG"].query(":SOURCE:FREQUENCY?"))
        # self.cycles = float(self.instrumentsDict["myAFG"].query("SOURce1:BURSt:NCYCles?"))
        self.qthreadch1.start()
        self.qthreadch2.start()
        self.qthreadch3.start()

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
        log.debug("CalcultoTrue 1")
        self.wait_for_6threads()

    def calcul_to_true2(self):
        self.calcul2finished = True
        log.debug("CalcultoTrue 2")
        self.wait_for_6threads()

    def calcul_to_true3(self):
        self.calcul3finished = True
        log.debug("CalcultoTrue 3")
        self.wait_for_6threads()

    def calcul_to_true4(self):
        self.calcul4finished = True
        log.debug("CalcultoTrue 4")
        self.wait_for_6threads()

    def calcul_to_true5(self):
        self.calcul5finished = True
        log.debug("CalcultoTrue 5")
        self.wait_for_6threads()

    def calcul_to_true6(self):
        self.calcul6finished = True
        log.debug("CalcultoTrue 6")
        self.wait_for_6threads()

    def wait_for_6threads(self):
        if self.calcul1finished is True and self.calcul2finished is True and self.calcul3finished is True and self.calcul4finished is True and self.calcul5finished is True and self.calcul6finished is True:
            self.calcul1finished, self.calcul2finished, self.calcul3finished, self.calcul4finished, self.calcul5finished, self.calcul6finished = False, False, False, False, False, False
            self.send_data_to_plot()
        else:
            log.debug("pass wait for 6 calculsthreads")

    def wait_for_3threads(self):
        if self.worker1finished is True and self.worker2finished is True and self.worker3finished is True:
            self.worker1finished, self.worker2finished, self.worker3finished = False, False, False
            self.save_status()
        else:
            log.debug("pass wait for 3 channelthreads")

    def convert_x_into_real_data_1(self):
        self.x1 += 1
        return 2 + (2 * (self.x1 - 1))

    def convert_y_into_real_data_1(self, data):
        return 2 + (data * 2)

    def convert_x_into_real_data_2(self):
        self.x2 += 1
        return 2 + (2 * (self.x2 - 1))

    def convert_y_into_real_data_2(self, data):
        return 2 * (2 + (data * 2))

    def convert_x_into_real_data_3(self):
        self.x3 += 1
        return 2 + (2 * (self.x3 - 1))

    def convert_y_into_real_data_3(self, data):
        return 2 + (data * 2)

    def convert_strlist_to_intlist1(self, string, statusSignal):
        # yconverted = list(map(self.convert_y_into_real_data_1, list(map(int, (re.split("\n|, ", string)[0].split(","))))))
        # log.debug(yconverted)
        self.xList1 = []
        yconverted = list(map(self.convert_y_into_real_data_1, string))
        for x in range(len(yconverted)):
            self.xList1.append(self.convert_x_into_real_data_1())
        self.dataCH1 = yconverted
        # log.debug(len(self.dataCH1), len(self.xList1))
        # self.ch1List = yconverted
        # log.info(self.dataCH1)
        # log.info(self.xList1)
        log.debug("calculCH1")

    def convert_strlist_to_intlist2(self, string, statusSignal):
        # yconverted = list(map(self.convert_y_into_real_data_2, list(map(int, (re.split("\n|, ", string)[0].split(","))))))
        # log.debug(yconverted)
        # log.debug(yconverted)
        self.xList2 = []
        yconverted = list(map(self.convert_y_into_real_data_2, string))
        for x in range(len(yconverted)):
            self.xList2.append(self.convert_x_into_real_data_2())
        self.dataCH2 = yconverted
        log.debug("calculCH2")

    def convert_strlist_to_intlist3(self, string, statusSignal):
        self.xList3 = []
        yconverted = list(map(self.convert_y_into_real_data_3, string))
        for x in range(len(yconverted)):
            self.xList3.append(self.convert_x_into_real_data_3())
        self.dataCH3 = yconverted
        log.debug("calculCH3")

    def save_status(self):
        log.debug("save_status (after wait for 3 channelthread)")
        self.qthreadcal1.start()
        self.qthreadcal2.start()
        self.qthreadcal3.start()
        self.qthreadcal4.start()
        self.qthreadcal5.start()
        self.qthreadcal6.start()

    def calcul_graph1(self, statusSignal):
        self.savedStatusDataDict["Voltage"]["data"]["x"].extend(self.xList1)
        self.savedStatusDataDict["Voltage"]["data"]["y"].extend(self.dataCH1)
        log.debug("calcul 1")

    def calcul_graph2(self, surface, statusSignal):
        ptlist = self.frequency * np.trapz(self.dataCH1, x=self.dataCH2) / surface
        self.savedStatusDataDict["Power (m)"]["data"]["x"].append(self.x2)
        self.savedStatusDataDict["Power (m)"]["data"]["y"].append(ptlist)
        log.debug("calcul 2")

    def calcul_graph3(self, cycles, surface, statusSignal):
        # log.info(self.dataCH1)
        # log.info(self.dataCH2)
        #log.info(len(self.dataCH1))
        #log.info(len(self.dataCH2))
        ptlist = self.frequency * np.trapz(self.dataCH1, x=self.dataCH2) / (surface * cycles)
        self.savedStatusDataDict["Power (t)"]["data"]["x"].append(self.x3)
        self.savedStatusDataDict["Power (t)"]["data"]["y"].append(ptlist)
        log.debug("calcul 3")

    def calcul_graph4(self, statusSignal):
        self.savedStatusDataDict["Lissajous"]["data"]["y"].extend(self.dataCH2)
        self.savedStatusDataDict["Lissajous"]["data"]["x"].extend(self.dataCH1)
        log.debug("calcul 4")

    def calcul_graph5(self, statusSignal):
        self.savedStatusDataDict["Lissajous asymetria"]["data"]["y"].extend(self.dataCH2)
        self.savedStatusDataDict["Lissajous asymetria"]["data"]["x"].extend(self.dataCH1)
        log.debug("calcul 5")

    def calcul_graph6(self, statusSignal):
        self.savedStatusDataDict["Charge asymetria"]["data"]["x"].extend(self.xList2)
        self.savedStatusDataDict["Charge asymetria"]["data"]["y"].extend(self.dataCH2)
        log.debug("calcul 6")
