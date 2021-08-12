import random
import time
import math
import numpy as np
import matplotlib.pyplot as plt
import json
from tools.pyqtWorker import Worker
from PyQt5.QtCore import pyqtSignal, QObject, QThreadPool, QMutex
import datetime
import logging
from pydispatch import dispatcher
from Data import Data
import pyvisa as visa
from scipy import integrate

log = logging.getLogger(__name__)

SIGNAL_PLOT_TOGGLED = "plot.toggled.graphic"

class PlasmaAnalyser(QObject):
    #s_data_changed = pyqtSignal(dict, list, int)
    s_data_changed = pyqtSignal(dict)
    instruments_connected = pyqtSignal(list)

    def __init__(self):
        super(PlasmaAnalyser, self).__init__()
        self.newX1, self.newY1, self.newX2, self.newY2 = -1, -1, -1, -1
        self.threadpool = QThreadPool()
        self.rm = visa.ResourceManager()
        self.mutex = QMutex()
        self.savedStatusDataDict = {}
        self.create_empty_savedStatusDataDict()
        self.connect_to_signals()
        self.instrumentsDict = {"myOscillo": None, "myAFG": None}
        self.xList = []
        self.surface = 0
        self.x1, self.x2, self.x3, self.x4, self.x5, self.x6 = -1
        self.timeList = []

    def new_resource_manager(self):
        log.info("New Resource Manager")
        self.rm.close()
        self.rm = visa.ResourceManager()

    def connect_oscillo(self, oscilloStr):
        log.info("Connection to instruments")
        self.instrumentsDict["myOscillo"] = self.rm.open_resource(oscilloStr)
        print(self.instrumentsDict["myOscillo"])

    def connect_afg(self, afgStr):
        log.info("Connection to instruments")
        self.instrumentsDict["myAFG"] = self.rm.open_resource(afgStr)
        print(self.instrumentsDict["myAFG"])

    def inject_AFG(self, mode, freq, wave, cycle):
        self.instrumentsDict["myAFG"].write(f"SOURce1:{mode}:MODE")
        self.instrumentsDict["myAFG"].write(f":SOURCE:FREQUENCY {freq}KHZ")
        self.instrumentsDict["myAFG"].write(f"SOURce1:FUNCtion:{wave}")
        if cycle != 0:
            self.instrumentsDict["myAFG"].write(f"SOURce1:BURSt:NCYCles {cycle}")

    def inject_Oscillo(self, nbData):
        print(f"HORizontal:RECOrdlength {nbData}")
        self.instrumentsDict["myOscillo"].write(f"HORizontal:RECOrdlength {nbData}")

    def change_surface_and_trigInt(self, surface, trigInt):
        self.surface = float(surface)
        self.trigInterval = trigInt

    def get_oscillo(self):
        return self.self.instrumentsDict["myOscillo"]

    def get_afg(self):
        return self.self.instrumentsDict["myAFG"]

    def create_empty_savedStatusDataDict(self):
        for graphic in Data().graphics:
            self.savedStatusDataDict[graphic] = {}
            self.savedStatusDataDict[graphic]["data"] = {"x":[], "y":[]}
        # print(self.savedStatusDataDict)

    def connect_to_signals(self):
        pass

    def send_data_to_plot(self, graphics=None):
        #self.s_data_changed.emit(self.savedStatusDataDict, self.dataCH1, self.frequency)
        self.s_data_changed.emit(self.savedStatusDataDict)
        log.info("sending data")

    def launch_propagation(self, progress_callback):
        self.launch_state = True
        log.info("=== === === SIMULATION STARTED === === ===")
        while self.launch_state is True:
            self.get_data_thread()
            self.mutex.lock()
            self.mutex.unlock()
            self.save_status()
            self.mutex.lock()
            self.mutex.unlock()
            self.send_data_to_plot()
            time.sleep(2)

    def stop_propagation(self, progress_callback):
        self.launch_state = False
        log.info("=== === === SIMULATION STOPPED === === ===")

    def reset_save_status(self, progress_callback):
        self.create_empty_savedStatusDataDict()
        self.send_data_to_plot()
        log.info("=== === === SIMULATION RESETED === === ===")

    def get_data_thread(self):
        self.timeDivision = float(self.instrumentsDict["myOscillo"].query("HORizontal:SCAle?")[-10:])
        self.nbData = int(self.instrumentsDict["myOscillo"].query("HORizontal:RECOrdlength?"))
        self.frequency = float(self.instrumentsDict["myAFG"].query(":SOURCE:FREQUENCY?"))
        self.cycles = float(self.instrumentsDict["myAFG"].query("SOURce1:BURSt:NCYCles?"))


        self.instrumentsDict["myOscillo"].write(":DATa:ENCdg ASCIi;:DATa:SOURce CH1")
        self.x1zero = self.instrumentsDict["myOscillo"].query(":WFMOutpre:XZEro?")
        self.x1incr = self.instrumentsDict["myOscillo"].query(":WFMOutpre:XINcr?")
        self.y1zero = self.instrumentsDict["myOscillo"].query(":WFMOutpre:YZEro?")
        self.y1mult = self.instrumentsDict["myOscillo"].query(":WFMOutpre:YMUlt?")
        self.dataCH1 = self.instrumentsDict["myOscillo"].query("CURVe?")


        self.instrumentsDict["myOscillo"].write("DATa:SOURce CH2")
        self.x2zero = self.instrumentsDict["myOscillo"].query(":WFMOutpre:XZEro?")
        self.x2incr = self.instrumentsDict["myOscillo"].query(":WFMOutpre:XINcr?")
        self.y2zero = self.instrumentsDict["myOscillo"].query(":WFMOutpre:YZEro?")
        self.y2mult = self.instrumentsDict["myOscillo"].query(":WFMOutpre:YMUlt?")
        self.dataCH2 = self.instrumentsDict["myOscillo"].query("CURVe?")


        self.instrumentsDict["myOscillo"].write("DATa:SOURce CH3")
        self.x3zero = self.instrumentsDict["myOscillo"].query(":WFMOutpre:XZEro?")
        self.x3incr = self.instrumentsDict["myOscillo"].query(":WFMOutpre:XINcr?")
        self.y3zero = self.instrumentsDict["myOscillo"].query(":WFMOutpre:YZEro?")
        self.y3mult = self.instrumentsDict["myOscillo"].query(":WFMOutpre:YMUlt?")
        self.dataCH3 = self.instrumentsDict["myOscillo"].query("CURVe?")

        workerch1 = Worker(self.convert_strlist_to_intlist1, self.dataCH1)
        workerch2 = Worker(self.convert_strlist_to_intlist2, self.dataCH2)
        workerch3 = Worker(self.convert_strlist_to_intlist3, self.dataCH3)
        self.threadpool.start(workerch1)
        self.threadpool.start(workerch2)
        self.threadpool.start(workerch3)

    def convert_into_real_data(self, data)
        data = data*

    def convert_strlist_to_intlist1(self, string, progress_callback):
        converted = list(map(int, list(string.split(","))))
        for i, x in enumerate(converted):
            converted[i] = self.y1zero + (self.y1mult*x)
        self.dataCH1 = converted
        #log.info(self.dataCH1)
        #print(len(self.dataCH1))
        #print(type(self.dataCH1))

    def convert_strlist_to_intlist2(self, string, progress_callback):
        converted = list(map(int, list(string.split(","))))
        self.dataCH2 = converted

    def convert_strlist_to_intlist3(self, string, progress_callback):
        converted = list(map(int, list(string.split(","))))
        self.dataCH3 = converted

    def save_status(self):
        worker1 = Worker(self.calcul_graph1)
        worker2 = Worker(self.calcul_graph2, self.surface)
        worker3 = Worker(self.calcul_graph3, self.cycles, self.surface, )
        worker4 = Worker(self.calcul_graph4)
        worker5 = Worker(self.calcul_graph5)
        worker6 = Worker(self.calcul_graph6)

        self.threadpool.start(worker1)
        self.threadpool.start(worker2)
        self.threadpool.start(worker3)
        self.threadpool.start(worker4)
        self.threadpool.start(worker5)
        self.threadpool.start(worker6)

    def calcul_graph1(self, progress_callback):
        self.savedStatusDataDict["Voltage"]["data"]["x"].extend(self.x1)
        self.savedStatusDataDict["Voltage"]["data"]["y"].extend(self.dataCH1)

    def calcul_graph2(self, surface, progress_callback):
        self.x2 +=1
        ptlist = self.frequency * np.trapz(self.dataCH1, x=self.dataCH2) / surface
        self.savedStatusDataDict["Power (m)"]["data"]["x"].append(self.x2)
        self.savedStatusDataDict["Power (m)"]["data"]["y"].append(ptlist)

    def calcul_graph3(self, cycles, surface, progress_callback):
        self.x3 += 1
        ptlist = self.frequency * np.trapz(self.dataCH1, x=self.dataCH2) / (surface * cycles)
        self.savedStatusDataDict["Power (t)"]["data"]["x"].append(self.x3)
        self.savedStatusDataDict["Power (t)"]["data"]["y"].append(ptlist)
        print("calcul 3")

    def calcul_graph4(self, progress_callback):
        self.x4 += 1
        self.savedStatusDataDict["Lissajous"]["data"]["x"].extend(self.dataCH2)
        self.savedStatusDataDict["Lissajous"]["data"]["y"].extend(self.dataCH1)
        print("calcul 4")

    def calcul_graph5(self, progress_callback):
        self.x5 += 1
        self.savedStatusDataDict["Lissajous asymetria"]["data"]["x"].extend(self.dataCH2)
        self.savedStatusDataDict["Lissajous asymetria"]["data"]["y"].extend(self.dataCH3)

    def calcul_graph6(self, progress_callback):
        self.x6 += 1
        self.savedStatusDataDict["Charge asymetria"]["data"]["x"].extend(self.dataCH2)
        self.savedStatusDataDict["Charge asymetria"]["data"]["y"].extend(self.dataCH3)

