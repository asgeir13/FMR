#import comedi
import time
import numpy as np
import matplotlib.pyplot as plt
from statistics import mean
import matplotlib.animation as animation
import tkinter as tk
from tkinter.constants import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import itertools
import pyvisa
from tkinter.messagebox import showinfo

#### Comedi setup, configuration for read and write
#subdevr, chanr, rngr, aref = 0, 0, 1, comedi.AREF_GROUND
#subdevw, chanw, rngw, = 1, 0, 0
#datazero, datawmax = 2048, 4095
#devname="/dev/comedi0"
#dev = comedi.comedi_open(devname)
#path = f=open('/home/at/suscept/magnari/Mælingar/calib_results.dat')
#lines = (line for line in f if not line.startswith('#'))
#FH = np.loadtxt(lines)
#dev = comedi.comedi_open("/dev/comedi0")
#ranger = comedi.comedi_get_range(dev, subdevr, chanr, rngr)


#if dev is None:
    #errno = comedi.comedi_errno()
    #print('Error (%d) %s',errno, comedi.comedi_strerror(errno))


def popup_bonus():
    win = tk.Toplevel()
    win.wm_title("Save calibration")

    l = tk.Label(win, text="Write \"open\", \"short\" and \"load\" for the corresponding measurements in the entry." )
    l.pack()
    b=tk.Button(win, text="Okay", command=win.destroy)
    b.pack()

def popup_showinfo():
    showinfo("Window", "Hello world!")
    


def popup_initial_value():
    win = tk.Toplevel()
    win.wm_title("Initial values")
    fram1=tk.Frame(win, bg='white')
    fram1.pack()
    labelsweep=tk.Label(fram1, text="Sweep setup", bg='white')
    labelsweep.pack(side=LEFT)

    fram2=tk.Frame(win, bg='white')
    fram2.pack()

    labelstart=tk.Label(fram2, text="Start", bg='white')
    labelstart.pack(side=LEFT, padx=5, pady=5)
    startentry=tk.Entry(fram2, width=5, bg='white')
    startentry.pack(side=LEFT)
    #startentry.insert("40")
    labelunit=tk.Label(fram2, text="MHz", bg='white')
    labelunit.pack(side=LEFT)
    
    fram3=tk.Frame(win, bg='white')
    fram3.pack()

    labelstop=tk.Label(fram3, text="Stop", bg='white')
    labelstop.pack(side=LEFT, padx=5, pady=5)
    stopentry=tk.Entry(fram3, width=5, bg='white')
    stopentry.pack(side=LEFT)
    #stopentry.insert("20000")
    labelunit1=tk.Label(fram3, text="MHz", bg='white')
    labelunit1.pack(side=LEFT)

    fram4=tk.Frame(win, bg='white')
    fram4.pack()
    label4=tk.Label(fram4, text="Calibration setup", bg='white')
    label4.pack(side=LEFT)

    fram5=tk.Frame(win, bg='white')
    fram5.pack()
    labelnumber=tk.Label(fram5, text="Nr. of measurements", bg='white')
    labelnumber.pack(side=LEFT)
    numberentry=tk.Entry(fram5, width=5, bg='white')
    numberentry.pack(side=LEFT)

    fram6=tk.Frame(win, bg='white')
    fram6.pack()
    setbutton=tk.Button(fram6, text="Set values", command=set_values)
    setbutton.pack()





