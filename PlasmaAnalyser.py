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
        self.timeNow = 0
        self.timePast = 0
        self.day = 0
        self.selectedgraphics = []
        self.population = []
        self.parameters = {}
        self.savedStatusDataDict = {}
        self.create_empty_savedStatusDataDict()
        self.data2plot = {}
        self.healthcareSystemLimit = 50000
        self.connect_to_signals()
        self.rm = visa.ResourceManager()

    def connect_AFG_and_Oscillo(self, AFGStr, OscilloStr):
        self.myOscillo = self.rm.open_resource(OscilloStr)
        self.myAFG = self.rm.open_resource(AFGStr)
        self.instrumentsList = [self.myAFG, self.myOscillo]
        return self.myAFG, self.myOscillo


    def create_empty_savedStatusDataDict(self):
        for graphic in Data().graphics:
            self.savedStatusDataDict[graphic] = {}
            self.savedStatusDataDict[graphic]["data"] = {"x":[], "y":[]}
        # print(self.savedStatusDataDict)

    def connect_to_signals(self):
        dispatcher.connect(self.handle_plot_toggled, signal=SIGNAL_PLOT_TOGGLED)

    def simulate_from_gui(self, *args, **kwargs):
        self.create_population(args[0])
        self.initialize_infection(nbOfInfected=args[1])
        self.launch_propagation(args[2])

    def simulate(self, amount, time, parameters=None):
        self.create_population(amount, parameters)
        self.initialize_infection(nbOfInfected=1)
        self.launch_propagation(time)

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

    def start_propagation(self):
        self.launch_propagation_state = True
        self.propagation()

    def stop_propagation(self):
        self.launch_propagation_state = False

    def propagation(self):
        while self.launch_propagation_state is True:
            self.get_data()
            self.filter_data()
            self.send_data_to_plot()


        log.info("=== === === SIMULATION COMPLETE === === ===")

    def get_data(self):
        pass

    def filter_data(self):
        pass

    def save_status(self):
        """{"graphic":{"[0-9]":{"x":[], "y":[]}, "[10-19]":{"x"}:[], "y":[]}, ...}
        For it is   Dictionnary[graphic][ageGroup]["x"] --> Days data
                    Dictionnary[graphic][ageGroup]["y"] --> Number of case data
        """
        for graphic in Data().graphics:
            for ageKey in list(self.parameters.keys()):
                self.savedStatusDataDict[graphic][ageKey]["x"].append(self.day)
                self.savedStatusDataDict[graphic][ageKey]["y"].append (
                    sum(p.graphics[graphic] == 1 and p.tag == ageKey for p in self.population))

    def initialize_infection(self, nbOfInfected=1):
        try:
            indexes = random.choices(range(len(self.population)), k=nbOfInfected)
            for index in indexes:
                self.population[index].graphics["isInfected"] = 1
        except Exception as e:
            log.error(e)

    def create_population(self, amountOfPeople, parameters=None):
        if parameters is not None:
            self.parameters = parameters

        id = 0
        for i, key in enumerate(self.parameters.keys()):
            for j in range(int(amountOfPeople * self.parameters[key]["percentageOfPopulation"])):
                randomizedParameters = self.give_gaussian_parameters(self.parameters[key])
                self.population.append(Data(randomizedParameters, tag=key, id=id))
                id += 1
            log.info("Creating Population...{}/{}".format(i, len(self.parameters.keys())))
        random.shuffle(self.population)
        log.info("Done.")
        log.info("Randomizing Relationships...")
        for person in self.population:
            person.select_relatives(self.population, 50)
        log.info("Done.")
        return self.population

    def load_json_parameters(self, jsonFilePath):
        with open(jsonFilePath) as f:
            parametersFile = json.load(f)
        self.parameters = parametersFile[0]
        return self.parameters

