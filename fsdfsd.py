import json
import pandas as pd

data_saving_python = {
    "VoltageX": [],
    "VoltageY": [],
    "Power (m)X": [],
    "Power (m)Y": [],
    "Power (t)X": [],
    "Power (t)y": [],
    "LissajousX": [],
    "LissajousY": [],
    "Lissajous asymetriaX": [],
    "Lissajous asymetriaY": [],
    "Voltage asymetriaX": [],
    "Voltage asymetriaY": [],
    "Frequency": [],
    "Voltage-Current Phase shift": [],
    "Charge asymetria ratio": [],
    "Voltage asymetria (Min)": [],
    "Voltage asymetria (Max)": []
}

lmao = pd.DataFrame.from_dict(data_saving_python)
lmao.to_csv("testtest.csv")