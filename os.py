import pyvisa
import time


rm = pyvisa.ResourceManager()
print(rm.list_resources())

