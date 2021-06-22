import pyvisa


rm = pyvisa.ResourceManager()
print(rm.list_resources())
my_instr = rm.open_resource('USB0::0x0699::0x03A3::C020282::0::INSTR')
print(my_instr.query("*IDN?"))

