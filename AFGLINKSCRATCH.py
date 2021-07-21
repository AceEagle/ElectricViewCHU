import array
import pyvisa
import struct
import os
import numpy

rm = pyvisa.ResourceManager()
liste = rm.list_resources()
instrumentObject = rm.open_resource("USB0::0x0699::0x0349::C014731::0::INSTR")
instrumentObject.timeout = 5000

print(instrumentObject.write("SOURce1:BURSt:NCYCles 50"))
print(instrumentObject.query("SOURce1:BURSt:NCYCles?"))
