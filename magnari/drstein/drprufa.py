import comedi
import time
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from statistics import mean
from matplotlib.figure import Figure


fig= plt.figure()
ax = fig.add_subplot(2,1,1)
ax1 = fig.add_subplot(2,1,2)
#Data about the hall sensor GMW 14. the inner resistance is 1.180 kOhms
#gmw 14. hall sensors

subdevr = 0 # subdevice for read channels
subdevw = 1 # subdevice for write channels
chanr = 0
chanw = 0
rngr = 1  #comedi.comedi_get_n_ranges returns number of available ranges, the 3 range is from -0.0499 to 0.0499, this is not the exact number of significant digits 
rngw = 0 # only one possible range for outputs -10..10 Volts
aref = comedi.AREF_GROUND
# for both input and output channels, range is 0..4095, zero is 2047.5
datazero = 2048
datawmax = 4095

dev = comedi.comedi_open("/dev/comedi0")
ranger = comedi.comedi_get_range(dev, subdevr, chanr, rngr)
if dev is None:
    errno = comedi.comedi_errno()
    print('Error (%d) %s',errno, comedi.comedi_strerror(errno))

#Divide into steps
val = input('Supplied voltage to coil ')
val = int(val)


if val < 0 and val > 4095:
    val = datazero
    print('Input value not available')

nvals = 21000
numbersteps=12
prevoltlist = np.arange(nvals, dtype=float)# .reshape([5,nvals])
voltlist = np.arange(nvals, dtype=float)
step=abs(2048-val)/(numbersteps-1)
if val < 2048:
    steps=np.flip(np.int_(np.append(np.arange(val, 2048, step),2048)))
    numbersteps=len(steps)   
    print(steps)

else:
    steps=np.int_(np.append(np.arange(2048, val, step),val))
    numbersteps=len(steps)
    print(steps)

for i, valu in enumerate(steps):
    retvalw=comedi.comedi_data_write(dev, subdevw, chanw, rngw, aref, int(valu))
    time.sleep(4)
    
    if i==numbersteps-1:
        time.sleep(4)
        n=0
        starttime1=time.process_time()
        
        while n < nvals:
            retvalr, volt = comedi.comedi_data_read(dev, subdevr, chanr, rngr, aref)
            prevoltlist[n] = ranger.min+float(volt)*2*ranger.max/float(datawmax)
            n+=1

stoptime1 = time.process_time()

retvalw = comedi.comedi_data_write(dev, subdevw, chanw, rngw, aref, datazero)
time.sleep(2)
retvalw = comedi.comedi_data_write(dev, subdevw, chanw, rngw, aref, val)
time.sleep(8)
starttime = time.process_time()
n=0
while n<nvals:
    retvalr, volt = comedi.comedi_data_read(dev, subdevr, chanr, rngr, aref)
    voltlist[n] = ranger.min+float(volt)*2*ranger.max/float(datawmax)
    n+=1
    
stoptime=time.process_time()

retval = comedi.comedi_data_write(dev, subdevw, chanw, rngw, aref, datazero)
print(f'Resetting DAQs to zero: {retval}')

#print(mean)
retval = comedi.comedi_get_maxdata(dev, subdevw, chanw)
print('write retval from maxdata: ', retval)

comedi.comedi_close(dev)

timestep=(stoptime-starttime)/nvals
timearr=np.arange(0, stoptime-starttime, timestep, dtype=float)
if len(timearr) > nvals:
    timearr=timearr[:-1]

timearr=np.array(timearr)
voltarr=np.array(voltlist)

timestep1=(stoptime1-starttime1)/(nvals)
timearr1=np.arange(0, stoptime1-starttime1, timestep1, dtype=float)
if len(timearr1) > nvals:
    timearr1=timearr1[:-1]

timearr1=np.array(timearr1)
voltarr1=np.array(prevoltlist)#np.ravel(prevoltlist))


print(f'''
Mean {np.mean(voltarr)}
Standard deviation {np.std(voltarr)}
Mean ramp {np.mean(voltarr1)}
Standard deviation ramp {np.std(voltarr1)}
''')
ax1.set_xlabel('Tími [s]')
ax1.set_ylabel('Segulflæðisþéttleiki [G]')
ax.set_xlabel('Tími [s]')
ax.set_ylabel('Segulflæðisþéttleiki [G]')

ax1.plot(timearr,voltarr*100,'o-')
ax.plot(timearr1,voltarr1*100,'o-')
plt.show()