class App(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack()

        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(1,2,1)
        self.ax1 = self.fig.add_subplot(1,2,2)
        
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        toolbar = NavigationToolbar2Tk(self.canvas, self)
        toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)


        frame1 = tk.Frame(self, bg="white")
        frame1.pack(fill=X)

        self.label = tk.Label(frame1, text="Set value for magnetic flux", bg='white')
        self.label.pack(side=LEFT, padx=5, pady=5)
        self.entry = tk.Entry(frame1,text="50", width=5, bg="white")
        self.entry.insert(0,"0")
        self.entry.pack(side=LEFT)
        self.labelunit = tk.Label(frame1, text="G", bg='white')
        self.labelunit.pack(side=LEFT)
        
        frame2 = tk.Frame(self, bg='white')
        frame2.pack(fill=X)
        
        self.btn=tk.Button(frame2, text="Reset magnet", command=self.zerofield)
        self.btn.pack(side=LEFT, padx=5)
        self.btn1= tk.Button(frame2, text="Turn on magnet", command=self.writevolt)
        self.btn1.pack(side=LEFT, padx=5)

        frame3= tk.Frame(self, bg='white')
        frame3.pack(fill=X)
        self.popup=tk.Button(frame3, text="Help", command=popup_bonus)
        self.popup.pack(side=LEFT, padx=5, pady=5)
        self.entry1 = tk.Entry(frame3, width = 6, bg='white')
        self.entry1.pack(side=LEFT, padx=5, pady=5)

        frame4 = tk.Frame(self, bg='white')
        frame4.pack(fill=X)
        
        self.btninitial=tk.Button(frame4, text="Set initial values", command=popup_initial_value)
        self.btninitial.pack(side=LEFT)

        self.btncalibrate=tk.Button(frame4, text="Calibrate", command=self.takecal)
        self.btncalibrate.pack(side=LEFT, padx=5, pady=5)
        

        self.btnexit=tk.Button(frame4, text="exit", command=tkint.destroy)
        self.btnexit.pack(side=RIGHT)
        
        self.btnsave=tk.Button(frame4, text="save", command=self.save)
        self.btnsave.pack(side=LEFT)
    

    #### Set magnetic field
    def save(self):
        text=self.entry1.get()
        if text == "open":
            S11o=S11
            print("S11o has been saved")
        elif text == "load":
            S11l=S11
            print("S11l has been saved")
        elif text == "short":
            S11s=S11
            print("S11s has been saved")
        else:
            print("Write in the entry which calibration took place!")

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

    def measure(self):
        inst.write("OFV")
        fre_val=inst.read("\n")
        fre_val=fre_val.rsplit(", ")
        new_fre_val=fre_val[0].rsplit(" ")
        new_fre_val.extend(fre_val[1:])
        new_fre_val=[float(n) for n in new_fre_val[1:]]

        inst.write("OFD")
        valu=inst.read("\n")
        valu=valu.rsplit(",")
        new_valu=valu[0].rsplit(" ")
        new_valu.extend(valu[1:])
        new_valu=[float(n) for n in new_valu[1:]]
        real_part=imag_part=np.arange(len(new_fre_val),dtype=np.float64)

        real_part=np.array(new_valu[0:-1:2])
        imag_part=new_valu[1:-1:2]
        imag_part.append(new_valu[-1])
        imag_part=np.array(imag_part)
        return real_part, imag_part, new_fre_val


    def takecal(self):
        global S11
        S11 = np.zeros(nfpoints, dtype=np.complex128)
        real_p, imag_p, freq = self.measure()
       
        S11=real_p+1j*imag_p
        self.ax.plot(freq, S11.real)
        self.ax1.plot(freq, S11.imag)
        plt.ion()
        self.canvas.draw()
        for n in range(nave):
            real_p, imag_p, freq=self.measure()
            S11=(S11*(n+1)+real_p+1j*imag_p)/(n+2)
            self.ax.clear()
            self.ax1.clear()
            self.ax.plot(freq, S11.real)
            self.ax1.plot(freq, S11.imag)
            self.canvas.draw()
            #self.canvas.pause(1)

        return S11


#some initial values
nfpoints = 401
nave = 10



#rm = pyvisa.ResourceManager('@py')
#inst = rm.open_resource('GPIB0::6::INSTR')
#inst.write("S11")
##start=input('Start frequency: ')
#start="40"
#start="SRT"+start+" MHz"
##stop=input('Stop frequency: ')
#stop="20000"
#stop="STP"+stop+" MHz"
#inst.write(start)
#inst.write(stop)

#inst.write("FMA") #Select ASCII data transfer format

#plt.ion()   
#plt.show()
#comedi.comedi_close(dev)
tkint = tk.Tk()
tkint.title("FMR")
myapp = App(tkint)
myapp.mainloop()
