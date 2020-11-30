import comedi
import time
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

##Data about the hall sensor KSY14, the inner resistance is 1.180 kOhms
#gmw 14. hall sensors

subdevr = 0 # subdevice for read channels
subdevr = 0
subdevw = 1 # subdevice for write channels
chanr = 0
chanw = 0
rngr = 3 
rngw = 0  # only one possible range for outputs -10..10 Volts
aref = comedi.AREF_GROUND
# for output channels, range is 0..4095, zero is 2047.5
datazero = 2048
datawmax = 4095
hallimp = 1121.95
hallimp_intercep = 0.002736

dev = comedi.comedi_open("/dev/comedi0")
print(comedi.comedi_get_board_name(dev))  #Get information about the daq card, current one is pci-6024E
ranger=comedi.comedi_get_range(dev, subdevr, chanr, rngr)
rangew=comedi.comedi_get_range(dev, 1, 1, rngw)


print(f'''
For read
{ranger.min}
{ranger.max}
{ranger.unit}
For write
{rangew.min}
{rangew.max}
{rangew.unit}''')

rang=comedi.comedi_get_n_ranges(dev, subdevr, chanr)
maxdat=comedi.comedi_get_maxdata(dev, subdevr, chanr)

print(maxdat)

if dev is None:
    errno = comedi.comedi_errno()
    print('Error (%d) %s',errno, comedi.comedi_strerror(errno))

data=comedi.lsampl_t

#retvalr=comedi.comedi_data_read_n(dev, subdevr, chanr, rngr, )


comedi.comedi_close(dev)
