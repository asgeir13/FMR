import comedi
import time
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from statistics import mean

#Data about the hall sensor GMW 14. the inner resistance is 1.180 kOhms
#gmw 14. hall sensors

subdevr = 0 # subdevice for read channels
subdevw = 1 # subdevice for write channels
chanr = 0
chanw = 0
chanw1 = 1
rngr = 0 #comedi.comedi_get_n_ranges returns number of available ranges, the 3 range is from -0.0499 to 0.0499, this is not the exact number of significant digits 
rngw = 0 # only one possible range for outputs -10..10 Volts
aref = comedi.AREF_GROUND
# for both input and output channels, range is 0..4095, zero is 2047.5
datazero = 2048
datawmax = 4095
hallimp = 1121.95+10000
hallimp_intercep = 0.002736

dev = comedi.comedi_open("/dev/comedi0")
ranger=comedi.comedi_get_range(dev, subdevr, chanr, rngr)
if dev is None:
    errno = comedi.comedi_errno()
    print('Error (%d) %s',errno, comedi.comedi_strerror(errno))

#print(ranger.unit)
#print(comedi.comedi_get_n_channels(dev, subdevw))
#print(comedi.comedi_get_board_name(dev))  Get information about the daq card, current one is pci-6024E 
#Divide into steps
rang=4095/2
#nvals = int(input('How many steps? '))
nvals = 65000
hallvoltlist = np.arange(nvals, dtype=float)

val = input('Supplied voltage to sensor ')
val = int(val)
val1 = input('Supplied voltage to coil ')
val1 = int(val1)

if val < 0 and val > 4095:
    val = datazero
    print('Input value not available')

retvalw = comedi.comedi_data_write(dev, subdevw, chanw, rngw, aref, val)
retvalw1 = comedi.comedi_data_write(dev, subdevw, chanw1, rngw, aref, val1)
#print(retvalw1)
#time.sleep(0.0005)
time.sleep(5)
starttime=time.process_time()
i=0
while i<nvals:
    retvalr, hallvolt = comedi.comedi_data_read(dev, subdevr, chanr, rngr, aref)
    hallvoltlist[i] = ranger.min+float(hallvolt)*2*ranger.max/float(datawmax)
   # time.sleep(0.000008)
    i+=1

stoptime=time.process_time()

print(f'''Mean {mean(hallvoltlist)*1000} mV
Deviation {np.std(hallvoltlist)*1000} mV
time elapsed {stoptime-starttime} s
''')

retval = comedi.comedi_data_write(dev, subdevw, chanw, rngw, aref, datazero)
retval1 =comedi.comedi_data_write(dev, subdevw, chanw1, rngw, aref, datazero)
print(f'Resetting DAQs to zero: {retval},{retval1}')

retval = comedi.comedi_get_maxdata(dev, subdevw, chanw)
print('write retval from maxdata: ', retval)

comedi.comedi_close(dev)

timestep=(stoptime-starttime)/(nvals)

timearr=np.arange(0, stoptime-starttime, timestep, dtype=float)
if len(timearr) > nvals:
    timearr=timearr[:-1]

hallvoltarr=np.array(hallvoltlist)
timearr=np.array(timearr)

plt.plot(timearr,hallvoltarr,'o-')
plt.title('Hallspenna')
plt.ylabel('Hallspenna [V]')
plt.show()
