from PyQt5.QtWidgets import QWidget, QFileDialog
from PyQt5.QtCore import pyqtSignal, QThreadPool
import os
from PyQt5 import uic
import logging
log = logging.getLogger(__name__)

calculViewUiPath = os.path.dirname(os.path.realpath(__file__)) + "{0}calculViewUI.ui".format(os.sep)
Ui_calculView, QtBaseClass = uic.loadUiType(calculViewUiPath)

SIGNAL_PLOT_TOGGLED = "plot.toggled.graphic"


class CalculView(QWidget, Ui_calculView):
    instruments_changed = pyqtSignal()

    def __init__(self, model=None, controller=None):
        super(CalculView, self).__init__()
        self.model = model
        self.setupUi(self)
        self.threadpool = QThreadPool()

        self.connect_buttons()

    def connect_buttons(self):
        self.OpenPButton.clicked.connect(self.open_file)
        self.OverwritePButton.clicked.connect(self.save_file)

    def connect_signals(self):
        pass

    def open_file(self):
        name = QFileDialog.getOpenFileName(self, 'Open File', '', 'Txt Files (*.txt);;All Files (*)',
                                           options=QFileDialog.DontUseNativeDialog)
        if name[0] == '':
            log.info("File is not good")

        else:
            name = name[0]

        text = open(name).read()
        self.PlainTextEdit.setPlainText(text)

    def save_file(self):
        pass
