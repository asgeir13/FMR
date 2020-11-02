import comedi
import time
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from statistics import mean
import glob
import signal

import tkinter as tk
from tkinter.constants import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)

##Ekki nýlegur kóði, ekki endilega taka mark á þessum kóða

def magnet():
    subdevw = 1 # subdevice for write channels
    chanw = 0
    rngw = 0 # only one possible range for outputs -10..10 Volts
    aref = comedi.AREF_GROUND
    # for both input and output channels, range is 0..4095, zero is 2047.5
    datazero = 2048
    datawmax = 4095
    path = '/home/at/suscept/magnari/Mælingar/calib_results.dat'
    f=open(path)
    lines = (line for line in f if not line.startswith('#'))
    FH = np.loadtxt(lines)

    dev = comedi.comedi_open("/dev/comedi0")
    rangew=comedi.comedi_get_range(dev, subdevw, chanw, rngw)
    if dev is None:
        errno = comedi.comedi_errno()
        print('Error (%d) %s',errno, comedi.comedi_strerror(errno))


    val = entry.get()#input('Set value for magnetic flux in gauss  ')
    val = float(val)*FH[0]+FH[1]
    print(f'Float {val}')
    val = int(np.around(val))
    print(f'Rounded {val}')

    if val < 0 and val > 4095:
        val = datazero
        print('Input value not available')

    numbersteps=5
    step=abs(2048-val)/(numbersteps-1)
    if val < 2048:
        steps=np.flip(np.int_(np.arange(val,2048,step)))
        numbersteps=len(steps)
        print(steps)

    else:
        steps=np.int_(np.arange(2048, val, step))
        numbersteps=len(steps)
        print(steps)

    for i, valu in enumerate(steps):
        retvalw=comedi.comedi_data_write(dev, subdevw, chanw, rngw, aref, int(valu))
        time.sleep(1)


    retvalw = comedi.comedi_data_write(dev, subdevw, chanw, rngw, aref, val)
    time.sleep(9)

    retval = comedi.comedi_data_write(dev, subdevw, chanw, rngw, aref, datazero)
    print('Resetting DAQ to zero: ', retval)

    retval = comedi.comedi_get_maxdata(dev, subdevw, chanw)
    print('write retval from maxdata: ', retval)

    comedi.comedi_close(dev)

tkint = tk.Tk()

label = tk.Label(text="Set value for magnetic flux")
label.pack()
entry = tk.Entry(text="50", width=15, bg="white")
entry.insert(0,"0")
entry.pack()

button = tk.Button(text="Click me!", command=magnet, width=20,height=5,bg="grey")
button.pack()

tkint.mainloop()

