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
from operator import methodcaller
import re

log = logging.getLogger(__name__)

SIGNAL_PLOT_TOGGLED = "plot.toggled.graphic"

class PlasmaAnalyser(QObject):
    #s_data_changed = pyqtSignal(dict, list, int)
    s_data_changed = pyqtSignal(dict)
    instruments_connected = pyqtSignal(list)

    def __init__(self):
        super(PlasmaAnalyser, self).__init__()
        self.threadpool = QThreadPool()
        self.rm = visa.ResourceManager()
        self.mutex = QMutex()
        self.savedStatusDataDict = {}
        self.create_empty_savedStatusDataDict()
        self.connect_to_signals()
        self.instrumentsDict = {"myOscillo": None, "myAFG": None}
        self.xList = []
        self.surface = 0
        self.x1, self.x2, self.x3 = -1, -1, -1
        self.timeList = []
        self.xList1 = []
        self.xList2 = []
        self.xList3 = []

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
        #print(f"HORizontal:RECOrdlength {nbData}")
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
            self.savedStatusDataDict[graphic]["data"] = {"x":[], "y":[]}
        # print(self.savedStatusDataDict)

    def connect_to_signals(self):
        pass

    def send_data_to_plot(self, graphics=None):
        #self.s_data_changed.emit(self.savedStatusDataDict, self.dataCH1, self.frequency)
        self.max1 = max(self.dataCH1)
        self.min1 = min(self.dataCH1)
        #voltageCurrentPhaseShift = self.xList1[self.dataCH1.index(max(self.dataCH1[:self.nbData/self.cycles]))] - self.xList3[self.dataCH3.index(max(self.dataCH3[:self.nbData/self.cycles]))]
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
        self.xList1.clear(), self.xList2.clear(), self.xList3.clear()
        self.x1 = 0
        self.x2 = 0
        self.x3 = 0
        self.send_data_to_plot()
        log.info("=== === === SIMULATION RESETED === === ===")

    def get_data_thread(self):
        self.nbData = int(self.instrumentsDict["myOscillo"].query("HORizontal:RECOrdlength?"))
        self.instrumentsDict["myOscillo"].write("HORizontal:SCAle 1E-3")
        #self.instrumentsDict["myOscillo"].write(f"WFMOutpre: NR_Pt {str(self.nbData)}")
        self.instrumentsDict["myOscillo"].write("HORizontal:DELay:MODe OFF")
        self.instrumentsDict["myOscillo"].write("HORizontal:POSition 0")
        self.frequency = float(self.instrumentsDict["myAFG"].query(":SOURCE:FREQUENCY?"))
        self.cycles = float(self.instrumentsDict["myAFG"].query("SOURce1:BURSt:NCYCles?"))
        #self.instrumentsDict["myOscillo"].write("ACQuire:STOPAfter SEQuence")


        self.instrumentsDict["myOscillo"].write(f":DATa:ENCdg ASCIi;:DATa:SOURce CH1")
        self.instrumentsDict["myOscillo"].write("ACQuire:STATE OFF")
        #self.instrumentsDict["myOscillo"].write(":DATa:STARt 1")
        #self.instrumentsDict["myOscillo"].write(f":DATa:STOP {str(self.nbData)}")
        self.x1zero = float(self.instrumentsDict["myOscillo"].query(":WFMOutpre:XZEro?"))
        self.x1incr = float(self.instrumentsDict["myOscillo"].query(":WFMOutpre:XINcr?"))
        self.y1zero = float(self.instrumentsDict["myOscillo"].query(":WFMOutpre:YZEro?"))
        self.y1mult = float(self.instrumentsDict["myOscillo"].query(":WFMOutpre:YMUlt?"))
        self.dataCH1 = self.instrumentsDict["myOscillo"].query("CURVe?")
        print(len(self.dataCH1))


        self.instrumentsDict["myOscillo"].write(f"DATa:SOURce CH2")
        #self.instrumentsDict["myOscillo"].write(":DATa:STARt 1")
        #self.instrumentsDict["myOscillo"].write(f":DATa:STOP {str(self.nbData)}")
        self.x2zero = float(self.instrumentsDict["myOscillo"].query(":WFMOutpre:XZEro?"))
        self.x2incr = float(self.instrumentsDict["myOscillo"].query(":WFMOutpre:XINcr?"))
        self.y2zero = float(self.instrumentsDict["myOscillo"].query(":WFMOutpre:YZEro?"))
        self.y2mult = float(self.instrumentsDict["myOscillo"].query(":WFMOutpre:YMUlt?"))
        self.dataCH2 = self.instrumentsDict["myOscillo"].query("CURVe?")
        print(len(self.dataCH2))


        #self.instrumentsDict["myOscillo"].write(f"DATa:SOURce CH3")
        #self.instrumentsDict["myOscillo"].write(":DATa:STARt 1")
        #self.instrumentsDict["myOscillo"].write(f":DATa:STOP {str(self.nbData)}")
        #self.x3zero = float(self.instrumentsDict["myOscillo"].query(":WFMOutpre:XZEro?"))
        #self.x3incr = float(self.instrumentsDict["myOscillo"].query(":WFMOutpre:XINcr?"))
        #self.y3zero = float(self.instrumentsDict["myOscillo"].query(":WFMOutpre:YZEro?"))
        #self.y3mult = float(self.instrumentsDict["myOscillo"].query(":WFMOutpre:YMUlt?"))
        #self.dataCH3 = self.instrumentsDict["myOscillo"].query("CURVe?")

        self.instrumentsDict["myOscillo"].write("ACQuire:STATE ON")

        workerch1 = Worker(self.convert_strlist_to_intlist1, self.dataCH1)
        workerch2 = Worker(self.convert_strlist_to_intlist2, self.dataCH2)
        #workerch3 = Worker(self.convert_strlist_to_intlist3, self.dataCH3)
        self.threadpool.start(workerch1)
        self.threadpool.start(workerch2)
        #self.threadpool.start(workerch3)


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
        yconverted = list(map(self.convert_y_into_real_data_1, list(map(int, (re.split("\n|, ", string)[0].split(","))))))
        for x in range(len(yconverted)):
            self.xList1.append(self.convert_x_into_real_data_1())
        self.dataCH1 = yconverted
        self.ch1list = yconverted
        #log.info(self.dataCH1)
        #log.info(self.xList1)

    def convert_strlist_to_intlist2(self, string, progress_callback):
        yconverted = list(map(self.convert_y_into_real_data_2, list(map(int, (re.split("\n|, ", string)[0].split(","))))))
        for x in range(len(yconverted)):
            self.xList2.append(self.convert_x_into_real_data_2())
        self.dataCH2 = yconverted

    def convert_strlist_to_intlist3(self, string, progress_callback):
        yconverted = map(self.convert_y_into_real_data_3, list(map(int, list(string.split(",")))))
        xconverted = map(self.convert_x_into_real_data_3, list(range(0, yconverted)))
        self.dataCH3 = yconverted
        self.xList3 = xconverted

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
        self.savedStatusDataDict["Voltage"]["data"]["x"].extend(self.xList1)
        self.savedStatusDataDict["Voltage"]["data"]["y"].extend(self.dataCH1)
        print("calcul 1")

    def calcul_graph2(self, surface, progress_callback):
        ptlist = self.frequency * np.trapz(self.dataCH1, x=self.dataCH2) / surface
        self.savedStatusDataDict["Power (m)"]["data"]["x"].append(self.x2)
        self.savedStatusDataDict["Power (m)"]["data"]["y"].append(ptlist)
        print("calcul 2")

    def calcul_graph3(self, cycles, surface, progress_callback):
        #log.info(self.dataCH1)
        #log.info(self.dataCH2)
        log.info(len(self.dataCH1))
        log.info(len(self.dataCH2))
        ptlist = self.frequency * np.trapz(self.dataCH1, x=self.dataCH2) / (surface * cycles)
        self.savedStatusDataDict["Power (t)"]["data"]["x"].append(self.x3)
        self.savedStatusDataDict["Power (t)"]["data"]["y"].append(ptlist)
        print("calcul 3")

    def calcul_graph4(self, progress_callback):
        self.savedStatusDataDict["Lissajous"]["data"]["y"].extend(self.dataCH2)
        self.savedStatusDataDict["Lissajous"]["data"]["x"].extend(self.dataCH1)
        print("calcul 4")

    def calcul_graph5(self, progress_callback):
        self.savedStatusDataDict["Lissajous asymetria"]["data"]["y"].extend(self.dataCH2)
        self.savedStatusDataDict["Lissajous asymetria"]["data"]["x"].extend(self.dataCH1)
        print("calcul 5")

    def calcul_graph6(self, progress_callback):
        self.savedStatusDataDict["Charge asymetria"]["data"]["x"].extend(self.xList2)
        self.savedStatusDataDict["Charge asymetria"]["data"]["y"].extend(self.dataCH2)
        print("calcul 6")
