import math
import numpy as np
from matplotlib import pyplot as plt
from scipy import integrate
file = open("Spectrum_Subt37_022.txt", 'r')
lines = file.readlines()
xliste = []
yliste = []
for i, x in enumerate(lines):
    lines[i] = lines[i].split(",")
    lines[i][1] = lines[i][1][:-1]
    lines[i][0] = float(lines[i][0])
    lines[i][1] = float(lines[i][1])
    xliste.append(lines[i][1])
    yliste.append(lines[i][0])
#print(lines)
#print(xliste[-1])
#print(yliste[-1])
cycles = 10e-3 * 10000 * 10
surface = 14.9 * 0.95 * 2
#print(surface)
dx = -4E-9

ptlist = 10000 * np.trapz(yliste, x=xliste) / surface

print(ptlist)
