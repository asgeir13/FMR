import comedi
import time
import numpy as np

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

dev = comedi.comedi_open("/dev/comedi0")


print(dev)
print(comedi.comedi_get_board_name(dev))
#info= comedi.comedi_get_subdevice_type("/dev/comedi0")
#print(info)
if dev is None:
    errno = comedi.comedi_errno()
    print('Error (%d) %s',errno, comedi.comedi_strerror(errno))
# # retval = comedi.comedi_data_read(dev, subdevr, chanr, rngr, aref)
# retval = comedi.comedi_data_write(dev, subdevw, chanw, rngw, aref, data)
# print('write retval: ', retval)
# # physval = comedi.comedi_to_phys(data, [-10, 10], 4095)
# # print('this corresponds to: ', physval)

# divide into equal steps:
nvals = 7
nsteps = nvals - 1
lenstep = datawmax/nsteps
ctrvec = np.arange(nvals)
idealwriteval = ctrvec*lenstep #ideal case, unrounded
writeval = np.int_(np.around(ctrvec*lenstep)) #must write integer values
outvolt = -10 + 20*writeval/datawmax
print('unrounded output value: ', idealwriteval)
print('ideal output voltage: ', -10 + 20*ctrvec*lenstep/datawmax)
print('rounded output value: ', writeval)
print('real output voltage: ', outvolt)

for n, val in enumerate(writeval):
    print(n, 'outp: ', val, writeval[n], 'voltage: ', outvolt[n])
    retval = comedi.comedi_data_write(dev, subdevw, chanw, rngw, aref, int(val))
    print('step: ', n, ' : ', 'value written: ', val, 'physical value: ', -10+val*20/4095, 'V')
    retval, hallvolt = comedi.comedi_data_read(dev, subdevr, chanr, rngr, aref)
    print('retval from read :', retval, '  Hall voltage: ', hallvolt, ' physical value: ', -10+hallvolt*20/4095, 'V')
    time.sleep(3.0)

# for n in range(len(vec2p)):
#     val = vec2p[n]
#     retval = comedi.comedi_data_write(dev, subdevw, chanw, rngw, aref, int(val))
#     print('step: ', n, ' : ', 'value written: ', val, 'physical value: ', -10+val*20/4095, 'V')
#     time.sleep(1.5)
#     retval, hallvolt = comedi.comedi_data_read(dev, subdevr, chanr, rngr, aref)
#     print('retval from read :', retval, '  Hall voltage: ', hallvolt, ' physical value: ', -10+hallvolt*20/4095, 'V')

retval = comedi.comedi_data_write(dev, subdevw, chanw, rngw, aref, datazero)
print('Resetting DAQ to zero: ', retval)

retval = comedi.comedi_get_maxdata(dev, subdevw, chanw)
print('write retval from maxdata: ', retval)

comedi.comedi_close(dev)
