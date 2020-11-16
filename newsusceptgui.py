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
#import pyvisa
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




class App(tk.Tk):
    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.wm_title(self, "FMR")
        container = tk.Frame(self)
        container.pack(side=TOP, fill=BOTH, expand=True)

        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)

        self.frames = {}

        for F in (StartPage, Page1, Page2, Page3):

            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row = 0, column = 0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        #self.popup=tk.Button(frame3, text="Help", command=popup_bonus)
        #self.popup.pack(side=LEFT, padx=5, pady=5)

        self.btninitial=tk.Button(self, text="Set initial values", command=lambda: controller.show_frame(Page1)).grid(row=0,column=0,pady=10, sticky='e')
        self.btnfield=tk.Button(self, text="Set magnetic flux", command=lambda: controller.show_frame(Page2)).grid(row=0,column=1, pady=10)
        self.btnfield=tk.Button(self, text="Viewer", command=lambda: controller.show_frame(Page3)).grid(row=0,column=2, pady=10)
        self.btncalcorr=tk.Button(self, text="Calc. correction & apply", command=self.docal).grid(row=2,column=0, pady=5, sticky='e')
    
        self.btncalibrate=tk.Button(self, text="Measure", command=self.takecal).grid(row=1, column=0, pady=5, sticky='e')
        self.entry1 = tk.Entry(self, width = 6, bg='white')
        self.entry1.grid(row=1,column=1, padx=5, pady=5, sticky='w')
        self.btnsave=tk.Button(self, text="save", command=self.save).grid(row=1,column=1,pady=5,sticky='n')
        self.btnask=tk.Button(self, text="save all data", command=self.file_save).grid(row=2, column=1, pady=5, padx=5, sticky='w')
        self.fig = plt.figure(figsize=[9,8])
        self.ax = self.fig.add_subplot(1,2,1)
        self.ax1 = self.fig.add_subplot(1,2,2)
        self.ax.set_xlabel('$f$ [GHz]')
        self.ax1.set_xlabel('$f$ [GHz]')
        self.ax.set_ylabel('S11 resistance [$\Omega$]')
        self.ax1.set_ylabel('S11 reactance [$\Omega$]')
        
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().grid(row=3, column=0, rowspan=5, columnspan=15)
        self.toolbarframe=tk.Frame(self)
        self.toolbarframe.grid(row=8, column=0, columnspan=6, sticky='nwe')
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.toolbarframe)
        self.toolbar.grid(row=9, column=0, columnspan=6, sticky='nwe')
        

        
    def docal(self):
        print("Calculating correction for given S11.")
        print("Calculating correction coefficients, the E's")
        Edf = S11l
        Erf = 2 * (S11o - S11l) * (S11l - S11s)/(S11o - S11s)
        Esf = (S11o - S11s - 2 * S11l)/(S11o - S11s)
        Z0 = 50
        S11a = (S11m - Edf)/((S11m - Edf) * Esf + Erf)
        Za = Z0 * (1 + S11a)/(1 - S11a)
        Resist, React = Za.real, Za.imag
        self.ax.plot(freq, S11a.real)
        self.ax1.plot(freq, S11a.imag)
        plt.ion()
        self.canvas.draw()

    def save(self):
        text=self.entry1.get()
        if text == "o":
            if 'S11o' in dir():
                print('Replacing prior calibration')
                S11o=S11
            else:
                S11o=S11
                print("S11o has been saved")
        elif text == "l":
            if 'S11l' in dir():
                print('Replacing prior calibration')
                S11l=S11
            else:
                S11l=S11
                print("S11l has been saved")
        elif text == "s":
            if 'S11s' in dir():
                print('Replacing prior calibration')
                S11s=S11
            else:
                S11s=S11
                print("S11s has been saved")
        elif text == "m":
            if S11o not in dir():
                print("Preform calibration for OPEN")
            elif S11l not in dir():
                print("Preform calibration for LOAD")
            elif S11s not in dir():
                print("Preform calibration for SHORT")
            else:
                S11m=S11
        else:
            print("Write in the entry which calibration took place!")

    def file_save(self):
        #files=[('All Files', '*.*'), ('Text Document', '*.')]

        f = tk.filedialog.asksaveasfile(mode="w", defaultextension="*.txt")
        intro="#FMR data, this file includes calibration measurements, correction factor and corrected S11\n"
        intro1="#S11a, S11m, S11o, S11l, S11s, Za, Edf, Erf, Esf\n"
        dataout=np.column_stack((S11a, S11m, S11o, S11l, S11s, Za, Edf, Erf, Esf))

        f.write(intro)
        f.write(intor1)
        f.write(dataout)



        f.write("þetta er flottur texti")
        f.close

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


