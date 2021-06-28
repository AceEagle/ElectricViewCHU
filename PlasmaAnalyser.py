import random
import numpy as np
import matplotlib.pyplot as plt
import json
from PyQt5.QtCore import pyqtSignal, QObject
import datetime
import logging
from pydispatch import dispatcher
from Data import Data

log = logging.getLogger(__name__)

SIGNAL_PLOT_TOGGLED = "plot.toggled.indicator"

class PlasmaAnalyser(QObject):
    s_data_changed = pyqtSignal(dict)

    def __init__(self):
        super(PlasmaAnalyser, self).__init__()
        self.timeNow = 0
        self.timePast = 0
        self.day = 0
        self.selectedIndicators = []
        self.population = []
        self.parameters = {}
        self.savedStatusDataDict = {}
        self.create_empty_savedStatusDataDict()
        self.data2plot = {}
        self.healthcareSystemLimit = 50000
        self.connect_to_signals()

    def create_empty_savedStatusDataDict(self):
        for indicator in Data().indicators:
            self.savedStatusDataDict[indicator] = {}
            for ageGroup in Data().ageGroupsList:
                self.savedStatusDataDict[indicator][ageGroup] = {"x":[], "y":[]}
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

    def plot_results(self, indicator):
        fig, ax1 = plt.subplots(figsize=(4, 4))
        xdata = range(len(self.savedStatusDataDict))

        for ageKey in self.savedStatusDataDict[0].keys():
            data2plot = []
            for dayKey in self.savedStatusDataDict.keys():
                data2plot.append(self.savedStatusDataDict[int(dayKey)][ageKey][indicator])
            ax1.plot(xdata, data2plot, label=ageKey)

        ax1.legend()
        plt.show()

    def send_data_to_plot(self, indicators=None):
        self.s_data_changed.emit(self.savedStatusDataDict)

    def launch_propagation(self, nbOfDays):
        for d in range(nbOfDays):
            self.day = d
            log.info("Simulation Day: {} on {} ({}%)".format(d, nbOfDays-1, d * 100 / nbOfDays-1))
            self.meet_people()
            log.info("DAY {} :: BEGIN SAVE STATUS".format(d))
            self.save_status()
            log.info("DAY {} :: END SAVE STATUS".format(d))
            self.send_data_to_plot()


        log.info("=== === === SIMULATION COMPLETE === === ===")

    def meet_people(self):
        log.info("DAY {} :: BEGIN INDEXING".format(self.day))
        personListIndex = [i if x.indicators["isInfected"] == 1 else -1 for i, x in enumerate(self.population)]
        personListIndex = list(filter((-1).__ne__, personListIndex))
        log.info("DAY {} :: END INDEXING".format(self.day))

        log.info("DAY {} :: BEGIN MEETING PERSONS".format(self.day))
        liste = [self.population[i] for i in personListIndex]
        for person in liste:
            person.update_own_status()
            if person.indicators["isInfectious"]:
                for metPerson in range(int(person.parameters["knownEncounteredPerDay"])):
                    person.interact(random.choice(person.listOfRelatives))
        log.info("DAY {} :: END MEETING PERSONS".format(self.day))

    def save_status(self):
        """{"indicator":{"[0-9]":{"x":[], "y":[]}, "[10-19]":{"x"}:[], "y":[]}, ...}
        For it is   Dictionnary[Indicator][ageGroup]["x"] --> Days data
                    Dictionnary[Indicator][ageGroup]["y"] --> Number of case data
        """
        for indicator in Data().indicators:
            for ageKey in list(self.parameters.keys()):
                self.savedStatusDataDict[indicator][ageKey]["x"].append(self.day)
                self.savedStatusDataDict[indicator][ageKey]["y"].append (
                    sum(p.indicators[indicator] == 1 and p.tag == ageKey for p in self.population))

    def initialize_infection(self, nbOfInfected=1):
        try:
            indexes = random.choices(range(len(self.population)), k=nbOfInfected)
            for index in indexes:
                self.population[index].indicators["isInfected"] = 1
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

