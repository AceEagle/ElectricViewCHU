import logging
import tools.pyqtWorker
import pyvisa as visa
import panda as pd


log = logging.getLogger(__name__)


class OptionsFunctions():
    def __init__(self):
        self.rm = visa.ResourceManager()

    def connect_oscilloscope(self, oscilloUSB):
        self.myOscillo = self.rm.open_resource(oscilloUSB)

    def detect_oscilloscopes(self):
        return self.rm.list_resources()

    def nb_points_oscilloscope(self, number):
        print(self.myOscillo.query("*IDN?"))
        self.myOscillo.write("trace:points %d" % number)
