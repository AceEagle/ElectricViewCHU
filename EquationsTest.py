import math
import numpy as np
from matplotlib import pyplot as plt
from scipy import integrate
sinus = []
cosin = []
xList = []
multiplied = []
finished = []
for x in range(10000):
    sinus.append(math.sin(x))
    cosin.append(math.cos(x))
    xList.append(x)

multiplied = np.multiply(sinus, cosin)
ptlist = 10000 * integrate.trapezoid(multiplied) / (20 * 50)
print(ptlist)
