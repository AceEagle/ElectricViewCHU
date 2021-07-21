import math

from scipy import integrate
sinus = []
cosin = []
multiplied = []
power1time = []
y0 = (0,)
t0 = 0
for x in range(50):
    sinus.append([x, math.sin(x)])
    cosin.append([x, math.cos(x)])
    multiplied.append([x, sinus[x][1]*cosin[x][1]])
(5000/20)*

power1time.append(5000/(20)*integrate.RK45(multiplied, t0, y0, 49))

