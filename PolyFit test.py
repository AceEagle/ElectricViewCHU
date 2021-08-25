import numpy as np
import matplotlib.pyplot as plt

datax = [-5, -4, -3, -2 , -1, 0, 1, 2, 3, 4, 5, 4, 3, 2, 1, 0, -1, -2, -3, -4 ,-5]
datay = [-50, -40, -30, -20, -10, 0, 10, 20, 30, 40, 40, 40, 40, 30, 20, 10, 0, -10, -20, -30 ,-50]
#for x in range(-5, 5): datax.append(x)
#for x in range(5, -5): datax.append(x)

#for x in range(-50, 50, 10): datay.append(x)
#for x in range(50, -50, 10): datay.append(x)

polyfitage = np.polyfit(datax, datay, 4)

def PolyCoefficients(x, coeffs):
    """ Returns a polynomial for ``x`` values for the ``coeffs`` provided.

    The coefficients must be in ascending order (``x**0`` to ``x**o``).
    """
    o = len(coeffs)
    print(f'# This is a polynomial of order {ord}.')
    y = 0
    for i in range(o):
        print(i, x)
        y += coeffs[i]*x[i]**i
    return y

plt.plot(datax, PolyCoefficients(datax, polyfitage))
plt.plot(polyfitage)
plt.show()