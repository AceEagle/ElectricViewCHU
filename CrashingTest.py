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
import random


newX1, newY1, newX2, newY2 = -1, -1, -1, -1
threadpool = QThreadPool()
rm = visa.ResourceManager()
mutex = QMutex()
savedStatusDataDict = {}
xList = []
timeList = []
randomlist1 = []
randomlist2 = []
randomlist3 = []

for i in range(0,1000000):
    n = random.randint(-100, 100)
    randomlist1.append(n)
    n = random.randint(-100, 100)
    randomlist2.append(n)
    n = random.randint(-100, 100)
    randomlist3.append(n)


def create_empty_savedStatusDataDict():
    for graphic in Data().graphics:
        savedStatusDataDict[graphic] = {}
        savedStatusDataDict[graphic]["data"] = {"x": [], "y": []}
    # print(savedStatusDataDict)


def plot_results(graphic):
    fig, ax1 = plt.subplots(figsize=(4, 4))
    xdata = range(len(savedStatusDataDict))

    for ageKey in savedStatusDataDict[0].keys():
        data2plot = []
        for dayKey in savedStatusDataDict.keys():
            data2plot.append(savedStatusDataDict[int(dayKey)][ageKey][graphic])
        ax1.plot(xdata, data2plot, label=ageKey)

    ax1.legend()
    plt.show()


def send_data_to_plot():
    print(savedStatusDataDict["Lissajoue"]["data"]["y"])

def launch_propagation():
    launch_state = True
    while launch_state is True:
        get_data_thread()
        mutex.lock()
        mutex.unlock()
        save_status()
        mutex.lock()
        mutex.unlock()
        # time.sleep(3)
        send_data_to_plot()


def get_data_thread():
    #timeDivision = float(myOscillo.query("HORizontal:SCAle?")[-10:])
    nbData = 1000000
    for i in range(nbData):
        xList.append(i)

    workerch1 = Worker(convert_strlist_to_intlist1, randomlist1)
    workerch2 = Worker(convert_strlist_to_intlist2, randomlist2)
    workerch3 = Worker(convert_strlist_to_intlist3, randomlist3)
    threadpool.start(workerch1)
    threadpool.start(workerch2)
    threadpool.start(workerch3)
    workerch3.signals.finished.connect(save_status)


def convert_strlist_to_intlist1(string, progress_callback):
    #converted = list(map(int, list(string.split(","))))
    pass

def convert_strlist_to_intlist2(string, progress_callback):
    #converted = list(map(int, list(string.split(","))))
    #dataCH2 = converted
    pass


def convert_strlist_to_intlist3(string, progress_callback):
    #converted = list(map(int, list(string.split(","))))
    #dataCH3 = converted
    mutex.lock()
    pass
    mutex.unlock()


def save_status():
    worker1 = Worker(calcul_graph1)
    worker2 = Worker(calcul_graph2)
    worker3 = Worker(calcul_graph3)
    worker4 = Worker(calcul_graph4)
    # worker5 = Worker(calcul_graph5)
    # worker6 = Worker(calcul_graph6)

    threadpool.start(worker1)
    threadpool.start(worker2)
    threadpool.start(worker3)
    threadpool.start(worker4)
    worker4.signals.finished.connect(send_data_to_plot)
    # threadpool.start(worker5)
    # threadpool.start(worker6)
    # threadNb = threadpool.activeThreadCount()
    # for graphic in Data().graphics:
    #   savedStatusDataDict[graphic]["data"]["x"].append(day)
    #  savedStatusDataDict[graphic]["data"]["y"].append (
    #     sum(p.graphics[graphic] == 1 and p.tag == ageKey for p in population))


def calcul_graph1(progress_callback):
    savedStatusDataDict["Tension"]["data"]["x"].append(xList)
    savedStatusDataDict["Tension"]["data"]["y"].append(randomlist1)


def calcul_graph2(progress_callback):
    savedStatusDataDict["Puissance (Full)"]["data"]["x"].append(xList)
    savedStatusDataDict["Puissance (Full)"]["data"]["y"].append(randomlist2)


def calcul_graph3(progress_callback):
    savedStatusDataDict["Puissance (1t)"]["data"]["x"].append(xList)
    savedStatusDataDict["Puissance (1t)"]["data"]["y"].append(randomlist3)


def calcul_graph4(progress_callback):
    mutex.lock()
    savedStatusDataDict["Lissajoue"]["data"]["x"].append(randomlist1)
    savedStatusDataDict["Lissajoue"]["data"]["y"].append(randomlist2)
    mutex.unlock()

create_empty_savedStatusDataDict()
launch_propagation()