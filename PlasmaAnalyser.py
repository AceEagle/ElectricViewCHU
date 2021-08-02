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

log = logging.getLogger(__name__)

SIGNAL_PLOT_TOGGLED = "plot.toggled.graphic"

class PlasmaAnalyser(QObject):
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
        self.myOscillo = None
        self.myAFG = None
        self.xList = []
        for x in range(100000):
            self.xList.append(x)
        self.timeList = []

    def new_resource_manager(self):
        log.info("New Resource Manager")
        self.rm.close()
        self.rm = visa.ResourceManager()

    def connect_instruments(self, oscilloStr, afgStr, progress_callback):
        log.info("Connection to instruments")
        try:
            self.myOscillo = self.rm.open_resource(oscilloStr)
            self.myAFG = self.rm.open_resource(afgStr)
        except:
            pass

    def get_oscillo(self):
        return self.myOscillo

    def get_afg(self):
        return self.myAFG

    def create_empty_savedStatusDataDict(self):
        for graphic in Data().graphics:
            self.savedStatusDataDict[graphic] = {}
            self.savedStatusDataDict[graphic]["data"] = {"x":[], "y":[]}
        # print(self.savedStatusDataDict)

    def connect_to_signals(self):
        pass

    def send_data_to_plot(self, graphics=None):
        self.s_data_changed.emit(self.savedStatusDataDict)
        print("sending data")

    def launch_propagation(self, progress_callback):
        self.launch_state = True
        while self.launch_state is True:
            self.get_data_thread()
            self.mutex.lock()
            self.mutex.unlock()
            self.save_status()
            self.mutex.lock()
            self.mutex.unlock()
            #time.sleep(3)
            self.send_data_to_plot()

        log.info("=== === === SIMULATION COMPLETE === === ===")

    def stop_propagation(self, progress_callback):
        self.launch_state = False

    def reset_save_status(self, progress_callback):
        self.create_empty_savedStatusDataDict()
        self.send_data_to_plot()

    def get_data_thread(self):
        self.timeDivision = float(self.myOscillo.query("HORizontal:SCAle?")[-10:])
        self.nbData = int(self.myOscillo.query("HORizontal:RECOrdlength?"))
        self.myOscillo.write(":DATa:ENCdg ASCIi;:DATa:SOURce CH1")
        self.dataCH1 = self.myOscillo.query("CURVe?")
        self.myOscillo.write("DATa:SOURce CH2")
        self.dataCH2 = self.myOscillo.query("CURVe?")
        #self.myOscillo.write("DATa:SOURce CH3")
        #self.dataCH3 = self.myOscillo.query("CURVe?")

        workerch1 = Worker(self.convert_strlist_to_intlist1, self.dataCH1)
        workerch2 = Worker(self.convert_strlist_to_intlist2, self.dataCH2)
        #workerch3 = Worker(self.convert_strlist_to_intlist3, self.dataCH3)
        self.threadpool.start(workerch1)
        self.threadpool.start(workerch2)
        #self.threadpool.start(workerch3)

    def convert_strlist_to_intlist1(self, string, progress_callback):
        converted = list(map(int, list(string.split(","))))
        self.dataCH1 = converted
        #print(len(self.dataCH1))
        #print(type(self.dataCH1))

    def convert_strlist_to_intlist2(self, string, progress_callback):
        converted = list(map(int, list(string.split(","))))
        self.dataCH2 = converted

    def convert_strlist_to_intlist3(self, string, progress_callback):
        converted = list(map(int, list(string.split(","))))
        self.dataCH3 = converted

    def save_status(self):
        #worker1 = Worker(self.calcul_graph1)
        #worker2 = Worker(self.calcul_graph2)
        #worker3 = Worker(self.calcul_graph3)
        worker4 = Worker(self.calcul_graph4)
        #worker5 = Worker(self.calcul_graph5)
        #worker6 = Worker(self.calcul_graph6)

        #self.threadpool.start(worker1)
        #self.threadpool.start(worker2)
        #self.threadpool.start(worker3)
        self.threadpool.start(worker4)
        #self.threadpool.start(worker5)
        #self.threadpool.start(worker6)

    def calcul_graph1(self, progress_callback):
        self.savedStatusDataDict["Voltage"]["data"]["x"].extend(self.xList)
        self.savedStatusDataDict["Voltage"]["data"]["y"].extend(self.dataCH1)

    def calcul_graph2(self, progress_callback):
        self.savedStatusDataDict["Puissance (m)"]["data"]["x"].extend(self.xList)
        self.savedStatusDataDict["Puissance (m)"]["data"]["y"].extend(self.dataCH2)

    def calcul_graph3(self, progress_callback):
        self.savedStatusDataDict["Puissance (t)"]["data"]["x"].extend(self.xList)
        self.savedStatusDataDict["Puissance (t)"]["data"]["y"].extend(self.dataCH3)

    def calcul_graph4(self, progress_callback):
        self.savedStatusDataDict["Lissajous"]["data"]["x"].extend(self.dataCH1)
        self.savedStatusDataDict["Lissajous"]["data"]["y"].extend(self.dataCH2)
        print("calcul")
    def calcul_graph5(self, progress_callback):
        self.savedStatusDataDict["Lissajous asymetria"]["data"]["x"].extend(self.xList)
        self.savedStatusDataDict["Lissajous asymetria"]["data"]["y"].extend(self.dataCH1)

    def calcul_graph6(self, progress_callback):
        self.savedStatusDataDict["Voltage asymetria"]["data"]["x"].extend(self.xList)
        self.savedStatusDataDict["Voltage asymetria"]["data"]["y"].extend(self.dataCH1)

    def inject_AFG(self, mode, freq, wave, cycle, trigInt):
        pass

    def inject_Oscillo(self, nbData, trigLevel):
        pass

