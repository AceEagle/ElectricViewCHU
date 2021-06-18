import pyvisa


rm = pyvisa.ResourceManager()
my_instrument = rm.open_resource('USB0::0x0699::0x0408::C049429::0::INSTR')
my_instrument.write("*rst; status:preset; *cls")