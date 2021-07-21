import math

from scipy import integrate
sinus = []
cosin = []
multiplied = []
finished = []
for x in range(50):
    sinus.append(math.sin(x))
    cosin.append(math.cos(x))
    multiplied.append(sinus[x]*cosin[x])
integrated = integrate.cumtrapz(multiplied)
finished.append(5000*integrated/20)

print(sinus)
print(cosin)
print(multiplied)
print(integrated)
print(finished)