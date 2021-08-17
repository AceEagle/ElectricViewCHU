import json
import pandas as pd

data_saving_python = {
    "VoltageX": [1,2,3,4,5],
    "VoltageY": [1,2,3,4,5],
    "Power (m)X": [1,2,3,4,5],
    "Power (m)Y": [1,2,3,4,5],
    "Power (t)X": [1,2,3,4,5],
    "Power (t)y": [1,2,3,4,5],
    "LissajousX": [1,2,3,4,5],
    "LissajousY": [1,2,3,4,5],
    "Lissajous asymetriaX": [1,2,3,4,5],
    "Lissajous asymetriaY": [1,2,3,4,5],
    "Voltage asymetriaX": [1,2,3,4,5],
    "Voltage asymetriaY": [1,2,3,4,5],
    "Frequency": [1,2,3,4,5],
    "Voltage-Current Phase shift": [1,2,3,4,5],
    "Charge asymetria ratio": [1,2,3,4,5],
    "Voltage asymetria (Min)": [1,2,3,4,5],
    "Voltage asymetria (Max)": [1,2,3,4,5]
}

lmao = pd.DataFrame.from_dict(data_saving_python)
lmao.to_csv("testtest.csv")