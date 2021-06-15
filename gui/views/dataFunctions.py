import logging
import tools.pyqtWorker
import matplotlib.pyplot as plt
import math
from optionsFunctions import rawDataFileName

log = logging.getLogger(__name__)


class DataFunctions():

    def __init__(self):
        self.rawData = open("XNOM FAUT LE SYNCHROO AVEC OPTIONFUNCTIONS")

    def tensionChargeFilter(self):
