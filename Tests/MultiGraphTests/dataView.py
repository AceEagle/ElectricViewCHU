from PyQt5.QtWidgets import QWidget, QCheckBox, QGraphicsView, QGroupBox, QGridLayout
from PyQt5.QtCore import pyqtSignal
from PyQt5 import uic
import logging
import os

log = logging.getLogger(__name__)

lensViewUiPath = os.path.dirname(os.path.realpath(__file__)) + '{0}dataViewUi.ui'.format(os.sep)
Ui_dataView, QtBaseClass = uic.loadUiType(lensViewUiPath)


class DataView(QWidget, Ui_dataView):  # type: QWidget

    s_lens_data_changed = pyqtSignal(dict)

    def __init__(self, model=None, controller=None):
        super(DataView, self).__init__()
        self.setupUi(self)
        self.model = model
        self.plotItem = None
        self.dataPlotItem = None
        self.connect_checkbox()
        self.spaceGraph1 = QGraphicsView()
        self.spaceGraph2 = QGraphicsView()
        self.spaceGraph3 = QGraphicsView()
        self.spaceGraph4 = QGraphicsView()
        self.spaceGraph5 = QGraphicsView()
        self.spaceGraph6 = QGraphicsView()

    def connect_checkbox(self):
        self.G1CheckBox.toggled.connect(lambda: self.initiate_graph1())
        self.G2CheckBox.toggled.connect(lambda: self.initiate_graph2())
        self.G3CheckBox.toggled.connect(lambda: self.initiate_graph3())
        self.G4CheckBox.toggled.connect(lambda: self.initiate_graph4())
        self.G5CheckBox.toggled.connect(lambda: self.initiate_graph5())
        self.G6CheckBox.toggled.connect(lambda: self.initiate_graph6())

    def connect_signals(self):
        pass

    def add_graph_space(self, spaceGraphX):
        if self.graphGridLayout.count() == 3:
            self.graphGridLayout.addWidget(spaceGraphX, 2, 1)
        elif self.graphGridLayout.count() == 4:
            self.graphGridLayout.addWidget(spaceGraphX, 3, 1)
        elif self.graphGridLayout.count() == 5:
            self.graphGridLayout.addWidget(spaceGraphX, 4, 0)
        elif self.graphGridLayout.count() == 6:
            self.graphGridLayout.addWidget(spaceGraphX, 4, 1)
        else:
            self.graphGridLayout.addWidget(spaceGraphX)

    def delete_graph_space(self):
        pass

    def initiate_graph1(self):
        self.add_graph_space(self.spaceGraph1)
        pass

    def initiate_graph2(self):
        self.add_graph_space(self.spaceGraph2)
        pass

    def initiate_graph3(self):
        self.add_graph_space(self.spaceGraph3)
        pass

    def initiate_graph4(self):
        self.add_graph_space(self.spaceGraph4)
        pass

    def initiate_graph5(self):
        self.add_graph_space(self.spaceGraph5)
        pass

    def initiate_graph6(self):
        self.add_graph_space(self.spaceGraph6)
        pass