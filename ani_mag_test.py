import comedi
import time
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from statistics import mean
import matplotlib.animation as animation
import tkinter as tk
from tkinter.constants import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import itertools

#### Comedi setup, configuration for read and write
subdevr, chanr, rngr, aref = 0, 0, 1, comedi.AREF_GROUND
subdevw, chanw, rngw, = 1, 0, 0
datazero, datawmax = 2048, 4095
devname="/dev/comedi0"
dev = comedi.comedi_open(devname)
path = f=open('/home/at/suscept/magnari/Mælingar/calib_results.dat')
lines = (line for line in f if not line.startswith('#'))
FH = np.loadtxt(lines)
dev = comedi.comedi_open("/dev/comedi0")
ranger = comedi.comedi_get_range(dev, subdevr, chanr, rngr)
if dev is None:
    errno = comedi.comedi_errno()
    print('Error (%d) %s',errno, comedi.comedi_strerror(errno))

fig, ax = plt.subplots()
line, = ax.plot([], [], lw=2)
ax.grid()
xdata, ydata = [], []
canvas.draw()

class App(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack()

        self.label = tk.Label(text="Set value for magnetic flux")
        self.label.pack()
        self.entry = tk.Entry(text="50", width=15, bg="white")
        self.entry.insert(0,"0")
        self.entry.pack()

        self.btn=tk.Button(text="Reset magnet", command=self.zerofield, width=15, height=5,bg="grey")
        self.btn.pack()
        self.btn1= tk.Button(text="Turn on magnet", command=self.writevolt, width=15, height=5,bg="grey")
        self.btn1.pack()
        self.btnexit=tk.Button(text="exit",command=tkint.destroy)
        self.btnexit.pack()
   
        canvas = FigureCanvasTkAgg(fig, self)
        canvas.draw()
        canvas.get_tk_widget().pack()
        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas.get_tk_widget().pack()


    #### Set magnetic field
    def writevolt(self):
        val = self.entry.get()
        val = float(val)*FH[0]+FH[1]
        val = int(np.around(val))
        dev = comedi.comedi_open("/dev/comedi0")

        if val < 0 and val > 4095:
            val = datazero
            print('Input value not available')

        retvalw = comedi.comedi_data_write(dev, subdevw, chanw, rngw, aref, val)
        comedi.comedi_close(dev)
        print(f"Value set to: {val}")

    def zerofield(self):
        dev = comedi.comedi_open("/dev/comedi0")     
        retval = comedi.comedi_data_write(dev, subdevw, chanw, rngw, aref, datazero)
        print(f'Resetting DAQs to zero: {retval}')
        comedi.comedi_close(dev)
        self.entry.delete(0, tk.END)
        self.entry.insert(0,"0")


def init():
    ax.set_ylim(-150,150)
    ax.set_xlim(0, 10)
    del xdata[:]
    del ydata[:]
    line.set_data(xdata, ydata)
    return line,

def data_gen():
        dev = comedi.comedi_open(devname)
    
        for cnt in itertools.count():
            n=0
            voltlist=np.arange(1000, dtype=float)

            while n<1000:
                retval, volt = comedi.comedi_data_read(dev, subdevr, chanr, rngr, aref)
                voltlist[n]= ranger.min+float(volt)*2*ranger.max/float(datawmax)
                n+=1

            volt_ave=np.mean(voltlist)*100*0.99580361+0.60118
            print(volt_ave)
            t = cnt / 10
            yield t, volt_ave

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

comedi.comedi_close(dev)
tkint = tk.Tk()
tkint.config(bg="white")
myapp = App(tkint)
myapp.mainloop()
