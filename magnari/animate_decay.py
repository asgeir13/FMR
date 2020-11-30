"""
=====
Decay
=====

This example showcases:
- using a generator to drive an animation,
- changing axes limits during an animation.
"""

import itertools

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import comedi

subdevr, chanr, rngr, aref = 0, 0, 1, comedi.AREF_GROUND
subdevw, chanw, rngw, = 1, 0, 0
datazero, datawmax = 2048, 4095
devname="/dev/comedi0"
dev = comedi.comedi_open(devname)
ranger = comedi.comedi_get_range(dev, subdevr, chanr, rngr)
print(ranger)
if dev is None:
    errno = comedi.comedi_errno()
    print('Error (%d) %s', errno,comedi.comedi_strerror(errno))

comedi.comedi_data_write(dev, subdevw, chanw, rngw, aref, 3500)

comedi.comedi_close(dev)



def data_gen():
    dev = comedi.comedi_open(devname)
    
    for cnt in itertools.count():
        n=0
        voltlist=np.arange(100, dtype=float)

        while n<100:
            retval, volt = comedi.comedi_data_read(dev, subdevr, chanr, rngr, aref)
            voltlist[n]= ranger.min+float(volt)*2*ranger.max/float(datawmax)
            #voltlist[n]=volt
            n+=1

        volt_ave=np.mean(voltlist)
        print(volt_ave)
        t = cnt / 10
        yield t, volt_ave


def init():
    ax.set_ylim(-1,1)
    ax.set_xlim(0, 10)
    del xdata[:]
    del ydata[:]
    line.set_data(xdata, ydata)
    return line,

fig, ax = plt.subplots()
line, = ax.plot([], [], lw=2)
ax.grid()
xdata, ydata = [], []


def run(data):
    # update the data
    t, y = data
    xdata.append(t)
    ydata.append(y)
    xmin, xmax = ax.get_xlim()

    if t >= xmax:
        ax.set_xlim(xmin, 2*xmax)
        ax.figure.canvas.draw()
    line.set_data(xdata, ydata)

    return line,

ani = animation.FuncAnimation(fig, run, data_gen, interval=10, init_func=init)
plt.show()


comedi.comedi_open(devname)
retval, value =comedi.comedi_data_write(dev, subdevw, chanw, rngw, aref, datazero)
print(f"Set to zero, {retval}")
comedi.comedi_close(dev)
