import time
from PyQt5.QtWidgets import QWidget, QFileDialog
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThreadPool
from PyQt5 import uic
import logging
import os
from pydispatch import dispatcher
import math
from Data import Data
from pyqtgraph import PlotItem
from gui.widgets.QFlashButton import QFlashButton
from tools.pyqtWorker import Worker

log = logging.getLogger(__name__)

lensViewUiPath = os.path.dirname(os.path.realpath(__file__)) + '{0}dataViewUi.ui'.format(os.sep)
Ui_dataView, QtBaseClass = uic.loadUiType(lensViewUiPath)

SIGNAL_PLOT_TOGGLED = "plot.toggled.graphic"


class DataView(QWidget, Ui_dataView):
    SIGNAL_toggled_plot_graphic = "graphic"
    s_lens_data_changed = pyqtSignal(dict)

    def __init__(self, model=None, controller=None):
        super(DataView, self).__init__()
        self.setupUi(self)
        self.model = model
        self.threadpool = QThreadPool()
        self.plotItem = None
        self.dataPlotItem = None
        self.connect_checkbox()
        self.connect_buttons()
        self.connect_signals()
        self.allPlotsDict = {}
        self.create_plots()
        self.saved_data = None
        self.initialize_view()
        log.info("Initiating multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

    def connect_buttons(self):
        self.LaunchDataFButton.clicked.connect(self.launch_data)
        self.SaveDataPButton.clicked.connect(self.search_file)
        self.ResetDataPButton.clicked.connect(self.reset_data)
        log.info("Connecting dataView GUI")

    def connect_checkbox(self):
        self.G1CheckBox.stateChanged.connect(lambda: self.initiate_graph("graph1" , caller=self.G1CheckBox))
        self.G2CheckBox.stateChanged.connect(lambda: self.initiate_graph("graph2" , caller=self.G2CheckBox))
        self.G3CheckBox.stateChanged.connect(lambda: self.initiate_graph("graph3" , caller=self.G3CheckBox))
        self.G4CheckBox.stateChanged.connect(lambda: self.initiate_graph("graph4" , caller=self.G4CheckBox))
        self.G5CheckBox.stateChanged.connect(lambda: self.initiate_graph("graph5" , caller=self.G5CheckBox))
        self.G6CheckBox.stateChanged.connect(lambda: self.initiate_graph("graph6" , caller=self.G6CheckBox))

    def connect_signals(self):
        log.info("Connecting dataView Signals...")
        self.model.s_data_changed.connect(self.update_graph)

    def initialize_view(self):
        self.G1CheckBox.setChecked(True)

    def search_file(self):
        name = QFileDialog.getSaveFileName(self, 'Save File', '', 'Txt Files (*.txt);;All Files (*)',
                                           options=QFileDialog.DontUseNativeDialog)
        if name[0] == '':
            log.info("File is not good")

        if name[1] == 'Txt Files (*.txt)' and name[0][-3:] != '.txt':
            name = name[0] + '.txt'
        else:
            name = name[0]

        lines = "test1 lmao"

        with open(name, 'w') as fp:
            fp.writelines(lines)

    def crash_the_app_thread(self):
        worker = Worker(self.crash_the_app)
        self.threadpool.start(worker)

    def crash_the_app(self, progress_callback):
        for x in range(3):
            time.sleep(1)
            print("x")
        log.info("BONJOUR TEST")

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
                kwargs = simPlotData[graphic]['data']
                print(kwargs)
                self.allPlotsDict[graphic]["plotDataItem"][graphic].setData(**kwargs)
            except:
                log.info("null")

    def lissajous_filter(self, tension, charge):
        pass

    def launch_data(self):
        self.LaunchDataFButton.start_flash()
        self.LaunchDataFButton.clicked.disconnect()
        self.LaunchDataFButton.clicked.connect(self.stop_data)
        self.LaunchDataFButton.setText("Stop")
        self.LaunchDataFButton.setEnabled(True)
        self.ResetDataPButton.setStyleSheet("background-color : red")
        worker = Worker(self.model.launch_propagation)
        self.threadpool.start(worker)

    def stop_data(self):
        self.LaunchDataFButton.stop_flash()
        self.LaunchDataFButton.setEnabled(False)
        self.LaunchDataFButton.setText("Resume")
        pass
        self.LaunchDataFButton.clicked.disconnect()
        self.LaunchDataFButton.clicked.connect(self.launch_data)
        self.LaunchDataFButton.setEnabled(True)
        worker = Worker(self.model.stop_propagation)
        self.threadpool.start(worker)

    def reset_data(self):
        self.saved_data = None
        self.LaunchDataFButton.stop_flash()
        self.LaunchDataFButton.setEnabled(False)
        self.LaunchDataFButton.setText("Start")
        self.LaunchDataFButton.clicked.disconnect()
        self.LaunchDataFButton.clicked.connect(self.launch_data)
        self.LaunchDataFButton.setEnabled(True)
        self.ResetDataPButton.setStyleSheet("background-color : None")
        worker = Worker(self.model.reset_save_status)
        self.threadpool.start(worker)

