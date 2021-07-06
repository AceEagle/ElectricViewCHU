import random
import numpy as np
import matplotlib.pyplot as plt
import json
from PyQt5.QtCore import pyqtSignal, QObject
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
        self.savedStatusDataDict = {}
        self.create_empty_savedStatusDataDict()
        self.connect_to_signals()
        self.myOscillo = None
        self.myAFG = None

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
            self.save_status()
            self.send_data_to_plot()

        log.info("=== === === SIMULATION COMPLETE === === ===")

    def stop_propagation(self):
        self.launch_state = False

    def reset_save_status(self):
        self.create_empty_savedStatusDataDict()

    def save_status(self):
        for graphic in Data().graphics:
            self.savedStatusDataDict[graphic]["data"]["x"].append(self.day)
            self.savedStatusDataDict[graphic]["data"]["y"].append (
                sum(p.graphics[graphic] == 1 and p.tag == ageKey for p in self.population))

