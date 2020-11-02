import comedi
import time
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from statistics import mean
from lmfit import Minimizer, Parameters, report_fit

##This code calibrates the small helmholtz coil, the magnetic flux is read from FH55 with it's analog output. The analog output has the range -3V to 3V and the following
##sampling/measurement the range is set to 300G. The current through the coil is sourced with this code, the array values are given in the range of from 0 to 4095,
##corresponding to -10V to 10V from the daq. This voltage is used to signal a amplifier with two powersupplies set to V_-=-25V and V_+=25V

##This code returns the file output.dat which incluedes the sourced voltage and the measured magnetic flux in gauss.

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
#val = input('Supplied voltage to coil ')
#val = int(val)


#if val < 0 and val > 4095:
#    val = datazero
#    print('Input value not available')

stepsize=100
steps=2095/stepsize
values=np.arange(1000,3100,stepsize)
values=np.append(values,3095)
nvals=10000
mean=np.arange(steps+1, dtype=float)
std=np.arange(steps+1, dtype=float)
for i, val in enumerate(values):
    voltlist = np.arange(nvals, dtype=float)
    retvalw = comedi.comedi_data_write(dev, subdevw, chanw, rngw, aref, int(val))
    time.sleep(2)
    n=0
    while n<nvals:
        retvalr, volt = comedi.comedi_data_read(dev, subdevr, chanr, rngr, aref)
        voltlist[n] = ranger.min+float(volt)*2*ranger.max/float(datawmax)
        n+=1
    

    mean[i] = np.mean(voltlist)*100*0.99580361+0.60118
    std[i] = np.std(voltlist)*100*0.9580361+0.60118
    retval = comedi.comedi_data_write(dev, subdevw, chanw, rngw, aref, datazero)
print(f'Resetting DAQs to zero: {retval}')

print(mean)
retval = comedi.comedi_get_maxdata(dev, subdevw, chanw)
print('write retval from maxdata: ', retval)

comedi.comedi_close(dev)
dataout= np.column_stack((values, mean, std))
np.savetxt('/home/at/suscept/magnari/Mælingar/output_Ls.dat', dataout, header='#coil source value, mean of analog output, standard deviation of the output', fmt=('%5.f', '%3.3f', '%4.4f'))


def fcn2min(params, x,y): 
    h = params['h']
    q = params['q']
    
    Y = h*x + q
    resids = Y - y
    weighted = resids ** 2 / std ** 2
    return weighted

params = Parameters()
params.add('h',value=20)
params.add('q',value=2060)

minner = Minimizer(fcn2min, params, fcn_args=(mean,values)) #,scale_covar=False)
result = minner.minimize()
print(result.params['h'].value)
report_fit(result)
parameters=np.arange(2, dtype=float)
parameters[0]=result.params['h'].value
parameters[1]=result.params['q'].value
plt.plot(mean,mean*result.params['h'].value + result.params['q'].value,'r-')
plt.show()
np.savetxt('/home/at/suscept/magnari/Mælingar/calib_results_Ls.dat', parameters, header='#Slope and intercept')
