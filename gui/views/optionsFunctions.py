import logging
import tools.pyqtWorker
import pyvisa as visa


log = logging.getLogger(__name__)


class OptionsFunctions():
    def __init__(self):
        self.rm = visa.ResourceManager()

    def connect_oscilloscope(self, oscilloUSB):
        self.myOscillo = self.rm.open_resource(oscilloUSB)

    def detect_oscilloscopes(self):
        return self.rm.list_resources()

    def nbPointsOscillo(self, number):
        print(self.myOscillo.query("*IDN?"))
        self.myOscillo.write("trace:points %d" % number)
