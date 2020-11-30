
#hef ekki uppfaert sidan nyju virarnir voru settir

import comedi
import time
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

#gmw 14. hall sensors

subdevr = 0 # subdevice for read channels
subdevw = 1 # subdevice for write channels
chanr = 0
chanw = 0
rngr = 0
rngw = 0 # only one possible range for outputs -10..10 Volts
aref = comedi.AREF_GROUND
# for output channels, range is 0..4095, zero is 2047.5
datazero = 2048
datawmax = 4095
K_B=-121 #sensitivity of the hall sensor
delta_K_B=4.6
K_B_intercept=587.21

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
current = (outvolt-0.0027)/1121.95
hallvoltlist = np.arange(nvals)

print(f'''
unrounded output value: {idealwriteval}
ideal output voltage: {outvoltstrg}
rounded output value: { writeval}
''')

for n, val in enumerate(writeval):
    retvalw = comedi.comedi_data_write(dev, subdevw, chanw, rngw, aref, int(val))
    retvalr, hallvolt = comedi.comedi_data_read(dev, subdevr, chanr, rngr, aref)
    hallvoltphys = -10 + hallvolt*20/4095
    print(f'''{n}, Output(Voltage, Value, Current): ({round(outvolt[n],5)} V, {writeval[n]}, {round(current[n],5)} A)
Return value from read:{retvalr}
Input(Hallvoltage, Value):          ({round(hallvoltphys,5)} V, {hallvolt})''')
    hallvoltlist[n] = hallvolt
    time.sleep(0.5)


retval = comedi.comedi_data_write(dev, subdevw, chanw, rngw, aref, datazero)
print('Resetting DAQ to zero: ', retval)

retval = comedi.comedi_get_maxdata(dev, subdevw, chanw)
print('write retval from maxdata: ', retval)

comedi.comedi_close(dev)


hallvoltlist=hallvoltlist*20/4095-10
hallvoltarr=np.array(hallvoltlist)
currentarr=np.array(current).reshape((-1,1))
model=LinearRegression().fit(currentarr[1:],hallvoltarr[1:])
y=model.intercept_+currentarr*model.coef_[0]

B=((y[-1]-model.intercept_)/(currentarr[-1])-K_B_intercept)/K_B
print(f'''
(spenna, straumur)=({y[-1]} V,{currentarr[-1]} A)
The magnetic flux density is B={B} T 
uncertainty in magnetic flux densisty is delta B = {abs(B*delta_K_B/K_B)} T
''')

plt.plot(currentarr,hallvoltarr,'o')
plt.plot(currentarr,y)
plt.title('Hallspenna sem fall af straum')
plt.xlabel('Straumur [A]')
plt.ylabel('Hallspenna [V]')
plt.show()
