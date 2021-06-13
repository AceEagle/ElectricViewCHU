from PyQt5.QtWidgets import QWidget, QMessageBox, QCheckBox, QFileDialog
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QThread
import copy
import os
from pyqtgraph import LinearRegionItem, mkBrush, mkPen, SignalProxy, InfiniteLine, TextItem, ArrowItem
from PyQt5 import uic
import pyvisa as visa
from gui.modules import mockSpectrometer as mock
from tools.threadWorker import Worker
from tools.CircularList import RingBuffer
import numpy as np


import logging


log = logging.getLogger(__name__)

optionsViewUiPath = os.path.dirname(os.path.realpath(__file__)) + "{0}optionsViewUI.ui".format(os.sep)
Ui_optionsView, QtBaseClass = uic.loadUiType(optionsViewUiPath)


class OptionsView(QWidget, Ui_optionsView):
    s_data_changed = pyqtSignal(dict)
    s_data_acquisition_done = pyqtSignal()

    def __init__(self, model=None):
