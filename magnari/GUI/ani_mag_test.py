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
        self.btnexit=tk.Button(text="exit", command=tkint.destroy)
        self.btnexit.pack()
        self.btnplot=tk.Button(text="plot", command=self.plotting, width=15, height=5,bg="grey")
        self.btnplot.pack()
        self.btnplotpause=tk.Button(text="Pause plot", command=self.data_gen_stop, width=15, height=5, bg="grey")
        self.btnplotpause.pack()

        self.btncalibrate=tk.Button(text="Calibrate", width=15, height=5, bg="grey")
        self.btncalibrate.pack()

        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot([], [], lw=1)
        self.ax.grid()
        self.xdata, self.ydata = [], []
        self.pause=True

        self.canvas = FigureCanvasTkAgg(self.fig, self)
        #toolbar = NavigationToolbar2Tk(canvas, self)
        #toolbar.update()
        self.canvas.get_tk_widget().pack()
    
    def plotting(self):
        self.pause=True
        plt.ion()
        self.canvas.draw()
        self.ani = animation.FuncAnimation(self.fig, self.run, self.data_gen, interval=200, init_func=self.init)
       
    def data_gen_stop(self):
        self.pause=False 


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


    def init(self):
        self.ax.set_ylim(-100,100)
        self.ax.set_xlim(0, 2)
        del self.xdata[:]
        del self.ydata[:]
        self.line.set_data(self.xdata, self.ydata)
        return self.line,
    
    
    def data_gen(self):
        dev = comedi.comedi_open("/dev/comedi0") 
        ranger = comedi.comedi_get_range(dev, subdevr, chanr, rngr)
        
        for cnd in itertools.count():
            n=0
            voltlist=np.arange(1000, dtype=float)
            if self.pause:
                while n<1000:
                    retval, volt = comedi.comedi_data_read(dev, subdevr, chanr, rngr, aref)
                    voltlist[n]= ranger.min+float(volt)*2*ranger.max/float(datawmax)
                    n+=1
            
                volt_ave=np.mean(voltlist)*100*0.99580361+0.60118
                print(volt_ave)
                t = cnd/50 
                yield t, volt_ave

    def run(self, data):
        # update the data
        self.data=data
        self.t, self.y = self.data
        self.xdata.append(self.t)
        self.ydata.append(self.y)
        self.xmin, self.xmax = self.ax.get_xlim()

        if self.t >= self.xmax:
            self.ax.set_xlim(self.xmin, 2*self.xmax)
            self.ax.figure.canvas.draw()
        
        self.line.set_data(self.xdata, self.ydata)

        return self.line,

#plt.ion()   
#plt.show()
comedi.comedi_close(dev)
tkint = tk.Tk()
tkint.config(bg="white")
myapp = App(tkint)
myapp.mainloop()
