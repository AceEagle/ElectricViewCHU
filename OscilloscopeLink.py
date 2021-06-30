import pyvisa
import time

rm = pyvisa.ResourceManager()
print(rm.list_resources())
my_instr = rm.open_resource('USB0::0x0699::0x03A3::C020282::0::INSTR')
#print(my_instr.query("*IDN?"))
#print(my_instr.query("HOR:SCA?"))
#print(my_instr.query("MEASU?"))
#my_instr.query("SAV:SET?")
#print(my_instr.query("TRIG:A:LEV?"))
#print(my_instr.query("CH1:PRO?"))
#print(my_instr.query("CH1:SCA?"))

#-------------------------------------------------------------

values = my_instr.query_ascii_values('CURV?')
print(values)
my_instr.write('CURV?', encoding='latin1')
values = my_instr.read_raw()
print(values)