class Page1(tk.Frame):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)
        self.labelsweep=tk.Label(self, text="Sweep setup", bg='white').grid(row=0, column=0, sticky="e")
        self.startpage=tk.Button(self, text="return", command=lambda : controller.show_frame(StartPage)).grid(row=0, column=1, pady=10, sticky='e')

        self.labelstart=tk.Label(self, text="Start", bg='white').grid(row=1, column=0, padx=5, pady=10, sticky="e")
        self.startentry=tk.Entry(self, width=5, bg='white')
        self.startentry.insert(0, "40")
        self.startentry.grid(row=1, column=1)
        
        self.labelunit=tk.Label(self, text="MHz", bg='white').grid(row=1, column=2)

        self.labelstop=tk.Label(self, text="Stop", bg='white').grid(row=1, column=3, padx=5, pady=5)
        self.stopentry=tk.Entry(self, width=5, bg='white')
        self.stopentry.insert(0, "20000")
        self.stopentry.grid(row=1, column=4)
        self.labelunit1=tk.Label(self, text="MHz", bg='white').grid(row=1, column=5)

        self.label4=tk.Label(self, text="Calibration setup", bg='white').grid(row=2, column=0)

        self.labelnumber=tk.Label(self, text="Nr. of measurements", bg='white').grid(row=3, column=1, columnspan=3, padx=5)
        self.numberentry=tk.Entry(self, width=5, bg='white')
        self.numberentry.insert(0, "10")
        self.numberentry.grid(row=3, column=2)

        self.setbtn=tk.Button(self, text="Set values", command=self.set_values).grid(row=4, column=0)

        
   
    def set_values(self):
        start=self.startentry.get()
        stop=self.stopentry.get()
        nave=self.numberentry.get()

class Page2(tk.Frame):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)

        self.label = tk.Label(self, text="Set magnetic flux", bg='white').grid(row=0, column=0, padx=5, pady=10)
        self.labelpar=tk.Label(self, text="Field parallel", bg='white').grid(row=1,column=0, padx=5, sticky="e")
        self.entrypar = tk.Entry(self,width=5, bg="white")
        self.entrypar.insert(0, "0")
        self.entrypar.grid(row=1, column=1)
        self.labelunitpar = tk.Label(self, text="G", bg='white').grid(row=1, column=2)

        self.btn=tk.Button(self, text="Reset magnet", command=self.zerofield).grid(row=1, column=4, padx=5)
        self.btn1= tk.Button(self, text="Set", command=self.writevolt).grid(row=1, column=3, padx=5)
        self.btnreturn=tk.Button(self, text="return", command=lambda : controller.show_frame(StartPage)).grid(row=0, column=4)

        self.labelper=tk.Label(self, text="Field perpendicular", bg='white').grid(row=2,column=0, padx=5, sticky="e")
        self.entryper = tk.Entry(self,width=5, bg="white")
        self.entryper.insert(0, "0")
        self.entryper.grid(row=2, column=1)
        self.labelunitper = tk.Label(self, text="G", bg='white').grid(row=2, column=2)

        self.btnper=tk.Button(self, text="Reset magnet", command=self.zerofield).grid(row=2, column=4, padx=5)
        self.btn1per= tk.Button(self, text="Set", command=self.writevolt).grid(row=2, column=3, padx=5)
    
        
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

        
class Page3(tk.Frame):

    def __init__(self, parent, controller):
        
        tk.Frame.__init__(self, parent)
        self.returnbut=tk.Button(self, text="return", command=lambda : controller.show_frame(StartPage)).grid(row=0, column=3, pady=10, padx=5)
        self.openbut=tk.Button(self, text="open", command=self.file_open).grid(row=0, column=1, pady=10, padx=5)
        self.plotting=tk.Button(self, text="plot", command=self.plot).grid(row=0, column=2)

        self.labelselect=tk.Label(self, text="Select array to plot: ").grid(row=0, column=0)
        self.listbox=tk.Listbox(self, width=8, height=5)
        self.listbox.grid(row=1, column=0)
        elements=["S11a", "S11m", "S11o", "S11l", "S11s", "Za", "Edf", "Erf", "Esf"]
        for i, ele in enumerate(elements):
            self.listbox.insert(i, ele)
            
        self.fig = plt.figure(figsize=[9,8])
        self.ax = self.fig.add_subplot(1,2,1)
        self.ax1 = self.fig.add_subplot(1,2,2)
        self.ax.set_xlabel('$f$ [GHz]')
        self.ax1.set_xlabel('$f$ [GHz]')
        self.ax.set_ylabel('S11 resistance [$\Omega$]')
        self.ax1.set_ylabel('S11 reactance [$\Omega$]')
        
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().grid(row=3, column=0, rowspan=5, columnspan=15, sticky='n')
        self.toolbarframe=tk.Frame(self)
        self.toolbarframe.grid(row=12, column=0, columnspan=6, sticky='nwe')
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.toolbarframe)
        self.toolbar.grid(row=13, column=0, columnspan=6, sticky='nwe')

    def file_open(self):

        f=tk.filedialog.askopenfilename()

    def plot(self):
        selected=self.listbox.curselection()
        print(selected)
        self.ax.clear()
        self.ax1.clear()
        #self.ax.plot(freq, S11.real)
        #self.ax1.plot(freq, S11.imag)
        self.canvas.draw()

        


def popup_bonus(self):
    l = tk.Label(self, text="Write \"open\", \"short\" and \"load\" for the corresponding measurements in the entry." )
    l.pack()
    b=tk.Button(self, text="Okay", command=win.destroy)
    b.pack()

def popup_showinfo():
    showinfo("Window", "Hello world!")



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
app = App()
app.mainloop()
