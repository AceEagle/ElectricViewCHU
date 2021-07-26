import random
import time
import math
import numpy as np
import matplotlib.pyplot as plt
import json
from tools.pyqtWorker import Worker
from PyQt5.QtCore import pyqtSignal, QObject, QThreadPool
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
        self.savedStatusDataDict = {}
        self.create_empty_savedStatusDataDict()
        self.connect_to_signals()
        self.myOscillo = None
        self.myAFG = None
        self.xList = []
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
        #dispatcher.connect(self.handle_plot_toggled, signal=SIGNAL_PLOT_TOGGLED)
        pass

    def simulate_from_gui(self, *args, **kwargs):
        self.create_population(args[0])
        self.initialize_infection(nbOfInfected=args[1])
        self.launch_propagation(args[2])

    def plot_results(self, graphic):
        fig, ax1 = plt.subplots(figsize=(4, 4))
        xdata = range(len(self.savedStatusDataDict))

        for ageKey in self.savedStatusDataDict[0].keys():
            data2plot = []
            for dayKey in self.savedStatusDataDict.keys():
                data2plot.append(self.savedStatusDataDict[int(dayKey)][ageKey][graphic])
            ax1.plot(xdata, data2plot, label=ageKey)

        ax1.legend()
        plt.show()

    def send_data_to_plot(self, graphics=None):
        self.s_data_changed.emit(self.savedStatusDataDict)

    def launch_propagation(self, progress_callback):
        self.launch_state = True
        while self.launch_state is True:
            self.get_data()
            self.save_status()
            time.sleep(1)
            self.send_data_to_plot()

        log.info("=== === === SIMULATION COMPLETE === === ===")

    def stop_propagation(self, progress_callback):
        self.launch_state = False

    def reset_save_status(self, progress_callback):
        self.create_empty_savedStatusDataDict()
        self.send_data_to_plot()

    def get_data(self):
        self.timeDivision = float(self.myOscillo.query("HORizontal:SCAle?")[-10:])
        self.nbData = int(self.myOscillo.query("HORizontal:RECOrdlength?")[25:])
        for i in range(self.nbData):
            self.xList.append(i)
        self.myOscillo.write("DATa:SOURce CH1")
        self.dataCH1 = self.myOscillo.query("CURVe?")
        self.myOscillo.write("DATa:SOURce CH2")
        self.dataCH2 = self.myOscillo.query("CURVe?")
        self.myOscillo.write("DATa:SOURce CH3")
        self.dataCH3 = self.myOscillo.query("CURVe?")
        #self.myOscillo.write("DATa:SOURce CH4")
        #self.dataCH4 = self.myOscillo.query("CURVe?")

    def save_status(self):
        worker1 = Worker(self.calcul_graph1)
        worker2 = Worker(self.calcul_graph2)
        worker3 = Worker(self.calcul_graph3)
        worker4 = Worker(self.calcul_graph4)
        worker5 = Worker(self.calcul_graph5)
        worker6 = Worker(self.calcul_graph6)

        self.threadpool.start(worker1)
        self.threadpool.start(worker2)
        self.threadpool.start(worker3)
        self.threadpool.start(worker4)
        self.threadpool.start(worker5)
        self.threadpool.start(worker6)
        self.threadNb = self.threadpool.activeThreadCount()
        #for graphic in Data().graphics:
         #   self.savedStatusDataDict[graphic]["data"]["x"].append(self.day)
          #  self.savedStatusDataDict[graphic]["data"]["y"].append (
           #     sum(p.graphics[graphic] == 1 and p.tag == ageKey for p in self.population))

    def calcul_graph1(self, progress_callback):
        self.savedStatusDataDict["Tension"]["data"]["x"].append(self.xList)
        self.savedStatusDataDict["Tension"]["data"]["y"].append(self.dataCH1)

    def calcul_graph2(self, progress_callback):
        self.savedStatusDataDict["Puissance (Full)"]["data"]["x"].append(self.xList)
        self.savedStatusDataDict["Puissance (Full)"]["data"]["y"].append(math.sin(self.dataCH2))

    def calcul_graph3(self, progress_callback):
        self.savedStatusDataDict["Puissance (1t)"]["data"]["x"].append(self.xList)
        self.savedStatusDataDict["Puissance (1t)"]["data"]["y"].append(self.dataCH3)

    def calcul_graph4(self, progress_callback):
        self.savedStatusDataDict["Lissajoue"]["data"]["x"].append(self.dataCH1)
        self.savedStatusDataDict["Lissajoue"]["data"]["y"].append(self.dataCH2)

    def calcul_graph5(self, progress_callback):
        self.savedStatusDataDict["graph5"]["data"]["x"].append(self.xList)
        self.savedStatusDataDict["graph5"]["data"]["y"].append(self.dataCH1)

    def calcul_graph6(self, progress_callback):
        self.savedStatusDataDict["graph6"]["data"]["x"].append(self.xList)
        self.savedStatusDataDict["graph6"]["data"]["y"].append(self.dataCH1)
