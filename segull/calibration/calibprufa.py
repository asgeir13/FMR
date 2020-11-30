import comedi
import time
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

##Data about the hall sensor KSY14, the inner resistance is 1.180 kOhms
#gmw 14. hall sensors

subdevr = 0 # subdevice for read channels
subdevw = 1 # subdevice for write channels
chanr = 0
chanw = 0
rngr = 2   #comedi.comedi_get_n_ranges returns number of available ranges, the 3 range is from -0.0499 to 0.0499, this is not the exact number of significant digits 
rngw = 0 # only one possible range for outputs -10..10 Volts
aref = comedi.AREF_GROUND
# for both input and output channels, range is 0..4095, zero is 2047.5
datazero = 2048
datawmax = 4095
hallimp = 1121.95+10000
hallimp_intercep = 0.002736

dev = comedi.comedi_open("/dev/comedi0")
ranger=comedi.comedi_get_range(dev, subdevr, chanr, rngr)
#print(comedi.comedi_get_board_name(dev))  Get information about the daq card, current one is pci-6024E 
if dev is None:
    errno = comedi.comedi_errno()
    print('Error (%d) %s',errno, comedi.comedi_strerror(errno))



#Divide into steps
rang=4095
#nvals = int(input('How many steps? '))
nvals = 50
nsteps = nvals-1
lenstep = rang/nsteps
ctrvec = np.arange(nvals)
idealwriteval = ctrvec*lenstep
writeval = np.int_(np.around(idealwriteval))
outvolt = -10+20*writeval/datawmax
outvoltstrg = [round(elem, 3) for elem in outvolt]
current = (outvolt-hallimp_intercep)/hallimp
hallvoltlist = np.arange(nvals, dtype=float)
print(f'''
unrounded output value: {idealwriteval}
ideal output voltage: {outvoltstrg}
rounded output value: {writeval}
''')

retvalw = comedi.comedi_data_write(dev, subdevw, chanw, rngw, aref, 2500)
time.sleep(0.0005)
for n, val in enumerate(writeval):
#    if n<nsteps/3:
#        retvalw = comedi.comedi_data_write(dev, subdevw, chanw, rngw, aref, 4095)
#        time.sleep(0.2)
#    elif n<nsteps*2/3 and n >= nsteps/3:
#        retvalw = comedi.comedi_data_write(dev, subdevw, chanw, rngw, aref, 3500)
#        time.sleep(0.2)
#    else:
#        retvalw2 = comedi.comedi_data_write(dev, subdevw, chanw, rngw, aref, 3200)
#       time.sleep(0.2)
    if n== nvals/2:
        retvalw= comedi.comedi_data_write(dev, subdevw, chanw, rngw, aref, 2300)
    retvalr, hallvolt = comedi.comedi_data_read(dev, subdevr, chanr, rngr, aref)
    hallvoltlist[n] = float(ranger.min+hallvolt*2*ranger.max/datawmax)
    print(f'''
Return value from read:{retvalr}
Input(Hallvoltage, Value):          ({hallvoltlist[n]} V, {hallvolt})''')



#Output (Voltage, Value, Current): ({20*2500/4095-10} V, {2500}, {(20*3500/4095-10-hallimp_intercep)/hallimp} A)    

print(hallvoltlist)
retval = comedi.comedi_data_write(dev, subdevw, chanw, rngw, aref, datazero)
print('Resetting DAQ to zero: ', retval)

retval = comedi.comedi_get_maxdata(dev, subdevw, chanw)
print('write retval from maxdata: ', retval)

comedi.comedi_close(dev)

hallvoltarr=np.array(hallvoltlist)
currentarr=np.array(current).reshape((-1,1))
model=LinearRegression().fit(currentarr,hallvoltarr)
y=model.intercept_+currentarr*model.coef_[0]

print(f'''
R2 is {model.score(currentarr,hallvoltarr)}            
The slope is: {model.coef_[0]} V/AT
''')

plt.plot(currentarr,hallvoltarr,'o')
plt.plot(currentarr,y)
plt.title('Hallspenna sem fall af straum')
plt.xlabel('Straumur [A]')
plt.ylabel('Hallspenna [V]')
plt.show()

