import string
import time
import sys
import array
import pyvisa
import struct
import os
import numpy
#from PyTektronixScope import TektronixScope as ts

rm = pyvisa.ResourceManager()
liste = rm.list_resources()
instrumentObject = rm.open_resource(liste[1])
instrumentObject.timeout = 5000
print(instrumentObject.write(":DATa:SOUrce CH1;:DATa:ENCdg ASCIi;:DATa:STARt 1;:DATa:STOP 100"))
#À tester:
#nrpt, xunit, xzero, xincr, yunit, yzero, ymult, bytnr = instrumentObject.query(":WFMOutpre:NR_pt?;:WFMOutpre:XUNit?;:WFMOutpre:XZEro?;:WFMOutpre:XINcr?;:WFMOutpre:YUNit?;:WFMOutpre:YZEro?;:WFMOutpre:YMUlt?;:WFMOutpre:BYT_nr?")
nrpt = instrumentObject.query(":WFMOutpre:NR_pt?")
xunit = instrumentObject.query(':WFMOutpre:XUNit?')
xzero = instrumentObject.query(":WFMOutpre:XZEro?")
xincr = instrumentObject.query(":WFMOutpre:XINcr?")
yunit = instrumentObject.query(":WFMOutpre:YUNit?")
yzero = instrumentObject.query(":WFMOutpre:YZEro?")
ymult = instrumentObject.query(":WFMOutpre:YMUlt?")
bytnr = instrumentObject.query(":WFMOutpre:BYT_nr?")
print(nrpt, xunit, xzero, xincr, yunit, yzero, ymult, bytnr)
print(instrumentObject.query("CURVe?"))


""""
x_increment = instrumentObject.query_ascii_values(":WAVeform:XINCrement?")
x_origin =  instrumentObject.query_ascii_values(":WAVeform:XORigin?")
y_increment =  instrumentObject.query_ascii_values(":WAVeform:YINCrement?")
y_origin =  instrumentObject.query_ascii_values(":WAVeform:YORigin?")
y_reference =  instrumentObject.query_ascii_values(":WAVeform:YREFerence?")
# Get the waveform data.
instrumentObject.write(":WAVeform:DATA?")
sData = instrumentObject.read_bytes(50000)
print(sData)
# sData = get_definite_length_block_data(sData)
# Unpack unsigned byte data.
values = struct.unpack("%dB" % len(sData), sData)
print("Number of data values: %d" % len(values))
# Save waveform data values to CSV file.
f = open("waveform_data.csv", "w")
for i in range(0, len(values) - 1):
    time_val = x_origin[0] + (i * x_increment[0])
    #print(values[i], y_reference, y_increment, y_origin)
    voltage = ((values[i] - y_reference[0]) * y_increment[0]) + y_origin[0]
    f.write("%E, %f\n" % (time_val, voltage))
f.close()
print("Waveform format BYTE data written to waveform_data.csv.")
"""
#instrumentObject.write('DATa:RESOlution FULL, DATa:COMPosition SINGULAR_YT, DATa:DESTination 5000, DATa:STARt 1, DATa:ENCdg ASCIi')
#a = instrumentObject.query_binary_values("WAVFrm?")
#print(a)
#x_origin =  instrumentObject.query_ascii_values(":WAVeform:XORigin?")
#y_increment =  instrumentObject.query_ascii_values(":WAVeform:YINCrement?")
#y_origin =  instrumentObject.query_ascii_values(":WAVeform:YORigin?")
#y_reference =  instrumentObject.query_ascii_values(":WAVeform:YREFerence?")
# Get the waveform data.
#instrumentObject.write(":WAVeform:DATA?")
#sData = instrumentObject.read_bytes(50000)
# sData = get_definite_length_block_data(sData)
# Unpack unsigned byte data.
#values = struct.unpack("%dB" % len(sData), sData)
#print("Number of data values: %d" % len(values))
# Save waveform data values to CSV file.
#f = open("waveform_data.csv", "w")
#for i in range(0, len(values) - 1):
#    time_val = x_origin[0] + (i * x_increment[0])
#    #print(values[i], y_reference, y_increment, y_origin)
#    voltage = ((values[i] - y_reference[0]) * y_increment[0]) + y_origin[0]
#    f.write("%E, %f\n" % (time_val, voltage))
#f.close()
#print("Waveform format BYTE data written to waveform_data.csv.")


