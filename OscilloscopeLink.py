from struct import unpack
import pyvisa as visa
import numpy as np
rm = visa.ResourceManager('@py')
print(rm)

def acquire(channel, port):
    try:
        scope = rm.open_resource(port)
        scope.write("DATA:SOURCE " + channel)
        scope.write('DATA:WIDTH 1')
        scope.write('DATA:ENC RPB')
        ymult = float(scope.ask('WFMPRE:YMULT?'))
        yzero = float(scope.ask('WFMPRE:YZERO?'))
        yoff = float(scope.ask('WFMPRE:YOFF?'))
        xincr = float(scope.ask('WFMPRE:XINCR?'))
        xdelay = float(scope.query('HORizontal:POSition?'))
        scope.write('CURVE?')
        data = scope.read_raw()
        headerlen = 2 + int(data[1])
        header = data[:headerlen]
        ADC_wave = data[headerlen:-1]
        ADC_wave = np.array(unpack('%sB' % len(ADC_wave),ADC_wave))
        Volts = (ADC_wave - yoff) * ymult  + yzero
        Time = np.arange(0, (xincr * len(Volts)), xincr)-((xincr * len(Volts))/2-xdelay)
        return Time,Volts
    except IndexError:
        return 0,0