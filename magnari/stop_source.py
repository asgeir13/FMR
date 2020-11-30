import comedi

subdevr = 0 # subdevice for read channels
subdevw = 1 # subdevice for write channels
chanr = 0
chanw = 0
rngr = 1  #comedi.comedi_get_n_ranges returns number of available ranges, the 3 range is from -0.0499 to 0.0499, this is not the exact number of significant digits 
rngw = 0 # only one possible range for outputs -10..10 Volts
aref = comedi.AREF_GROUND
datazero = 2048
datawmax = 4095

dev = comedi.comedi_open("/dev/comedi0")
if dev is None:
    errno = comedi.comedi_errno()
    print('Error (%d) %s',errno, comedi.comedi_strerror(errno))

retval = comedi.comedi_data_write(dev, subdevw, chanw, rngw, aref, datazero)
print(f'Resetting DAQs to zero: {retval}')
retval = comedi.comedi_get_maxdata(dev, subdevw, chanw)
print('write retval from maxdata: ', retval)
comedi.comedi_close(dev)
