import pyvisa

number_of_readings = 10
interval_in_ms = 500
rm = pyvisa.ResourceManager()
print(rm.list_resources())
my_instrument = rm.open_resource('USB0::0x0699::0x0408::C049429::0::INSTR')
my_instrument.('*rst; status:preset; *cls')
