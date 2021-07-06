import logging
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QSettings
from PlasmaAnalyser import PlasmaAnalyser
import os


log = logging.getLogger(__name__)


class MainModel(QObject):
    s_simulatorObject_changed = pyqtSignal(PlasmaAnalyser)
    defaultFilePath = os.path.dirname(os.path.realpath(__file__)) + r"\parameters_preset\default_parameters.json"
    alternativePath = "default_parameters.json"
    print(defaultFilePath)

    def __init__(self):
        super(MainModel, self).__init__()
        self._simulatorObject = PlasmaAnalyser()

    @property
    def simulatorObject(self):
        return self._simulatorObject

