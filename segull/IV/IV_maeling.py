import comedi
import time
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

##Data about the hall sensor KSY14, the inner resistance is 1.180 kOhms
#gmw 14. hall sensors

subdevw = 1 # subdevice for write channels
chanw = 0
rngw = 0 # only one possible range for outputs -10..10 Volts
aref = comedi.AREF_GROUND
# for output channels, range is 0..4095, zero is 2047.5
datazero = 2048
datawmax = 4095
hall_imp = 1180 #ohms

dev = comedi.comedi_open("/dev/comedi0")
#print(comedi.comedi_get_board_name(dev))  Get information about the daq card, current one is pci-6024E 
if dev is None:
    errno = comedi.comedi_errno()
    print('Error (%d) %s',errno, comedi.comedi_strerror(errno))

#Divide into steps
start=2048-4095/20
rang=2*4095/20
nvals = int(input('How many steps? '))
print(nvals)
nsteps = nvals - 1
lenstep = rang/(nsteps)
ctrvec = np.arange(nvals)
idealwriteval = ctrvec*lenstep+start #ideal case, unrounded
writeval = np.int_(np.around(idealwriteval)) #must write integer values
outvolt = -10 + 20*writeval/datawmax
outvoltstrg =[round(elem, 3) for elem in outvolt] # print only 3 decimals

print(f'''
unrounded output value: {idealwriteval}
ideal output voltage: {outvoltstrg}
rounded output value: { writeval}
''')

inp=[]

for n, val in enumerate(writeval):
    retvalw = comedi.comedi_data_write(dev, subdevw, chanw, rngw, aref, int(val))
    print(f'{n}, Output(Voltage, Value): ({round(outvolt[n],5)} V, {writeval[n]})')
    inp=input('Next? ') 

retval = comedi.comedi_data_write(dev, subdevw, chanw, rngw, aref, datazero)
print('Resetting DAQ to zero: ', retval)

retval = comedi.comedi_get_maxdata(dev, subdevw, chanw)
print('write retval from maxdata: ', retval)

comedi.comedi_close(dev)

