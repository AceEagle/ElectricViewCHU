from PyQt5.QtWidgets import QWidget, QCheckBox, QGraphicsView, QGroupBox, QGridLayout
from PyQt5.QtCore import pyqtSignal
from PyQt5 import uic, QtMultimedia
import logging
import os
from pydispatch import dispatcher
import math


log = logging.getLogger(__name__)

lensViewUiPath = os.path.dirname(os.path.realpath(__file__)) + '{0}dataViewUi.ui'.format(os.sep)
Ui_dataView, QtBaseClass = uic.loadUiType(lensViewUiPath)

SIGNAL_PLOT_TOGGLED = "plot.toggled.indicator"

class DataView(QWidget, Ui_dataView):  # type: QWidget
    SIGNAL_toggled_plot_indicator = "indicator"
    s_lens_data_changed = pyqtSignal(dict)

    def __init__(self, model=None, controller=None):
        super(DataView, self).__init__()
        self.setupUi(self)
        self.model = model
        self.plotItem = None
        self.dataPlotItem = None
        self.connect_checkbox()
        self.allPlotsDict = {}

    def connect_checkbox(self):
        self.G1CheckBox.stateChanged.connect(lambda: self.initiate_graph("Graph1" , caller=self.G1CheckBox))
        self.G2CheckBox.stateChanged.connect(lambda: self.initiate_graph("Graph2" , caller=self.G2CheckBox))
        self.G3CheckBox.stateChanged.connect(lambda: self.initiate_graph("Graph3" , caller=self.G3CheckBox))
        self.G4CheckBox.stateChanged.connect(lambda: self.initiate_graph("Graph4" , caller=self.G4CheckBox))
        self.G5CheckBox.stateChanged.connect(lambda: self.initiate_graph("Graph5" , caller=self.G5CheckBox))
        self.G6CheckBox.stateChanged.connect(lambda: self.initiate_graph("Graph6" , caller=self.G6CheckBox))

    def connect_signals(self):
        pass

    def initiate_graph(self, indicator, caller=None):
        if caller.checkState() == 2:
            self.allPlotsDict[indicator]["displayed"] = 1
            self.update_plots_position()
            dispatcher.send(signal=SIGNAL_PLOT_TOGGLED, sender=self, **{"indicator": indicator})

        elif caller.checkState() == 0:
            self.pyqtgraphWidget.removeItem(self.allPlotsDict["{}".format(indicator)]["plotItem"])
            self.allPlotsDict[indicator]["displayed"] = 0
            self.update_plots_position()

        else:
            pass

    def update_plots_position(self):
        self.pyqtgraphWidget.clear()
        sideLength = math.ceil(
            math.sqrt(sum(self.allPlotsDict[ind]["displayed"] == 1 for ind in self.allPlotsDict.keys())))
        tempPlotDict = {key : value for (key, value) in self.allPlotsDict.items() if value["displayed"] == 1}
        indicatorList = list(tempPlotDict.keys())
        listIndex = 0
        for i in range(sideLength):
            for j in range(sideLength):
                try:
                    self.pyqtgraphWidget.addItem(tempPlotDict[indicatorList[listIndex]]["plotItem"], i, j)
                    listIndex += 1
                except:
                    pass

    def initiate_graph1(self):
        if self.G1CheckBox.isChecked:
            self.add_graph_space(self.spaceGraph1)
        else:
            log.debug("YO")
            self.delete_graph_space(self.spaceGraph1)

    def initiate_graph2(self):
        if self.G2CheckBox.isChecked:
            self.add_graph_space(self.spaceGraph2)
        else:
            log.debug("YO")
            self.delete_graph_space(self.spaceGraph2)

    def initiate_graph3(self):
        if self.G3CheckBox.isChecked:
            self.add_graph_space(self.spaceGraph3)
        else:
            log.debug("YO")
            self.delete_graph_space(self.spaceGraph3)

    def initiate_graph4(self):
        if self.G4CheckBox.isChecked:
            self.add_graph_space(self.spaceGraph4)
        else:
            log.debug("YO")
            self.delete_graph_space(self.spaceGraph4)

    def initiate_graph5(self):
        if self.G5CheckBox.isChecked:
            self.add_graph_space(self.spaceGraph5)
        else:
            log.debug("YO")
            self.delete_graph_space(self.spaceGraph5)

    def initiate_graph6(self):
        if self.G6CheckBox.isChecked:
            self.add_graph_space(self.spaceGraph6)
        else:
            log.debug("YO")
            self.delete_graph_space(self.spaceGraph6)
