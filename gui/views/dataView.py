from PyQt5.QtWidgets import QWidget, QCheckBox, QGraphicsView, QGroupBox, QGridLayout
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5 import uic, QtMultimedia
import logging
import os
from pydispatch import dispatcher
import math
from gui.views.data import Data
from pyqtgraph import PlotItem, widgets


log = logging.getLogger(__name__)

lensViewUiPath = os.path.dirname(os.path.realpath(__file__)) + '{0}dataViewUi.ui'.format(os.sep)
Ui_dataView, QtBaseClass = uic.loadUiType(lensViewUiPath)

SIGNAL_PLOT_TOGGLED = "plot.toggled.graphic"

class DataView(QWidget, Ui_dataView):  # type: QWidget
    SIGNAL_toggled_plot_graphic = "graphic"
    s_lens_data_changed = pyqtSignal(dict)

    def __init__(self, model=None, controller=None):
        super(DataView, self).__init__()
        self.setupUi(self)
        self.model = model
        self.plotItem = None
        self.dataPlotItem = None
        self.connect_checkbox()
        self.allPlotsDict = {}
        self.create_plots()

    def connect_checkbox(self):
        self.G1CheckBox.stateChanged.connect(lambda: self.initiate_graph("graph1" , caller=self.G1CheckBox))
        self.G2CheckBox.stateChanged.connect(lambda: self.initiate_graph("graph2" , caller=self.G2CheckBox))
        self.G3CheckBox.stateChanged.connect(lambda: self.initiate_graph("graph3" , caller=self.G3CheckBox))
        self.G4CheckBox.stateChanged.connect(lambda: self.initiate_graph("graph4" , caller=self.G4CheckBox))
        self.G5CheckBox.stateChanged.connect(lambda: self.initiate_graph("graph5" , caller=self.G5CheckBox))
        self.G6CheckBox.stateChanged.connect(lambda: self.initiate_graph("graph6" , caller=self.G6CheckBox))

    def connect_signals(self):
        pass

    def initiate_graph(self, graphic, caller=None):
        if caller.checkState() == 2:
            self.allPlotsDict[graphic]["displayed"] = 1
            self.update_plots_position()
            dispatcher.send(signal=SIGNAL_PLOT_TOGGLED, sender=self, **{"graphic": graphic})

        elif caller.checkState() == 0:
            self.graphicsView.removeItem(self.allPlotsDict["{}".format(graphic)]["plotItem"])
            self.allPlotsDict[graphic]["displayed"] = 0
            self.update_plots_position()

        else:
            pass

    def create_plots(self):
        for graphic in Data().graphics:
            self.allPlotsDict[graphic] = {"plotItem": PlotItem(), "displayed": 0}
        for graphic in Data().graphics:
            self.allPlotsDict[graphic]["plotDataItem"] = {}
            dataPlotItem = self.allPlotsDict[graphic]["plotItem"].plot()
            self.allPlotsDict[graphic]["plotDataItem"][graphic] = dataPlotItem
            self.allPlotsDict[graphic]["plotItem"].setTitle(graphic)
        print(self.allPlotsDict)

    def update_plots_position(self):
        self.graphicsView.clear()
        sideLength = math.ceil(
            math.sqrt(sum(self.allPlotsDict[ind]["displayed"] == 1 for ind in self.allPlotsDict.keys())))
        tempPlotDict = {key : value for (key, value) in self.allPlotsDict.items() if value["displayed"] == 1}
        graphicList = list(tempPlotDict.keys())
        listIndex = 0
        for i in range(sideLength):
            for j in range(sideLength):
                try:
                    self.graphicsView.addItem(tempPlotDict[graphicList[listIndex]]["plotItem"], i, j)
                    listIndex += 1
                except:
                    pass

    @pyqtSlot(dict)
    def update_graph(self, simPlotData):
        for graphic in Data().graphics:
            try:
                kwargs = simPlotData[graphic]
                self.allPlotsDict[graphic]["plotDataItem"][graphic].setData(**kwargs)
            except:
                log.info("null")