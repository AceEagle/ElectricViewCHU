import logging
import tools.pyqtWorker
import matplotlib.pyplot as plt
import math
#from optionsFunctions import rawDataFileName
import panda as pd
import PyTektronixScope as pts

log = logging.getLogger(__name__)


class DataFunctions():

    def __init__(self):
        self.rawData = open("XNOM FAUT LE SYNCHROO AVEC OPTIONFUNCTIONS")

    def tension_charge_filter(self):
        df = pd.read_csv('filename.txt', spe=";", names="Tension")
        df["Tension"] = df["Tension"].str.replace(r' \(.+$', '')
        df = df[~df['Tension'].str.contains('\[edit\]')].reset_index(drop=True)
        print(df)

    def initiate_graph(self):
        plt.plot