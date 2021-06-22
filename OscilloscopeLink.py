import pyvisa
import time

rm = pyvisa.ResourceManager()
print(rm.list_resources())
my_instr = rm.open_resource('USB0::0x0699::0x0408::C049429::0::INSTR')
#print(my_instr.query("*IDN?"))
#print(my_instr.query("HOR:SCA?"))
#print(my_instr.query("MEASU?"))
#my_instr.query("SAV:SET?")
#print(my_instr.query("TRIG:A:LEV?"))
#print(my_instr.query("CH1:PRO?"))
#print(my_instr.query("CH1:SCA?"))

#-------------------------------------------------------------

my_instr.write("SINGle")
print(my_instr.query("*OPC?"))
print(my_instr.query("CHAN:DATA？"))
