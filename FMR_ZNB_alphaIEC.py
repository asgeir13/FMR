import time
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
from tkinter.constants import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
# import pyvisa
import platform
import pandas as pd
import datetime
from scipy import signal, optimize
#import math
#from astropy import modeling
from lmfit.models import GaussianModel, LorentzianModel, SplitLorentzianModel, SplineModel, LinearModel, StepModel, QuadraticModel, PolynomialModel, ExponentialModel
import cmath
from reportlab.pdfgen.canvas import Canvas
from PIL import Image
import codecs
from lmfit import Minimizer, report_fit, Parameters, conf_interval, printfuncs
import matplotlib as cm
from scipy.optimize import fsolve, root

colors=cm.colormaps.get_cmap('tab20')
myos = platform.system()

#if myos=='Darwin':

#    from matplotlib.backend_bases import NavigationToolbar2

    #App class makes the frames and allows easy switching between them, frames are the different windows that pop up and cover the GUI,
    #calibrate, batch and viewer are "independent" frames

class App(tk.Tk):
    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.wm_title(self, "FMR")
        container = tk.Frame(self)
        container.pack(side=TOP,fill=BOTH,expand=True)#

        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)
        
        x, y = self.winfo_screenwidth(), self.winfo_screenheight()*0.8
        self.geometry("%dx%d+%d+%d" % (x,y,x/2-1200/2,y/2-600/2))

        self.frames = {}
        #for-loop to place each page in the container or parent page
        for F in (Measure, Calibrate, Batch, Viewer2, IEC):

            frame = F(container, self)

            self.frames[F] = frame


            frame.grid(row = 0, column = 0, sticky="nsew")

        self.show_frame(Viewer2)
        #raises the page to the top with tkraise()
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
        
    try:
        try:
            tk.Tk.call('tk_getOpenFile', '-foobarbaz')
        except TclError:
            pass
        tk.TK.call('set','::tk::dialog::file:showHiddenBtn','-1')
    except:
        pass
    #this is the main page
class Measure(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
       
        self.buttonframe=tk.Frame(self)
        self.buttonframe.grid(row=0,column=11,rowspan=2, columnspan=2,sticky='wn')
        tk.Button(self.buttonframe, text="Measure", command=lambda: controller.show_frame(Measure), width=8, height=1, font=fontconf).grid(row=0,column=0,padx=5)
        tk.Button(self.buttonframe, text="Viewer", command=lambda: controller.show_frame(Viewer2), width=8, height=1, font=fontconf).grid(row=0,column=1)
        tk.Button(self.buttonframe, text="Batch", command=lambda: controller.show_frame(Batch), width=8, height=1, font=fontconf).grid(row=1, column=0, sticky='n', padx=5)
        tk.Button(self.buttonframe, text="Calibrate", command=lambda: controller.show_frame(Calibrate), width=8, height=1, font=fontconf).grid(row=1,column=1, sticky='n')
        self.buttonframe.columnconfigure(0,weight=1)
        self.buttonframe.columnconfigure(1,weight=1)
        tk.Button(self, text="Exit", command=self._quit, font=fontconf).grid(row=0, column=19,sticky='ne')

        self.fig = plt.figure(constrained_layout=True, figsize=[5,5])
        gs1 = self.fig.add_gridspec(nrows=1, ncols=2, left=0.1, right=0.95, wspace=0.3)
        self.ax = self.fig.add_subplot(gs1[0,0])
        self.ax1 = self.fig.add_subplot(gs1[0,1])
        self.ax.set_xlabel('$f$ [Hz]')
        self.ax1.set_xlabel('$f$ [Hz]')
        self.ax.set_ylabel('S11 resistance [\u03A9]')
        self.ax1.set_ylabel('S11 reactance [\u03A9]')
        self.canvas=FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().grid(row=0, column=0, rowspan=30, columnspan=10, sticky='nwse')
        self.toolbarframe=tk.Frame(self)
        self.toolbarframe.grid(row=31, column=0, columnspan=10, sticky='nswe')
        self.toolbar=NavigationToolbar2Tk(self.canvas, self.toolbarframe)
        self.toolbar.grid(row=0, column=0, columnspan=10, sticky='nswe')
        self.canvas.draw_idle()
                
        tk.Label(self, text="Set magnetic field",relief='ridge',font=fontconf).grid(row=3, column=13)
        self.magfield=tk.Frame(self)
        self.magfield.grid(row=4,column=13, rowspan=3,columnspan=6)
        tk.Label(self.magfield, text="Parallel",font=fontconf).grid(row=0,column=0,sticky='e')
        self.entrypar = tk.Entry(self.magfield,width=5)
        self.entrypar.insert(0, "0")
        self.entrypar.grid(row=0, column=1)
        tk.Label(self.magfield, text="G").grid(row=0, column=2, sticky='w')

        tk.Label(self.magfield, text="Perpendicular",font=fontconf).grid(row=1,column=0,sticky='e')
        self.entryper = tk.Entry(self.magfield,width=5)
        self.entryper.insert(0, "0")
        self.entryper.grid(row=1, column=1)
        tk.Label(self.magfield, text="G").grid(row=1, column=2,sticky='w')

        tk.Label(self.magfield, text="Magnitude",font=fontconf).grid(row=0, column=3,sticky='e')
        self.entrymag = tk.Entry(self.magfield, width=5)
        self.entrymag.insert(0, "0")
        self.entrymag.grid(row=0, column=4, sticky='e')
        tk.Label(self.magfield, text="G").grid(row=0, column=5, sticky='w')
        tk.Label(self.magfield, text="Angle",font=fontconf).grid(row=1, column=3,sticky='e')
        self.entryang = tk.Entry(self.magfield, width=5)
        self.entryang.insert(0, "0")
        self.entryang.grid(row=1, column=4, sticky='e')
        tk.Label(self.magfield, text="°").grid(row=1, column=5, sticky='w')

        tk.Button(self.magfield, text="Reset", command=self.zerofield, font=fontconf).grid(row=2, column=2,columnspan=2,sticky='w')
        tk.Button(self.magfield, text="Set", command=self.writevolt, width=2, font=fontconf).grid(row=2, column=1, sticky='e')
         
        self.scanframe=tk.Frame(self)
        self.scanframe.grid(row=7,column=13, rowspan=3,columnspan=6)
        tk.Button(self.scanframe, text="Scan", command=self.takecal, font=fontconf).grid(row=4, column=0, sticky='e')
        tk.Button(self.scanframe, text="Save", command=self.file_save, font=fontconf).grid(row=4, column=1)
        
        tk.Button(self.scanframe, text="Stop", command=self.stop_run, font=fontconf).grid(row=4, column=2)


        self.status=tk.Listbox(self, width=30, height=7, bg='#E0E0E0', bd=2)
        self.status.grid(row=18, column=13, rowspan=3, columnspan=5)
        self.status.yview(END)
       
        for i in np.arange(0,11):
            #self.rowconfigure(i, weight=1)
            self.columnconfigure(i,weight=1)

        for i in range(0,5):
            self.scanframe.rowconfigure(i,weight=1)

        for i in np.arange(0,33):
            self.rowconfigure(i, weight=1)

    def _quit(self):
        app.quit()
        app.destroy()
    
    def stop_run(self):
        self.run=False

        #saves all the arrays, filedialog.asksaveasfile creates pop up save window
    def file_save(self):
        f = tk.filedialog.asksaveasfile(initialdir='/home/at/FMRmaelingar', mode="w", defaultextension="*.txt")
        intro=f"#FMR data, this file includes calibration measurements, correction factor and corrected S11, Number of measurments: {nave+1}, number of points {nfpoints}, IF BW {IF_BW}\nfreq\tS11a\tS11m\tS11o\tS11l\tS11s\tZa\tEdf\tErf\tEsf\tI"
        #intro2=f"#Notes: {self.notes.get('1.0','end')}"
        currarray=np.empty(len(self.S11a))
        currarray[:]=np.nan
        fmt='%.5e'
        for x, n in enumerate(self.current):
            currarray[x]=n
        dataout=np.column_stack((self.freq, self.S11a, self.S11m, S11o, S11l, S11s, self.Za, Edf, Erf, Esf, currarray))
        np.savetxt(f, dataout, delimiter='\t', header=intro, fmt=fmt, comments='')
        
        #use open, short, load to calibrate the measurement   
    def docal(self):
        global Edf, Erf, Esf, Z0
        Edf = S11l
        Erf = 2 * (S11o - S11l) * (S11l - S11s)/(S11o - S11s)
        Esf = (S11o + S11s - 2 * S11l)/(S11o - S11s)
        Z0 = 50
        self.S11a = (self.S11m - Edf)/((self.S11m - Edf) * Esf + Erf)
        self.Za = Z0 * (1 + self.S11a)/(1 - self.S11a)
      
    def takecal(self):
        self.run=True  #enable the stop function, when the stop function is called self.run=False and the for loop stops
        self.S11m = np.zeros(nfpoints, dtype=np.complex128)
        real_p, imag_p, self.freq, self.current = self.measure()
        plt.ion() #enable interactive plotting
        self.S11m=real_p+1j*imag_p
        self.docal() #run docal function to receive Za and S11a
        self.ax.clear()
        self.ax1.clear()
        self.ax.set_xlabel('$f$ [Hz]')
        self.ax1.set_xlabel('$f$ [Hz]')
        self.ax.set_ylabel('$Z_a$ resistance [\u03A9]')
        self.ax1.set_ylabel('$Z_a$ reactance [\u03A9]')
        self.ax.plot(self.freq, self.Za.real)
        self.ax1.plot(self.freq, self.Za.imag)
        self.canvas.draw_idle()  #enables gentile plotting, doesn't interupt the GUI's internal loops
        self.canvas.flush_events()
        self.status.insert(END, 'Measurement complete')
        self.status.yview(END)

    def measure(self):
        self.current_measurement()
        curr=self.current
        inst.write_str_with_opc('INIT2:IMM')
        valu=inst.query_str("CALC2:DATA:TRAC? 'Trc2', SDAT")
        values=np.array([float(x) for x in valu.rsplit(',')])
        self.current_measurement()
        self.current=np.append(curr,self.current)
        real=values[0:-1:2]
        imag=values[1::2]
        start=float(inst.query_str("SENS2:FREQ:STAR?"))
        stop=float(inst.query_str("SENS2:FREQ:STOP?"))
        point=int(inst.query_str("SENS2:SWEEP:POINTS?"))
        step=float(inst.query_str("SENS2:SWEEP:STEP?"))
        freq=np.linspace(start,stop,num=point)
        return real, imag, freq, self.current

    def current_measurement(self):
        iterations=30
        if multimeter==0:
            self.current=np.empty(iterations,dtype=float)
        else:
            self.current=np.empty(iterations,dtype=float)
            t=0
            while t<iterations:
                string=instCurr.read()
                print(string)
                self.current[t]=float(eval(string.split(',')[0]))
                time.sleep(0.05)
                t+=1

 
    #set the magnetic field. FH are values read from a calibration file, which can be updated 
    def writevolt(self):
        val = float(self.entrypar.get())
        val1 = float(self.entryper.get())
        if int(val)==0 and int(val1)==0:
            mag = int(self.entrymag.get())
            ang = int(self.entryang.get())
            val, val1=mag*np.cos(ang*np.pi/180), mag*np.sin(ang*np.pi/180)
     
        self.status.insert(END, f'Parallel set to: {round(val,2)} G')
        self.status.insert(END, f'Perpendicular set to: {round(val1,2)} G')
        self.status.yview(END)
           
        val, val1 = float(val)*FH1[0]+FH1[1], float(val1)*FH[0]+FH[1]
        if multimeter==1 and abs(val)>9.3:
            self.entrypar.delete(0, END)
            self.entrypar.insert(0, 0)
            val=0
            self.status.insert(END, 'Multimeter is connected, lower the magnetic field')
            self.staus.yview(END)
        print(val)
        if ((val < -10) | (val > 10) | (val1<-10) | (val1 > 10)).any():
            val, val1 = 0, 0
            print('Input value not available')
            self.status.insert(END, 'Input value not available')

        with nidaqmx.Task() as task:
            task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
            task.ao_channels.add_ao_voltage_chan('Dev1/ao1')
            task.write([val,val1])

        print(f"Value set to: {val}")
        print(f"Value set to: {val1}") 
        #reset the magnet
    def zerofield(self):
        self.entryper.delete(0, END)
        self.entryper.insert(0, "0")
        self.entrypar.delete(0, END)
        self.entrypar.insert(0, "0")
        self.entrymag.delete(0, END)
        self.entryang.delete(0, END)
        self.entrymag.insert(0, "0")
        self.entryang.insert(0, "0")
        
        with nidaqmx.Task() as task:
            task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
            task.ao_channels.add_ao_voltage_chan('Dev1/ao1')
            task.write([0,0])

        print(f'Resetting DAQs to zero')
        self.status.insert(END, f'Resetting DAQs to zero')
        self.status.yview(END)

    #page to set the initial values
class Calibrate(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.fig = plt.figure(constrained_layout=True, figsize=[10,4.5])
        gs1 = self.fig.add_gridspec(nrows=1, ncols=2, left=0.1, right=0.95, wspace=0.3)
        self.ax = self.fig.add_subplot(gs1[0,0])
        self.ax1 = self.fig.add_subplot(gs1[0,1])
        self.ax.set_xlabel('$f$ [Hz]')
        self.ax1.set_xlabel('$f$ [Hz]')
        self.ax.set_ylabel('S11 resistance [\u03A9]')
        self.ax1.set_ylabel('S11 reactance [\u03A9]')
        self.canvas=FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().grid(row=0, column=0, rowspan=30, columnspan=10, sticky='nwse')
        self.toolbarframe=tk.Frame(self)
        self.toolbarframe.grid(row=31, column=0, columnspan=10, sticky='nswe')
        self.toolbar=NavigationToolbar2Tk(self.canvas, self.toolbarframe)
        self.toolbar.grid(row=0, column=0, columnspan=10, sticky='nswe')
        self.canvas.draw_idle()
        
        self.buttonframe=tk.Frame(self)
        self.buttonframe.grid(row=0,column=11, columnspan=2,rowspan=2,sticky='wn')
        tk.Button(self.buttonframe, text="Measure", command=lambda: controller.show_frame(Measure), width=8, height=1, font=fontconf).grid(row=0,column=0,padx=5)
        tk.Button(self.buttonframe, text="Viewer", command=lambda: controller.show_frame(Viewer2), width=8, height=1, font=fontconf).grid(row=0,column=1)
        tk.Button(self.buttonframe, text="Batch", command=lambda: controller.show_frame(Batch), width=8, height=1, font=fontconf).grid(row=1, column=0, sticky='n', padx=5)
        tk.Button(self.buttonframe, text="Calibrate", font=fontconf, command=lambda: controller.show_frame(Calibrate), width=8, height=1).grid(row=1,column=1, sticky='n')
        self.buttonframe.columnconfigure(0,weight=1)
        self.buttonframe.columnconfigure(1,weight=1)
        tk.Button(self, text="Exit", command=self._quit, font=fontconf).grid(row=0, column=18, sticky='ne')
        self.scanframe=tk.Frame(self)
        self.scanframe.grid(row=7,column=13,columnspan=3)#row=2,column=13,rowspan=7,columnspan=6,sticky='ne'
        tk.Button(self.scanframe, text="Scan", command=self.takecal, font=fontconf).grid(row=0, column=0)
        self.listbox=tk.Listbox(self.scanframe, height=2, width=6)
        self.listbox.grid(row=0,column=1)
        elements=['Open', 'Load', 'Short']
        for i, ele in enumerate(elements):
            self.listbox.insert(i, ele)

        tk.Button(self.scanframe, text="save", command=self.save,font=fontconf).grid(row=0,column=2, columnspan=2)
        
        tk.Label(self, text="Set magnetic field",relief='ridge',font=fontconf).grid(row=3, column=13)
        self.magfield=tk.Frame(self)
        self.magfield.grid(row=4,column=13, rowspan=3,columnspan=6)
        tk.Label(self.magfield, text="Parallel",font=fontconf).grid(row=0,column=0,sticky='e')
        self.entrypar = tk.Entry(self.magfield,width=5)
        self.entrypar.insert(0, "0")
        self.entrypar.grid(row=0, column=1)
        tk.Label(self.magfield, text="G").grid(row=0, column=2, sticky='w')

        tk.Label(self.magfield, text="Perpendicular",font=fontconf).grid(row=1,column=0,sticky='e')
        self.entryper = tk.Entry(self.magfield,width=5)
        self.entryper.insert(0, "0")
        self.entryper.grid(row=1, column=1)
        tk.Label(self.magfield, text="G").grid(row=1, column=2,sticky='w')

        tk.Label(self.magfield, text="Magnitude",font=fontconf).grid(row=0, column=3,sticky='e')
        self.entrymag = tk.Entry(self.magfield, width=5)
        self.entrymag.insert(0, "0")
        self.entrymag.grid(row=0, column=4, sticky='e')
        tk.Label(self.magfield, text="G").grid(row=0, column=5, sticky='w')
        tk.Label(self.magfield, text="Angle",font=fontconf).grid(row=1, column=3,sticky='e')
        self.entryang = tk.Entry(self.magfield, width=5)
        self.entryang.insert(0, "0")
        self.entryang.grid(row=1, column=4, sticky='e')
        tk.Label(self.magfield, text="°").grid(row=1, column=5, sticky='w')

        tk.Button(self.magfield, text="Reset", command=self.zerofield, font=fontconf, width=4).grid(row=2, column=2,columnspan=2,sticky='w')
        tk.Button(self.magfield, text="Set", command=self.writevolt, width=3, font=fontconf).grid(row=2, column=1, sticky='e')
        tk.Button(self.magfield, text="Init. meter", command=self.start_currmeasurement, width=8, font=fontconf).grid(row=2, column=3,columnspan=2,sticky='e')


        
        self.sweepframe=tk.Frame(self)
        self.sweepframe.grid(row=9,column=13,columnspan=4,rowspan=5)
        tk.Label(self, text="Sweep setup", relief='ridge', font=fontconf).grid(row=8, column=13)
        
        tk.Label(self.sweepframe, text="Start", font=fontconf).grid(row=0, column=0,sticky='e')
        self.startentry=tk.Entry(self.sweepframe, width=5)
        self.startentry.insert(0, "40")
        self.startentry.grid(row=0, column=1)
        tk.Label(self.sweepframe, text="MHz").grid(row=0, column=2)

        tk.Label(self.sweepframe, text="Stop", font=fontconf).grid(row=1, column=0,sticky='e')
        self.stopentry=tk.Entry(self.sweepframe, width=5)
        self.stopentry.insert(0, "5000")
        self.stopentry.grid(row=1, column=1)
        tk.Label(self.sweepframe, text="MHz").grid(row=1, column=2)

        tk.Label(self.sweepframe, text="Nr. of meas.", font=fontconf).grid(row=2, column=0,sticky='e')
        self.numberentry=tk.Entry(self.sweepframe, width=5)
        self.numberentry.insert(0, "1")
        self.numberentry.grid(row=2, column=1)

        tk.Label(self.sweepframe, text="Data points", font=fontconf).grid(row=3,column=0,sticky='e')
        self.pointsbox=tk.Entry(self.sweepframe, width=6)
        self.pointsbox.insert(0, "2000")
        self.pointsbox.grid(row=3, column=1)
        self.pointlist=["51", "101", "201", "401", "801", "1601"]
        #tk.Button(self.sweepframe, text="+", width=2, command=lambda: self._up(0), font=fontconf).grid(row=3, column=3)
        #tk.Button(self.sweepframe, text="-", width=2, command=lambda: self._down(0), font=fontconf).grid(row=3,column=2)

        tk.Label(self.sweepframe, text="IF BW", font=fontconf).grid(row=4, column=0,sticky='e')
        self.IF_list=["10 Hz", "100 Hz", "1 kHz", "10 kHz"]
        self.IF_BW=tk.Entry(self.sweepframe,width=6)
        self.IF_BW.insert(0,"100 Hz")
        self.IF_BW.grid(row=4, column=1)
        #tk.Button(self.sweepframe, text="+", width=2, command=lambda: self._up(1), font=fontconf).grid(row=4, column=3)
        #tk.Button(self.sweepframe, text="-", width=2, command=lambda: self._down(1), font=fontconf).grid(row=4,column=2)
        tk.Button(self.sweepframe, text="Set values", width=8, command=self.set_values, font=fontconf).grid(row=1, column=4)
        self.status=tk.Listbox(self, width=30, height=7, bg='#E0E0E0', bd=2)
        self.status.grid(row=18, column=13, rowspan=3, columnspan=5)
        self.status.yview(END)

        for i in range(0,5):

            self.sweepframe.columnconfigure(i, weight=1)
            #self.sweepframe.rowconfigure(i, weight=1)
        
        for i in np.arange(0,33):
            self.rowconfigure(i, weight=1)
       
        for i in range(0,18):
            self.columnconfigure(i,weight=1)
    
    
    def start_currmeasurement(self):
        multimeter=0
        try:
            multimeter=1
            rm=pyvisa.ResourceManager()
            instCurr=rm.open_resource('GPIB0::17::INSTR')
            instCurr.write('F5R5S2T0Y1')
        except:
            print('Multimeter not responding')


        #save each measurement to it's corresponding variable
    def save(self):
        global S11o, S11l, S11s
        number=self.listbox.curselection()[0]
        if number == 0:
            if "S11o" in savelist:
                print('Replacing prior calibration')
                self.status.insert(END, 'Replacing prior calibration')
                S11o=self.S11m
            else:
                S11o=self.S11m
                savelist.append("S11o")
                print("S11o has been saved")
                self.status.insert(END, "S11o has been saved")
                print(savelist)
        elif number == 1:
            if 'S11l' in savelist:
                print('Replacing prior calibration')
                self.status.insert(END, 'Replacing prior calibration')
                S11l=self.S11m
            else:
                S11l=self.S11m
                savelist.append("S11l")
                print(savelist)
                print("S11l has been saved")
                self.status.insert(END, "S11l has been saved")
        elif number == 2:
            if 'S11s' in savelist:
                print('Replacing prior calibration')
                self.status.insert(END, 'Replacing prior calibration')
                S11s=self.S11m
            else:
                S11s=self.S11m
                savelist.append("S11s")
                print(savelist)
                print("S11s has been saved")
                self.status.insert(END, "S11s has been saved")
        elif number == 3:
            if "S11o" not in savelist:
                print("Perform calibration for OPEN")
                self.status.insert(END, "Perform calibration for OPEN")
            elif "S11l" not in savelist:
                print("Perform calibration for LOAD")
                self.status.insert(END, "Perform calibration for LOAD")
            elif "S11s" not in savelist:
                print("Perform calibration for SHORT")
                self.status.insert(END, "Perform calibration for SHORT")
            else:
                print("S11m has been saved")
                self.status.insert(END, 'S11m has been saved')
        else:
            print("Write in the entry which calibration took place!")

        self.status.yview(END)
            

    def _quit(self):
        app.quit()
        app.destroy()

    def set_values(self):
        global nave, nfpoints, IF_BW, timi
        start=self.startentry.get()
        stop=self.stopentry.get()
        start="STAR "+start+"e6"
        stop="STOP "+stop+"e6"
        freqstring="SENS2:FREQ:"+start+"; "+stop
        inst.write_with_opc(freqstring)
        #set IF_BW value
        IF_BW=self.IF_BW.get()
        inst.write_with_opc(f"SENS2:BAND {IF_BW}")
        ask=inst.query_with_opc("SENS2:BAND?")
        self.status.insert(END, f"IF BW: {ask}")
        #number of data points set, 
        inst.write_with_opc("SENS2:SWE:POIN "+self.pointsbox.get())
        nfpoints=int(self.pointsbox.get())
        inst.write_with_opc(f"SENS2:SWEEP:COUN {self.numberentry.get()}")
        count=inst.query_with_opc('SENS2:SWEEP:COUN?')
        self.status.insert(END,f"Count: {count}")
        nave=int(self.numberentry.get())-1
        inst.write_with_opc("SENS2:SWE:TIME:AUTO ON")
        timi=inst.query_with_opc("SENS2:SWE:TIME?")
        timi=float(timi)*float(count)
        print(f'Timi skanns {timi}')
        self.status.insert(END, 'Setting current values')
        self.status.yview(END)


        #set the magnetic field. FH are values read from a calibration file, which can be updated 
    def writevolt(self):
        val = float(self.entrypar.get())
        val1 = float(self.entryper.get())
        if int(val)==0 and int(val1)==0:
            mag = int(self.entrymag.get())
            ang = int(self.entryang.get())
            val, val1=mag*np.cos(ang*np.pi/180), mag*np.sin(ang*np.pi/180)
     
        self.status.insert(END, f'Parallel set to: {round(val,2)} G')
        self.status.insert(END, f'Perpendicular set to: {round(val1,2)} G')
        self.status.yview(END)

        val, val1 = float(val)*FH1[0]+FH1[1], float(val1)*FH[0]+FH[1]
        print(val)
        if ((val < -10) | (val > 10) | (val1<-10) | (val1 > 10)).any():
            val, val1 = 0, 0
            print('Input value not available')
            self.status.insert(END, 'Input value not available')

        with nidaqmx.Task() as task:
            task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
            task.ao_channels.add_ao_voltage_chan('Dev1/ao1')
            task.write([val,val1])

        print(f"Value set to: {val}")
        print(f"Value set to: {val1}") 
        #reset the magnet
    def zerofield(self):
        self.entryper.delete(0, END)
        self.entryper.insert(0, "0")
        self.entrypar.delete(0, END)
        self.entrypar.insert(0, "0")
        self.entrymag.delete(0, END)
        self.entryang.delete(0, END)
        self.entrymag.insert(0, "0")
        self.entryang.insert(0, "0")
        
        with nidaqmx.Task() as task:
            task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
            task.ao_channels.add_ao_voltage_chan('Dev1/ao1')
            task.write([0,0])

        print(f'Resetting DAQs to zero')
        self.status.insert(END, f'Resetting DAQs to zero')
        self.status.yview(END)


        #receiving measurements from the network analyzer
    def measure(self):
        inst.write_str_with_opc('INIT2:IMM')
        valu=inst.query_str("CALC2:DATA:TRAC? 'Trc2', SDAT")
        values=np.array([float(x) for x in valu.rsplit(',')])
        real=values[0:-1:2]
        imag=values[1::2]
        start=float(inst.query_str("SENS2:FREQ:STAR?"))
        stop=float(inst.query_str("SENS2:FREQ:STOP?"))
        point=int(inst.query_str("SENS2:SWEEP:POINTS?"))
        step=float(inst.query_str("SENS2:SWEEP:STEP?"))
        freq=np.linspace(start,stop,num=point)
        return real, imag, freq

    def takecal(self):
        self.S11m = np.zeros(nfpoints, dtype=np.complex128)
        real_p, imag_p, self.freq = self.measure()
        plt.ion()
        self.S11m=real_p+1j*imag_p
        self.ax.clear()
        self.ax1.clear()
        self.ax.set_xlabel('$f$ [Hz]')
        self.ax1.set_xlabel('$f$ [Hz]')
        self.ax.set_ylabel('S11 resistance [\u03A9]')
        self.ax1.set_ylabel('S11 reactance [\u03A9]')
        self.ax.plot(self.freq, self.S11m.real)
        self.ax1.plot(self.freq, self.S11m.imag)
        self.canvas.draw_idle()
        self.canvas.flush_events()
        self.status.insert(END, 'Measurement complete')
        self.status.yview(END)


class Batch(tk.Frame):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)
        self.buttonframe=tk.Frame(self)
        self.buttonframe.grid(row=0,column=11, columnspan=2,rowspan=2,sticky='wn')
        tk.Button(self.buttonframe, text="Measure", command=lambda: controller.show_frame(Measure), width=8, height=1, font=fontconf).grid(row=0,column=0,padx=5)
        tk.Button(self.buttonframe, text="Viewer", command=lambda: controller.show_frame(Viewer2), width=8, height=1, font=fontconf).grid(row=0,column=1)
        tk.Button(self.buttonframe, text="Batch", command=lambda: controller.show_frame(Batch), width=8, height=1, font=fontconf).grid(row=1, column=0, sticky='n', padx=5)
        tk.Button(self.buttonframe, text="Calibrate", command=lambda: controller.show_frame(Calibrate), width=8, height=1, font=fontconf).grid(row=1,column=1, sticky='n')
        self.buttonframe.columnconfigure(0,weight=1)
        self.buttonframe.columnconfigure(1,weight=1)
        tk.Button(self, text="Exit", command=self._quit, font=fontconf).grid(row=0, column=18,sticky='ne')

        self.fig = plt.figure(constrained_layout=True, figsize=[10,4.5])
        gs1 = self.fig.add_gridspec(nrows=1, ncols=2, left=0.1, right=0.95, wspace=0.3)
        self.ax = self.fig.add_subplot(gs1[0,0])
        self.ax1 = self.fig.add_subplot(gs1[0,1])
        self.ax.set_xlabel('$f$ [Hz]')
        self.ax1.set_xlabel('$f$ [Hz]')
        self.ax.set_ylabel('S11 resistance [\u03A9]')
        self.ax1.set_ylabel('S11 reactance [\u03A9]')

        self.canvas=FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().grid(row=0, column=0, rowspan=30, columnspan=10, sticky='nwse')
        self.toolbarframe=tk.Frame(self)
        self.toolbarframe.grid(row=31, column=0, columnspan=10, sticky='nswe')
        self.toolbar=NavigationToolbar2Tk(self.canvas, self.toolbarframe)
        self.toolbar.grid(row=0, column=0, columnspan=10, sticky='nswe')
        self.canvas.draw_idle()
        
        tk.Label(self, text="Sweep magnetic field", relief='ridge', font=fontconf).grid(row=3,column=14)
        self.batchframe=tk.Frame(self)
        self.batchframe.grid(row=4, column=13, rowspan=8, columnspan=8, sticky='n')
        tk.Label(self.batchframe, text="Parallel",relief='ridge', font=fontconf).grid(row=0, column=0, columnspan=2)
        tk.Label(self.batchframe, text="Angular",relief='ridge', font=fontconf).grid(row=0, column=4, columnspan=2)
        tk.Label(self.batchframe, text="Magnitude", font=fontconf).grid(row=1, column=4)
        self.mag = tk.Entry(self.batchframe, width=5)
        self.mag.insert(0, "0")
        self.mag.grid(row=1, column=5)
        tk.Label(self.batchframe, text="G").grid(row=1, column=6)

        tk.Label(self.batchframe, text="Start", font=fontconf).grid(row=2, column=0)
        self.start = tk.Entry(self.batchframe,width=5)
        self.start.insert(0, "0")
        self.start.grid(row=2, column=1)
        tk.Label(self.batchframe, text="G").grid(row=2, column=2)
        tk.Label(self.batchframe, text="Stop", font=fontconf).grid(row=3, column=0)
        self.stop = tk.Entry(self.batchframe,width=5)
        self.stop.insert(0, "0")
        self.stop.grid(row=3, column=1)
        tk.Label(self.batchframe, text="G").grid(row=3, column=2)
        tk.Label(self.batchframe,text="Step", font=fontconf).grid(row=4,column=0)
        self.step = tk.Entry(self.batchframe, width=5)
        self.step.insert(0,"0")
        self.step.grid(row=4, column=1)
        tk.Label(self.batchframe,text="G").grid(row=4, column=2)
        tk.Label(self.batchframe, text="Start", font=fontconf).grid(row=2, column=4,sticky='e')
        self.startang = tk.Entry(self.batchframe, width=5)
        self.startang.insert(0, "0")
        self.startang.grid(row=2, column=5)
        tk.Label(self.batchframe, text="°", font=fontconf).grid(row=2, column=6)
        tk.Label(self.batchframe, text="Step", font=fontconf).grid(row=3, column=4,sticky='e')
        self.stepang = tk.Entry(self.batchframe, width=5)
        self.stepang.insert(0, "0")
        self.stepang.grid(row=3, column=5)
        tk.Label(self.batchframe, text="°", font=fontconf).grid(row=3, column=6)
        tk.Label(self.batchframe, text="Stop", font=fontconf).grid(row=4, column=4,sticky='e')
        self.stopang = tk.Entry(self.batchframe, width=5)
        self.stopang.insert(0, "0")
        self.stopang.grid(row=4, column=5)
        tk.Label(self.batchframe, text="°", font=fontconf).grid(row=4, column=6)
        tk.Label(self.batchframe, text="String{start,end,step:..}", font=fontconf).grid(row=5,column=0,columnspan=2)
        self.vector = tk.Entry(self.batchframe, width=14)
        self.vector.grid(row=5,column=2,columnspan=4)
        self.offvar=tk.IntVar()
        self.offvar.set(0)
        self.offsetCB=tk.Checkbutton(self.batchframe,text='Offset',font=fontconf,variable=self.offvar).grid(row=6,column=0)
        self.offset = tk.Entry(self.batchframe,width=4)
        self.offset.grid(row=6,column=2)

        self.blankframe=tk.Frame(self)
        self.blankframe.grid(row=11,column=14,rowspan=2,columnspan=4)
        tk.Button(self.blankframe, text="Blank scan", command=self.blankscan, font=fontconf).grid(row=0,column=0)
        tk.Label(self.blankframe, text="Start [°]", font=fontconf).grid(row=1,column=0,sticky='e')
        tk.Label(self.blankframe, text="Stop [°]", font=fontconf).grid(row=1,column=2)
        self.startangle=tk.Entry(self.blankframe,width=4)
        self.stopangle=tk.Entry(self.blankframe,width=4)
        self.startangle.insert(0,"0")
        self.stopangle.insert(0,"0")
        self.startangle.grid(row=1,column=1)
        self.stopangle.grid(row=1,column=3)

        self.scanframe=tk.Frame(self)
        self.scanframe.grid(row=13,column=14, rowspan=2, columnspan=4)
        tk.Button(self.scanframe, text="Calc", command=self.calcvect, font=fontconf).grid(row=1, column=0)
        tk.Button(self.scanframe, text="Scan", command=self.batchscan, font=fontconf).grid(row=2, column=0)
        tk.Button(self.scanframe, text="Save", command=self.file_save, font=fontconf).grid(row=1, column=1)
        tk.Button(self.scanframe, text="Stop", command=self.stop_run, font=fontconf).grid(row=2, column=1)
        tk.Button(self.scanframe, text="Clear", command=self.clear, font=fontconf).grid(row=1, column=2, columnspan=2)
        self.status=tk.Listbox(self, width=30, height=7, bg='#E0E0E0', bd=2)
        self.status.grid(row=18, column=13, rowspan=3, columnspan=5)

        for i in np.arange(0,33):
           self.rowconfigure(i, weight=1)

        for i in range(0,18):
            self.columnconfigure(i,weight=1)

    def clear(self):
        self.start.delete(0,END)
        self.stop.delete(0,END)
        self.step.delete(0,END)
        self.startang.delete(0,END)
        self.stopang.delete(0,END)
        self.stepang.delete(0,END)
        self.mag.delete(0,END)
        self.start.insert(0,'0')
        self.stop.insert(0,'0')
        self.step.insert(0,'0')   
        self.startang.insert(0,'0')
        self.stopang.insert(0,'0')
        self.stepang.insert(0,'0')
        self.mag.insert(0,'0')

    def stop_run(self):
        self.run=False

    def _quit(self):
        app.quit()
        app.destroy()

    def calcvect(self):
        #try:
            if int(self.stepang.get())!=0:
                step = float(self.stepang.get())
                self.angles = np.arange(float(self.startang.get())*np.pi/180, (float(self.stopang.get())+step)*np.pi/180, step*np.pi/180)
                print(self.angles)
                self.status.insert(END, f'{np.arange(float(self.startang.get()),float(self.stopang.get())+step, step)}')
                self.status.yview(END)
                mag = float(self.mag.get())
                if multimeter==1 and mag>120:
                    self.status.insert(END, 'Multimeter is connected, lower the magnetic field')
                    self.staus.yview(END)
                else:
                    par=[mag*np.cos(element)*FH1[0]+FH1[1] for n, element in enumerate(self.angles)]
                    per=[mag*np.sin(element)*FH[0]+FH[1] for n, element in enumerate(self.angles)]
                    self.values=np.row_stack((par,per))
                    self.type="ang"
            elif int(self.step.get())!=0:
                step = float(self.step.get())
                self.values=np.arange(float(self.start.get()), float(self.stop.get())+float(step), float(step))
                if multimeter==1 and np.max(self.values)>190:

                    self.status.insert(END, 'Multimeter is connected, lower the magnetic field')
                    self.staus.yview(END) 
                else:
                    if self.offvar.get()==0:
                        self.status.insert(END, f'{self.values}')
                        self.values=[element*FH1[0]+FH1[1] for n, element in enumerate(self.values)]
                        self.type="parallel"

                    else:
                        element=float(self.offset.get())*np.pi/180
                        self.status.insert(END, f'{self.values*np.cos(element)}')
                        par=[mag*np.cos(element)*FH1[0]+FH1[1] for n, mag in enumerate(self.values)]
                        per=[mag*np.sin(element)*FH[0]+FH[1] for n, mag in enumerate(self.values)]
                        self.values=np.row_stack((par,per))
                        self.type="Offset"

            
            elif self.vector.get()!='':
                print(self.vector.get())
                for n, i in enumerate(self.vector.get().split(':')):
                    print(n)
                    print(i)
                    if n==0:
                        mag=float(i)
                        if multimeter==1 and mag>120:
                            self.status.insert(END, 'Multimeter is connected, lower the magnetic field')
                            self.staus.yview(END)
 
                    elif n==1:
                        start=float(i.split(',')[0])
                        end=float(i.split(',')[1])
                        step=float(i.split(',')[2])
                        self.angles=np.arange(start,end,step)
                    else:
                        start=float(i.split(',')[0])
                        end=float(i.split(',')[1])
                        step=float(i.split(',')[2])
                        print(np.arange(start,end,step))
                        self.angles=np.append(self.angles, np.arange(start,end,step))
                self.status.insert(END, self.angles)
                self.status.yview(END)
                self.angles=self.angles*np.pi/180
                par=[mag*np.cos(element)*FH1[0]+FH1[1] for n, element in enumerate(self.angles)]
                per=[mag*np.sin(element)*FH[0]+FH[1] for n, element in enumerate(self.angles)]
                self.values=np.row_stack((par,per))
                self.type="ang"

        # except:
        #     print('Dividing by zero')
        #     self.status.insert(END, 'Dividing by zero')
        #     self.status.yview(END)
    
        #set the magnetic field. FH are values read from a calibration file, which can be updated 
    def writevolt(self):
        if len(self.values)==2 or self.blank==True: 
            val, val1=self.val[0], self.val[1]

            if ((val < -10) | (val > 10) | (val1<-10) | (val1 > 10)).any():
                val, val1 = 0, 0
                print('Input value not available')
                self.status.insert(END, 'Input value not available')
            with nidaqmx.Task() as task:
                task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
                task.ao_channels.add_ao_voltage_chan('Dev1/ao1')
                task.write([val,val1])

            print(f"Value set to: {val}")
            self.status.insert(END, f'Value set to: {val}')
            self.status.yview(END)

        else:
            if ((self.val<-10) | (self.val>10)).any():
                self.val=0
                print('Input value not available')
                self.status.insert(END, 'Input value not available')
                self.status.yview(END)
            with nidaqmx.Task() as task:
                task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
                task.ao_channels.add_ao_voltage_chan('Dev1/ao1')
                task.write([self.val,0])
            print(f"Value set to: 0")
            self.status.insert(END, f'Value set to: 0')
            self.status.yview(END)


        #reset the magnet
    def zerofield(self):
        with nidaqmx.Task() as task:
            task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
            task.ao_channels.add_ao_voltage_chan('Dev1/ao1')
            task.write([0,0])

        print(f'Resetting DAQs to zero')
        self.status.insert(END, f'Resetting DAQs to zero')
        self.status.yview(END)

    def blankscan(self):
        self.run=True
        self.blank=True
        self.values=np.arange(0,3,1)
        step = 5
        angles = np.arange(float(self.startangle.get())*np.pi/180, (float(self.stopangle.get())+step)*np.pi/180, step*np.pi/180)
        print(angles)
        self.status.insert(END, f'{np.arange(float(self.startangle.get()),float(self.stopangle.get())+step, step)}')
        self.status.yview(END)
        mag = float(self.mag.get())
        if mag==0:
            print("Set magnetic field")
            self.status.insert(END, 'Set magnetic field')
        par=[mag*np.cos(element)*FH1[0]+FH1[1] for n, element in enumerate(angles)]
        per=[mag*np.sin(element)*FH[0]+FH[1] for n, element in enumerate(angles)]
        values=np.row_stack((par,per))

        for i, item in enumerate(angles):
            self.val=values[:,i]
            print(item*180/np.pi)
            self.status.insert(END, str(item*180/np.pi))
            self.status.yview(END)
            self.writevolt()
            time.sleep(0.5)
        
        self.blank=False


    def batchscan(self):
        self.run=True
        self.blank=False
       
        if self.type=="ang":
            iterator=self.values[0,:]
        elif self.type=="Offset":
            iterator=self.values[0,:]

        else:
            iterator=self.values
            

        for i, item in enumerate(iterator):
            if self.run == False:
                self.zerofield
                break
            if len(self.values)==2:
                self.val=self.values[:,i]
            else:
                self.val=self.values[i]
            self.status.insert(END, f'Scan nr. {i+1} of {len(iterator)}')
            self.status.yview(END)
            self.writevolt()
            time.sleep(1)
            self.takecal()
            #if self.type=="ang":
            #    print("ang")

            currarray=np.empty(len(self.S11a))
            currarray[:]=np.nan
            if i ==0:
                for x, n in enumerate(self.current):
                    currarray[x]=n
                self.array=np.column_stack((self.S11a, self.Za, self.S11m, currarray))
            else:
                for x, n in enumerate(self.current):
                    currarray[x]=n
                self.array=np.column_stack((self.array, self.S11a, self.Za, self.S11m, currarray))

        print('done')
        self.status.insert(END, 'Done')
        self.status.yview(END)
        self.zerofield()
      
        #receiving measurements from the network analyzer
    
    def measure(self):
        self.current_measurement()
        inst.write_str_with_opc('INIT2:IMM')
        valu=inst.query_str("CALC2:DATA:TRAC? 'Trc2', SDAT")
        values=np.array([float(x) for x in valu.rsplit(',')])
        real=values[0:-1:2]
        imag=values[1::2]
        start=float(inst.query_str("SENS2:FREQ:STAR?"))
        stop=float(inst.query_str("SENS2:FREQ:STOP?"))
        point=int(inst.query_str("SENS2:SWEEP:POINTS?"))
        step=float(inst.query_str("SENS2:SWEEP:STEP?"))
        freq=np.linspace(start,stop,num=point)
        return real, imag, freq, self.current

    def current_measurement(self):
        if multimeter==0:
            self.current=np.empty(15,dtype=float)
        else:
            self.current=np.empty(15,dtype=float)
            t=0
            while t<15:
                string=instCurr.read()
                print(string)
                self.current[t]=float(eval(string.split(',')[0]))
                time.sleep(0.05)
                t+=1

    def docal(self):
        global Edf, Erf, Esf, Z0
        Edf = S11l
        Erf = 2 * (S11o - S11l) * (S11l - S11s)/(S11o - S11s)
        Esf = (S11o + S11s - 2 * S11l)/(S11o - S11s)
        Z0 = 50
        self.S11a = (self.S11m - Edf)/((self.S11m - Edf) * Esf + Erf)
        self.Za = Z0 * (1 + self.S11a)/(1 - self.S11a)

    def takecal(self):
        self.S11m = np.zeros(nfpoints, dtype=np.complex128)
        real_p, imag_p, self.freq, self.current = self.measure()
        plt.ion()
        self.S11m=real_p+1j*imag_p
        self.docal()
        self.ax.clear()
        self.ax1.clear()
        self.ax.set_xlabel('$f$ [Hz]')
        self.ax1.set_xlabel('$f$ [Hz]')
        self.ax.set_ylabel('$Z_a$ resistance [\u03A9]')
        self.ax1.set_ylabel('$Z_a$ reactance [\u03A9]')

        if self.type=='ang':
            plotlabel=str(np.around(self.angles[self.values[0,:]==self.val[0]]*180/np.pi))
            print(plotlabel)
        else:
            plotlabel=str(np.around((self.val-FH1[1])/FH1[0]))

        self.ax.plot(self.freq, self.Za.real, label=plotlabel)
        self.ax.legend()
        self.ax1.plot(self.freq, self.Za.imag, label=plotlabel)
        self.ax1.legend()
        self.canvas.draw_idle()
        self.canvas.flush_events()
        self.status.insert(END, 'Measurement complete')
        self.status.yview(END)

    def file_save(self):
        filename = tk.filedialog.asksaveasfilename(initialdir='/home/at/FMRmaelingar', defaultextension="*.txt")
        intro=f'''#FMR data from {datetime.datetime.now()}, this file includes calibration measurements, correction factor and corrected S11, Number of measurments: {nave+1}, number of points {nfpoints} 
freq\tS11o\tS11l\tS11s\tEdf\tErf\tEsf\tS11a\tZa\tS11m\tI'''

        #Notes: {self.notes.get('1.0','end')}
        fmt='%.5e'
        #np.savetxt('prufa.dat', np.arange(1,4) ,header=intro)
        dataout=np.column_stack((self.freq, S11o, S11l, S11s, Edf, Erf, Esf))
        
        if self.type=="ang":
            for i, n in enumerate(self.values[0,:]):
                looparray=np.column_stack((dataout, self.array[:,i*4:(i*4+4)]))
                label=self.mag.get()+'G_'+str(np.around(self.angles[i]*180/np.pi))+'deg.dat'
                np.savetxt(filename.rsplit('.')[0]+label, looparray, delimiter='\t', header=intro, fmt=fmt, comments='')
 
        elif self.type=="parallel":
            for i, n in enumerate(self.values):
                looparray=np.column_stack((dataout, self.array[:,i*4:(i*4+4)]))
                label=str(np.around((n-FH1[1])/FH1[0]))+'G.dat'
                np.savetxt(filename.rsplit('.')[0]+label, looparray, delimiter='\t', header=intro, fmt=fmt, comments='')
        elif self.type=="Offset":
            for i, n in enumerate(self.values[0,:]):
                looparray=np.column_stack((dataout, self.array[:,i*4:(i*4+4)]))
                label=str(np.around((n-FH1[1])/FH1[0]))+'G.dat'
                np.savetxt(filename.rsplit('.')[0]+label, looparray, delimiter='\t', header=intro, fmt=fmt, comments='')            



class IEC(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.buttonframe=tk.Frame(self)
        self.buttonframe.grid(row=0,column=11, columnspan=2,rowspan=2,sticky='wn')
        tk.Button(self.buttonframe, text="Measure", command=lambda: controller.show_frame(Measure), width=8, height=1, font=fontconf).grid(row=0,column=0,padx=5)
        tk.Button(self.buttonframe, text="Normal", command=lambda: controller.show_frame(Viewer2), width=8, height=1, font=fontconf).grid(row=0,column=1)
        tk.Button(self.buttonframe, text="Batch", command=lambda: controller.show_frame(Batch), width=8, height=1, font=fontconf).grid(row=1, column=0, sticky='n', padx=5)
        tk.Button(self.buttonframe, text="Calibrate", command=lambda: controller.show_frame(Calibrate), width=8, height=1, font=fontconf).grid(row=1,column=1, sticky='n')
        tk.Button(self, text="Exit", command=self._quit, font=fontconf).grid(row=0, column=17, sticky='ne')
        self.buttonframe.columnconfigure(0,weight=1)
        self.buttonframe.columnconfigure(1,weight=1)
        self.plotframe=tk.Frame(self)
        self.plotframe.grid(row=4, column=15, columnspan=10,rowspan=6)
        tk.Button(self.plotframe, text="Open", command=self.file_open, font=fontconf).grid(row=0, column=0)
        tk.Label(self, text="Selection",relief='ridge', font=fontconf).grid(row=4, column=14)
        self.Re=tk.IntVar() 
        self.Im=tk.IntVar()
        self.Re.set(0)
        self.Im.set(0)
        tk.Checkbutton(self.plotframe, text='Re', variable=self.Re, font=fontconf).grid(row=2,column=0)
        tk.Checkbutton(self.plotframe, text='Im', variable=self.Im, font=fontconf).grid(row=2,column=1,sticky='w')       
        self.plotframe.columnconfigure(0,weight=1)
        self.plotframe.columnconfigure(1,weight=1)

        self.listboxopen=tk.Listbox(self.plotframe, selectmode=tk.EXTENDED, height=6, width=22)
        self.listboxopen.grid(row=3, column=0, rowspan=4, columnspan=8)
        tk.Button(self.plotframe, text="Remove", command=self.listbox_delete,width=6, font=fontconf).grid(row=0, column=1,sticky='w')
        self.plotframe.bind_all('<Delete>', lambda e:self.listbox_delete())
        self.filelist=[]
        tk.Button(self.plotframe, text='up', command=lambda: self.reArrangeListbox("up"), font=fontconf).grid(row=0, column=3)
        tk.Button(self.plotframe, text='dn', command=lambda: self.reArrangeListbox("dn"), font=fontconf).grid(row=1, column=3)

        self.chipeakframe=tk.Frame(self)
        self.chipeakframe.grid(row=10,column=15,columnspan=3,rowspan=3)
        self.peak=tk.Button(self.chipeakframe, text="Peak", command=self.peak_finder, width=4, font=fontconf).grid(row=0, column=1,sticky='w')
        self.entryPwidth=tk.Entry(self.chipeakframe,width=5)
        self.entryPwidth.insert(0,"19e9")
        self.entryPwidth.grid(row=1,column=5)
        self.entryorder=tk.Entry(self.chipeakframe, width=5)
        self.entryorder.insert(0,"50")
        self.entryorder.grid(row=0, column=5)

        self.uncertvar=tk.IntVar()
        tk.Button(self.chipeakframe,text="Chi", command=self.chi, width=5, font=fontconf).grid(row=0, column=0,sticky='e')
        tk.Button(self.chipeakframe,text='Fit IEC',command=self.fitJalpha,width=5, font=fontconf).grid(row=1,column=0)
        #tk.Button(self.chipeakframe,text='Uncert.',command=self.iterate_extrema,font=fontconf).grid(row=1,column=1)
        tk.Button(self.chipeakframe,text='Save fit', command=self.save_fit,width=5,font=fontconf).grid(row=2,column=0)
        tk.Button(self.chipeakframe,text='EA fit',command=self.EA_fit,font=fontconf).grid(row=1,column=1)
        self.chipeakframe.bind_all('<o>', lambda e:self.chi())   

        self.circvar=tk.IntVar()
        self.circvar.set(1)
        self.squarevar=tk.IntVar()
        self.varLor, self.varDoubleLor,self.varSplitLor=tk.IntVar(self),tk.IntVar(self),tk.IntVar(self)
        
        self.sampleframe=tk.Frame(self)
        self.sampleframe.grid(row=13,column=15,rowspan=5, columnspan=3)
        self.circ=tk.Checkbutton(self.sampleframe, text="Circular", variable=self.circvar, font=fontconf)
        self.square=tk.Checkbutton(self.sampleframe, text="Square", variable=self.squarevar, font=fontconf)
        self.Lorentz=tk.Checkbutton(self.sampleframe, text="Lorentzian", variable=self.varLor, font=fontconf).grid(row=5,column=0)#,command=lambda: self.set_checkfit(1)
        self.Lorentzdouble=tk.Checkbutton(self.sampleframe, text="Double.Lor", variable=self.varDoubleLor, font=fontconf).grid(row=5,column=1)
        self.Lorentzsplit=tk.Checkbutton(self.sampleframe, text='Split.Lor',variable=self.varSplitLor,font=fontconf).grid(row=6,column=0,sticky='w')
        self.varTest=tk.IntVar(self)
        self.Test=tk.Checkbutton(self.sampleframe,text='FWHM-fit',variable=self.varTest,font=fontconf).grid(row=6,column=1,sticky='w')
        self.varLor.set(0)
        self.varDoubleLor.set(1)
        self.varSplitLor.set(0)
        tk.Label(self, text="Sample", relief='ridge', font=fontconf).grid(row=13, column=14)
        tk.Label(self.sampleframe, text="Width [mm]", font=fontconf).grid(row=0, column=0,sticky='e')
        tk.Label(self.sampleframe, text="Sampleh. width [mm]", font=fontconf).grid(row=2,column=0,sticky='e')
        self.circ.grid(row=4, column=0)
        self.square.grid(row=4, column=1)
        self.entrywidth = tk.Entry(self.sampleframe,width=3)
        self.entrywidth.insert(0, "4")
        self.entrywidth.grid(row=0, column=1)
        self.entrysampleh=tk.Entry(self.sampleframe,width=3)
        self.entrysampleh.insert(0,"4")
        self.entrysampleh.grid(row=2,column=1)
    
        self.fwhmframe=tk.Frame(self)
        self.fwhmframe.grid(row=17,column=15, rowspan=2,columnspan=2)
        for i in np.arange(0,3):
            self.fwhmframe.columnconfigure(i,weight=1)
        
        tk.Label(self, text='Axis limits',relief='ridge', font=fontconf).grid(row=18,column=14,sticky='nw')
        fwhmfr=self.fwhmframe
        self.axismin,self.axismax=tk.Entry(fwhmfr,width=6),tk.Entry(fwhmfr,width=6)
        i=0
        for F in (self.axismin,self.axismax):
            F.insert(0,'0')
            if i<2:
                F.grid(row=1,column=i+1)
            else:
                F.grid(row=2,column=i-1)
            i+=1
        self.fig = plt.figure(constrained_layout=True,figsize=[10,4.5])
        self.ax = plt.subplot()
        self.ax.set_xlabel('$f$ [Hz]')
        self.ax.set_ylabel('S11')
        
        self.canvas=FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().grid(row=0, column=0, rowspan=30, columnspan=10, sticky='nwse')
        self.toolbarframe=tk.Frame(self)
        self.toolbarframe.grid(row=31, column=0, columnspan=10, sticky='nswe')
        self.toolbar=NavigationToolbar2Tk(self.canvas, self.toolbarframe)
        self.toolbar.grid(row=0, column=0, columnspan=10, sticky='nswe')
        for i in np.arange(0,33):
            self.rowconfigure(i, weight=1)

        self.columnconfigure(0,weight=1)
        self.columnconfigure(1,weight=1)
        self.columnconfigure(2,weight=2)
        self.columnconfigure(3,weight=3)

        self.rowconfigure(20, weight=5)
        self.custframe=tk.Frame(self)
        self.custframe.grid(row=19, column=14, columnspan=4, rowspan=15, sticky='nsew')
        tk.Label(self.custframe,text='Min').grid(row=1,column=2)
        tk.Label(self.custframe,text='Max').grid(row=1,column=3)
        tk.Label(self.custframe,text="\u03B3\u2081").grid(row=2,column=0)
        self.entryGamma=tk.Entry(self.custframe,width=10)
        self.entryGamma.insert(0,'-19758412.149678')
        self.entryGamma.grid(row=2, column=1)
        # self.entryGaMin=tk.Entry(self.custframe,width=10)
        # self.entryGaMin.insert(0,'0')
        # self.entryGaMin.grid(row=2,column=2)
        # self.entryGaMax=tk.Entry(self.custframe,width=10)
        # self.entryGaMax.insert(0,'0')
        # self.entryGaMax.grid(row=2,column=3)
        tk.Label(self.custframe,text="\u03B3\u2082").grid(row=3,column=0)
        self.entryGamma1=tk.Entry(self.custframe,width=10)
        self.entryGamma1.insert(0,'-19758412.1496778')
        self.entryGamma1.grid(row=3, column=1)
        # self.entryGaMin1=tk.Entry(self.custframe,width=10)
        # self.entryGaMin1.insert(0,'0')
        # self.entryGaMin1.grid(row=3,column=2)
        # self.entryGaMax1=tk.Entry(self.custframe,width=10)
        # self.entryGaMax1.insert(0,'0')
        # self.entryGaMax1.grid(row=3,column=3)
        
        tk.Label(self.custframe,text="K\u0075\u2081 [erg/cm³]").grid(row=4,column=0)
        self.entryKu=tk.Entry(self.custframe,width=10)
        self.entryKu.insert(0,'12126')
        self.entryKu.grid(row=4,column=1)

        self.entryKuMin=tk.Entry(self.custframe,width=10)
        self.entryKuMin.insert(0,'12002')
        self.entryKuMin.grid(row=4,column=2)
        self.entryKuMax=tk.Entry(self.custframe,width=10)
        self.entryKuMax.insert(0,'12250')
        self.entryKuMax.grid(row=4,column=3)
        tk.Label(self.custframe,text="K\u0075\u2082 [erg/cm³]").grid(row=5,column=0)
        self.entryKu1=tk.Entry(self.custframe,width=10)
        self.entryKu1.insert(0,'8762')
        self.entryKu1.grid(row=5,column=1)

        self.entryKuMin1=tk.Entry(self.custframe,width=10)
        self.entryKuMin1.insert(0,'8650')
        self.entryKuMin1.grid(row=5,column=2)
        self.entryKuMax1=tk.Entry(self.custframe,width=10)
        self.entryKuMax1.insert(0,'8874')
        self.entryKuMax1.grid(row=5,column=3)

        tk.Label(self.custframe,text='M\u2081 [emu/cm³]').grid(row=6,column=0)
        self.entryMs=tk.Entry(self.custframe,width=10)
        self.entryMs.insert(0,'889.22')
        self.entryMs.grid(row=6,column=1)
        self.entryMsMin=tk.Entry(self.custframe,width=10)
        self.entryMsMin.insert(0,'886.32')
        self.entryMsMin.grid(row=6,column=2)
        self.entryMsMax=tk.Entry(self.custframe,width=10)
        self.entryMsMax.insert(0,'892.12')
        self.entryMsMax.grid(row=6,column=3)
        tk.Label(self.custframe,text='M\u2082 [emu/cm³]').grid(row=7,column=0)
        self.entryMs1=tk.Entry(self.custframe,width=10)
        self.entryMs1.insert(0,'631.8')
        self.entryMs1.grid(row=7,column=1)
        self.entryMsMin1=tk.Entry(self.custframe,width=10)
        self.entryMsMin1.insert(0,'630.8')
        self.entryMsMin1.grid(row=7,column=2)
        self.entryMsMax1=tk.Entry(self.custframe,width=10)
        self.entryMsMax1.insert(0,'632.8')
        self.entryMsMax1.grid(row=7,column=3)
        tk.Label(self.custframe,text='J [erg/cm\u00B2]').grid(row=8,column=0)
        self.entryJ=tk.Entry(self.custframe,width=10)
        self.entryJ.insert(0,'0')
        self.entryJ.grid(row=8,column=1)
        self.entryJMin=tk.Entry(self.custframe,width=10)
        self.entryJMin.insert(0,'0')
        self.entryJMin.grid(row=8,column=2)
        self.entryJMax=tk.Entry(self.custframe,width=10)
        self.entryJMax.insert(0,'0.07')
        self.entryJMax.grid(row=8,column=3)
        tk.Label(self.custframe,text='d\u2081 [nm]').grid(row=9,column=0,sticky='e')
        self.entryd1=tk.Entry(self.custframe,width=7)
        self.entryd1.insert(0,'19.39')
        self.entryd1.grid(row=9,column=1,sticky='w')
        tk.Label(self.custframe,text='d\u2082 [nm]').grid(row=9,column=2,sticky='e')
        self.entryd2=tk.Entry(self.custframe,width=7)
        self.entryd2.insert(0,'19.07')
        self.entryd2.grid(row=9,column=3,sticky='w') 
        tk.Label(self.custframe,text='\u0394d\u2081 [nm]').grid(row=10,column=0,sticky='e')
        self.entryd1delta=tk.Entry(self.custframe,width=7)
        self.entryd1delta.insert(0,'0.054')
        self.entryd1delta.grid(row=10,column=1,sticky='w')    
        tk.Label(self.custframe,text='\u0394d\u2082 [nm]').grid(row=10,column=2,sticky='e')
        self.entryd2delta=tk.Entry(self.custframe,width=7)
        self.entryd2delta.insert(0,'0.065')
        self.entryd2delta.grid(row=10,column=3,sticky='w')
        tk.Label(self.custframe,text="\u03b1\u2081").grid(row=11,column=0)
        self.entryAlpha1=tk.Entry(self.custframe,width=7)
        self.entryAlpha1.insert(0,'0.00')
        self.entryAlpha1.grid(row=11,column=1,sticky='w')
        self.entryAlpha1Min=tk.Entry(self.custframe,width=10)
        self.entryAlpha1Min.insert(0,'0.003')
        self.entryAlpha1Min.grid(row=11,column=2)
        self.entryAlpha1Max=tk.Entry(self.custframe,width=10)
        self.entryAlpha1Max.insert(0,'0.03')
        self.entryAlpha1Max.grid(row=11,column=3)
        tk.Label(self.custframe,text="\u03b1\u2082").grid(row=12,column=0)
        self.entryAlpha2=tk.Entry(self.custframe,width=7)
        self.entryAlpha2.insert(0,'0.0')
        self.entryAlpha2.grid(row=12,column=1,sticky='w')
        self.entryAlpha2Min=tk.Entry(self.custframe,width=10)
        self.entryAlpha2Min.insert(0,'0.003')
        self.entryAlpha2Min.grid(row=12,column=2)
        self.entryAlpha2Max=tk.Entry(self.custframe,width=10)
        self.entryAlpha2Max.insert(0,'0.03')
        self.entryAlpha2Max.grid(row=12,column=3)
        tk.Label(self.custframe,text='Geo.').grid(row=13,column=0)
        self.entryGeo=tk.Entry(self.custframe,width=10)
        self.entryGeo.insert(0,'0.8')
        self.entryGeo.grid(row=13,column=1)
        self.entryGeoMin=tk.Entry(self.custframe,width=10)
        self.entryGeoMin.insert(0,'0.8')
        self.entryGeoMin.grid(row=13,column=2)
        self.entryGeoMax=tk.Entry(self.custframe,width=10)
        self.entryGeoMax.insert(0,'1.0')
        self.entryGeoMax.grid(row=13,column=3)


        self.varLinearBkg,self.varLogisticBkg,self.varQuadBkg=tk.IntVar(self),tk.IntVar(self),tk.IntVar(self)
        self.varLinearBkg.set(0)
        self.varLogisticBkg.set(0)
        self.varQuadBkg.set(1)
        self.LinearBkg=tk.Checkbutton(self.custframe,text='Linear', variable=self.varLinearBkg).grid(row=16,column=2)
        self.LogisticBkg=tk.Checkbutton(self.custframe,text='Logistic',variable=self.varLogisticBkg).grid(row=16,column=3)
        self.LinearBkg=tk.Checkbutton(self.custframe,text='Linear', variable=self.varLinearBkg).grid(row=16,column=2)
        self.QuadBkg=tk.Checkbutton(self.custframe,text='Quadratic',variable=self.varQuadBkg).grid(row=16,column=1)
        self.varLeastsq, self.varShgo=tk.IntVar(self), tk.IntVar(self)
        self.Leastsq=tk.Checkbutton(self.custframe, text="Leastsq", variable=self.varLeastsq,command=lambda: self.set_checkfit(2)).grid(row=14, column=1)
        self.Shgo=tk.Checkbutton(self.custframe, text="Shgo", variable=self.varShgo,command=lambda: self.set_checkfit(3)).grid(row=14,column=2)
        self.varLeastsq.set(1)
        self.varBackgr=tk.IntVar(self)
        self.Backgr=tk.Checkbutton(self.custframe, text="Backgr", variable=self.varBackgr).grid(row=14,column=3)
        self.varBackgr.set(1)
        self.acceptindicator=False
        self.status=tk.Listbox(self, width=20, height=9, bg='#E0E0E0', bd=2)
        self.status.grid(row=22, column=10, rowspan=5, columnspan=4)
        for i in np.arange(0,12):
            self.custframe.rowconfigure(i, weight=1)
                
        self.indexmax=4
        self.indexmin=0
        self.peakpos=[0,0]
        self.iterator=0

    def _quit(self):
        app.quit()
        app.destroy()

    def file_open(self):
        t=tk.filedialog.askopenfilenames(initialdir='/home/fmrdata/Data',filetypes=(('dat files', '*.dat'),('txt files','*.txt'),('all files','*.*')))
        self.filelist.extend(list(t))
        self.listboxopen.delete(0,self.listboxopen.size())

        for i in range(len(self.filelist)):
            self.listboxopen.insert(i, self.filelist[i].split('/')[-1])

        #remove .dat files from the list to plot

    def listbox_delete(self):
        END = self.listboxopen.size()
        self.removelist = self.listboxopen.curselection()
        self.filelist = [item for n, item in enumerate(self.filelist) if n not in self.removelist]
        self.listboxopen.delete(0,END)
        for i in range(len(self.filelist)):
            self.listboxopen.insert(i, self.filelist[i].split('/')[-1])

        #plot the all the .dat files but only the selected item in the self.listbox, which corresponds the the S11 measurement
            
    def EA_fit(self):
        self.ax.clear()
        self.ax.set_xlabel('H [Oe]')
        self.ax.set_ylabel('$\u03C9 [rad/s]$')
        field=np.loadtxt(self.filelist[0],usecols=[0], dtype='str', skiprows=1, delimiter='\t')
        resonance1=np.loadtxt(self.filelist[0], usecols=[2], skiprows=1, delimiter='\t')
        stdres1=np.loadtxt(self.filelist[0],usecols=[3],skiprows=1, delimiter='\t')
        try:        
            resonance2=np.loadtxt(self.filelist[0], usecols=[6], skiprows=1, delimiter='\t')
            stdres2=np.loadtxt(self.filelist[0], usecols=[7],skiprows=1, delimiter='\t')
            fit_indicator=0
        except:
            print('Only one array')
            fit_indicator=1
        
        H=np.array([float(i.split('_')[-1].split('G')[0]) for i in field])
        d1=float(self.entryd1.get())*1e-7
        d2=float(self.entryd2.get())*1e-7
        M1=float(self.entryMs.get())
        M2=float(self.entryMs1.get())
        J=float(self.entryJ.get())
        Ku1=float(self.entryKu.get())
        Ku2=float(self.entryKu1.get())
        ga1=float(self.entryGamma.get())
        ga2=float(self.entryGamma1.get())

        if fit_indicator==0:
            def fcn2min(params, H, y, y1):
                J=params['J']
                B1=J/(d1*M1*M2)
                B2=J/(d2*M1*M2)
                Dx1=H+2*Ku1/M1+M2*B1+4*np.pi*M1
                Dy1=-H-2*Ku1/M1-M2*B1
                Dx2=H+2*Ku2/M2+M1*B2+4*np.pi*M2
                Dy2=-H-2*Ku2/M2-M1*B2
                omega1=1/np.sqrt(2)*(np.sqrt(2*M1*M2*B1*B2*ga1*ga2-ga1**2*Dx1*Dy1-ga2**2*Dx2*Dy2-np.sqrt(-4*M1*M2*B1*B2*ga1*ga2*(-ga2*Dx2+ga1*Dy1)*(ga1*Dx1-ga2*Dy2)+(ga1**2*Dx1*Dy1-ga2**2*Dx2*Dy2)**2)))
                omega2=1/np.sqrt(2)*(np.sqrt(2*M1*M2*B1*B2*ga1*ga2-ga1**2*Dx1*Dy1-ga2**2*Dx2*Dy2+np.sqrt(-4*M1*M2*B1*B2*ga1*ga2*(-ga2*Dx2+ga1*Dy1)*(ga1*Dx1-ga2*Dy2)+(ga1**2*Dx1*Dy1-ga2**2*Dx2*Dy2)**2)))
                res1=(y-omega1)**2
                res2=(y1-omega2)**2
                res2[np.where(y1==0)]=0
            
                resids = res1+res2
                return resids

            params = Parameters()
            params.add('J',value=float(self.entryJ.get()),min=float(self.entryJMin.get()),max=float(self.entryJMax.get()))

            minner=Minimizer(fcn2min, params, fcn_args = (H, resonance1, resonance2))
        elif fit_indicator==1:
            def fcn2min(params, H, y):
                J=params['J']
                #M2=params['M2']
                B1=J/(d1*M1*M2)
                B2=J/(d2*M1*M2)
                Dx1=H+2*Ku1/M1+M2*B1+4*np.pi*M1
                Dy1=-H-2*Ku1/M1-M2*B1
                Dx2=H+2*Ku2/M2+M1*B2+4*np.pi*M2
                Dy2=-H-2*Ku2/M2-M1*B2
                omega1=1/np.sqrt(2)*(np.sqrt(2*M1*M2*B1*B2*ga1*ga2-ga1**2*Dx1*Dy1-ga2**2*Dx2*Dy2-np.sqrt(-4*M1*M2*B1*B2*ga1*ga2*(-ga2*Dx2+ga1*Dy1)*(ga1*Dx1-ga2*Dy2)+(ga1**2*Dx1*Dy1-ga2**2*Dx2*Dy2)**2)))
                res1=(y-omega1)**2    
                res1[np.where(H>95)]=res1[np.where(H>95)]*9

                return res1

            params = Parameters()
            params.add('J',value=float(self.entryJ.get()),min=float(self.entryJMin.get()),max=float(self.entryJMax.get()))
            #params.add('M2',value=float(self.entryMs1.get()),min=float(self.entryMsMin1.get()),max=float(self.entryMsMax1.get()))
            minner=Minimizer(fcn2min, params, fcn_args = (H, resonance1))

        
        result = minner.minimize()
        #if fit_indicator==1:
        #    ci=conf_interval(minner,result)
        #    printfuncs.report_ci(ci)

        report_fit(result)
        J=result.params['J'].value
        B1=J/(d1*M1*M2)
        B2=J/(d2*M1*M2)
        Dx1=H+2*Ku1/M1+M2*B1+4*np.pi*M1
        Dy1=-H-2*Ku1/M1-M2*B1
        Dx2=H+2*Ku2/M2+M1*B2+4*np.pi*M2
        Dy2=-H-2*Ku2/M2-M1*B2
        omega1=1/np.sqrt(2)*(np.sqrt(2*M1*M2*B1*B2*ga1*ga2-ga1**2*Dx1*Dy1-ga2**2*Dx2*Dy2-np.sqrt(-4*M1*M2*B1*B2*ga1*ga2*(-ga2*Dx2+ga1*Dy1)*(ga1*Dx1-ga2*Dy2)+(ga1**2*Dx1*Dy1-ga2**2*Dx2*Dy2)**2)))
        omega2=1/np.sqrt(2)*(np.sqrt(2*M1*M2*B1*B2*ga1*ga2-ga1**2*Dx1*Dy1-ga2**2*Dx2*Dy2+np.sqrt(-4*M1*M2*B1*B2*ga1*ga2*(-ga2*Dx2+ga1*Dy1)*(ga1*Dx1-ga2*Dy2)+(ga1**2*Dx1*Dy1-ga2**2*Dx2*Dy2)**2)))
        self.ax.errorbar(H,resonance1,yerr=stdres1,fmt='*')
        self.ax.plot(H,omega1,'--')
        if fit_indicator==0:
            self.ax.errorbar(H,resonance2,yerr=stdres2,fmt='o')
            self.ax.plot(H,omega2,'--')
        self.status.insert(END, '-------------------------')
        self.status.insert(END, f'J {np.round(J,4)}')
        self.status.insert(END, f'Delta J {np.round(result.params["J"].stderr,5)}')
        self.status.insert(END, f'Uncert. ratio {result.params["J"].stderr/J}')
        self.status.yview(END)
        self.entryJ.delete(0,"end")
        self.entryJ.insert(0,J)
        self.canvas.draw()

    def reArrangeListbox(self, direction):
        items=list(self.listboxopen.curselection())
        if not items:
            print("Nothing")
            return
        if direction == "up":
            for pos in items:
                if pos == 0:
                    continue
                text=self.listboxopen.get(pos)
                fileName = self.filelist[pos]
                self.filelist.pop(pos)
                self.listboxopen.delete(pos)
                self.filelist.insert(pos-1, fileName)
                self.listboxopen.insert(pos-1, text)
            self.listboxopen.selection_clear(0,self.listboxopen.size())
            self.listboxopen.selection_set(tuple([i-1 for i in items]))

        if direction == "dn":
            for pos in items:
                if pos ==self.listboxopen.size():
                    continue
                text=self.listboxopen.get(pos)
                fileName = self.filelist[pos]
                self.listboxopen.delete(pos)
                self.filelist.pop(pos)
                self.filelist.insert(pos+1, fileName)
                self.listboxopen.insert(pos+1, text)
            self.listboxopen.selection_clear(0,self.listboxopen.size())
            self.listboxopen.selection_set(tuple([i+1 for i in items]))
        else:
            return
        
    def iterate_extrema(self):
        J_array=np.empty(0)
        for i in np.arange(12):
            J_array=np.append(J_array,self.fitJ(i))
            print(f'''Step {i}''')
        print(J_array)
        delta_J_variable=np.empty(0)
        for i, n in enumerate(J_array):
            if np.mod(i,2)==0 and i!=11:
                delta_J_variable=np.append(delta_J_variable,abs(J_array[i+1]-J_array[i])/2)
        accumulate=np.sqrt(np.sum(delta_J_variable**2))
        print(np.log10(accumulate),accumulate)
        meanJ=np.round(np.mean(J_array),int(abs(np.floor(np.log10(accumulate)))))
        uncertratio=accumulate/meanJ
        self.status.insert(END, '-------------------------')
        self.status.insert(END, f'J array {np.round(J_array,4)}')
        self.status.insert(END, f'J mean {meanJ}')
        self.status.insert(END, f'Delta J {delta_J_variable}')
        self.status.insert(END, f'Total uncert. {np.round(accumulate,5)}')
        self.status.insert(END, f'Uncert. ratio {np.round(uncertratio,4)}')
        self.status.yview(END)

    
    def fitJalpha(self):
        H=float(self.filelist[0].split('_')[-1].split('.')[0])
        d1=float(self.entryd1.get())*1e-7
        d2=float(self.entryd2.get())*1e-7
        d1_delta=float(self.entryd1delta.get())*1e-7
        d2_delta=float(self.entryd2delta.get())*1e-7
        m1=float(self.entryMs.get())
        M1Max=float(self.entryMsMax.get())
        M1Min=float(self.entryMsMin.get())
        m2=float(self.entryMs1.get())
        M2Max=float(self.entryMsMax1.get())
        M2Min=float(self.entryMsMin1.get())
        J=float(self.entryJ.get())
        k1=float(self.entryKu.get())
        Ku1Max=float(self.entryKuMax.get())
        Ku1Min=float(self.entryKuMin.get())
        k2=float(self.entryKu1.get())
        Ku2Max=float(self.entryKuMax1.get())
        Ku2Min=float(self.entryKuMin1.get())
        ga1=float(self.entryGamma.get())
        ga2=float(self.entryGamma1.get())
        a1=float(self.entryAlpha1.get())
        a2=float(self.entryAlpha2.get())
        geo=float(self.entryGeo.get())
        J=float(self.entryJ.get())
        def func2solve(params,O,chi):
            if float(self.entryJMin.get())!=float(self.entryJMax.get()):
                J=params['J']
            else:
                J=float(self.entryJ.get())
            if M1Min!=M1Max:
                m1=params['m1']
            else:
                m1=float(self.entryMs.get())
            if M2Min!=M2Max:
                m2=params['m2']
            else:
                m2=float(self.entryMs1.get())
            a1=params['a1']
            a2=params['a2']
            geo=float(self.entryGeo.get())

            if geoindex==1:
                geo1=params['geo']
                chi=chi*geo/geo1

            b1=J/(d1*m1*m2)
            b2=J/(d2*m1*m2)            
            Chi=(1/(d1+d2))*(d2*((1j*O*m2*b2*ga2*(((1j*O+(1j*O*m1*m2*b1*b2*ga1*ga2)/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2)))*((m1*m2*b1*ga1*ga2*(-1j*O*a2-(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2))/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2))-m1*ga1))/((1j*O+(1j*O*m1*m2*b1*b2*ga1*ga2)/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2)))**2-(1j*O*a1+(H+4*np.pi*m1+m2*b1+(2*k1)/m1)*ga1-(m1*m2*b1*b2*ga1*ga2*(1j*O*a2-(-H-m1*b2-(2*k2)/m2)*ga2))/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2)))*(-1j*O*a1+(-H-m2*b1-(2*k1)/m1)*ga1-(m1*m2*b1*b2*ga1*ga2*(-1j*O*a2-(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2))/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2))))-(1j*O*m1*m2*b1*ga1*ga2*(1j*O*a1-(-H-m2*b1-(2*k1)/m1)*ga1+(m1*m2*b1*b2*ga1*ga2*(-1j*O*a2-(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2))/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2))))/((-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2))*((1j*O+(1j*O*m1*m2*b1*b2*ga1*ga2)/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2)))**2-(1j*O*a1+(H+4*np.pi*m1+m2*b1+(2*k1)/m1)*ga1-(m1*m2*b1*b2*ga1*ga2*(1j*O*a2-(-H-m1*b2-(2*k2)/m2)*ga2))/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2)))*(-1j*O*a1+(-H-m2*b1-(2*k1)/m1)*ga1-(m1*m2*b1*b2*ga1*ga2*(-1j*O*a2-(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2))/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2)))))))/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2))-(m2*ga2*(-1j*O*a2-(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2))/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2))-(m2*b2*ga2*(-1j*O*a2-(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2)*(((-1j*O*a1-(H+4*np.pi*m1+m2*b1+(2*k1)/m1)*ga1+(m1*m2*b1*b2*ga1*ga2*(1j*O*a2-(-H-m1*b2-(2*k2)/m2)*ga2))/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2)))*((m1*m2*b1*ga1*ga2*(-1j*O*a2-(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2))/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2))-m1*ga1))/((1j*O+(1j*O*m1*m2*b1*b2*ga1*ga2)/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2)))**2-(1j*O*a1+(H+4*np.pi*m1+m2*b1+(2*k1)/m1)*ga1-(m1*m2*b1*b2*ga1*ga2*(1j*O*a2-(-H-m1*b2-(2*k2)/m2)*ga2))/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2)))*(-1j*O*a1+(-H-m2*b1-(2*k1)/m1)*ga1-(m1*m2*b1*b2*ga1*ga2*(-1j*O*a2-(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2))/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2))))-(1j*O*m1*m2*b1*ga1*ga2*(1j*O+(1j*O*m1*m2*b1*b2*ga1*ga2)/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2))))/((-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2))*((1j*O+(1j*O*m1*m2*b1*b2*ga1*ga2)/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2)))**2-(1j*O*a1+(H+4*np.pi*m1+m2*b1+(2*k1)/m1)*ga1-(m1*m2*b1*b2*ga1*ga2*(1j*O*a2-(-H-m1*b2-(2*k2)/m2)*ga2))/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2)))*(-1j*O*a1+(-H-m2*b1-(2*k1)/m1)*ga1-(m1*m2*b1*b2*ga1*ga2*(-1j*O*a2-(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2))/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2)))))))/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2)))+d1*(((-1j*O*a1-(H+4*np.pi*m1+m2*b1+(2*k1)/m1)*ga1+(m1*m2*b1*b2*ga1*ga2*(1j*O*a2-(-H-m1*b2-(2*k2)/m2)*ga2))/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2)))*((m1*m2*b1*ga1*ga2*(-1j*O*a2-(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2))/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2))-m1*ga1))/((1j*O+(1j*O*m1*m2*b1*b2*ga1*ga2)/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2)))**2-(1j*O*a1+(H+4*np.pi*m1+m2*b1+(2*k1)/m1)*ga1-(m1*m2*b1*b2*ga1*ga2*(1j*O*a2-(-H-m1*b2-(2*k2)/m2)*ga2))/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2)))*(-1j*O*a1+(-H-m2*b1-(2*k1)/m1)*ga1-(m1*m2*b1*b2*ga1*ga2*(-1j*O*a2-(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2))/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2))))-(1j*O*m1*m2*b1*ga1*ga2*(1j*O+(1j*O*m1*m2*b1*b2*ga1*ga2)/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2))))/((-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2))*((1j*O+(1j*O*m1*m2*b1*b2*ga1*ga2)/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2)))**2-(1j*O*a1+(H+4*np.pi*m1+m2*b1+(2*k1)/m1)*ga1-(m1*m2*b1*b2*ga1*ga2*(1j*O*a2-(-H-m1*b2-(2*k2)/m2)*ga2))/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2)))*(-1j*O*a1+(-H-m2*b1-(2*k1)/m1)*ga1-(m1*m2*b1*b2*ga1*ga2*(-1j*O*a2-(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2))/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2)))))))
            return (Chi.imag-chi)**2
        params=Parameters()
        
        if float(self.entryJMin.get())!=float(self.entryJMax.get()):
            params.add('J',value=J,min=float(self.entryJMin.get()),max=float(self.entryJMax.get()))
        if M1Min!=M1Max:
            params.add('m1',value=m1,min=M1Min,max=M1Max)
        if M2Min!=M2Max:
            params.add('m2',value=m2,min=M2Min,max=M2Max)
        params.add('a1',value=a1,min=float(self.entryAlpha1Min.get()),max=float(self.entryAlpha1Max.get()))
        params.add('a2',value=a2,min=float(self.entryAlpha2Min.get()),max=float(self.entryAlpha2Max.get()))
        
        geomin,geomax=float(self.entryGeoMin.get()),float(self.entryGeoMax.get())
        if geomin!=geomax:
            params.add('geo',value=float(self.entryGeo.get()),min=float(self.entryGeoMin.get()),max=float(self.entryGeoMax.get()))
            geoindex=1
        else:
            geoindex=0

        if self.varQuadBkg.get()==1:
            minner = Minimizer(func2solve, params,fcn_args=(self.freqfit,self.imagfit-self.comp['quad_']))#self.comp['l_upper_']+self.comp['l_lower_']))
        else:
            minner = Minimizer(func2solve, params,fcn_args=(self.freqfit,self.imagfit-self.comp['line_']))#self.comp['l_upper_']+self.comp['l_lower_']))
        
        result = minner.minimize()
        report_fit(result)
        if float(self.entryJMin.get())!=float(self.entryJMax.get()):
            J=result.params['J'].value
            self.Jresult=result.params['J']
        b1=J/(d1*m1*m2)
        b2=J/(d2*m1*m2)
        a1=result.params['a1'].value
        a2=result.params['a2'].value
        if M1Min!=M1Max:
            m1=result.params['m1'].value
        if M2Min!=M2Max:
            m2=result.params['m2'].value
        O=self.freqfit
        Chi=(1/(d1+d2))*(d2*((1j*O*m2*b2*ga2*(((1j*O+(1j*O*m1*m2*b1*b2*ga1*ga2)/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2)))*((m1*m2*b1*ga1*ga2*(-1j*O*a2-(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2))/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2))-m1*ga1))/((1j*O+(1j*O*m1*m2*b1*b2*ga1*ga2)/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2)))**2-(1j*O*a1+(H+4*np.pi*m1+m2*b1+(2*k1)/m1)*ga1-(m1*m2*b1*b2*ga1*ga2*(1j*O*a2-(-H-m1*b2-(2*k2)/m2)*ga2))/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2)))*(-1j*O*a1+(-H-m2*b1-(2*k1)/m1)*ga1-(m1*m2*b1*b2*ga1*ga2*(-1j*O*a2-(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2))/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2))))-(1j*O*m1*m2*b1*ga1*ga2*(1j*O*a1-(-H-m2*b1-(2*k1)/m1)*ga1+(m1*m2*b1*b2*ga1*ga2*(-1j*O*a2-(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2))/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2))))/((-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2))*((1j*O+(1j*O*m1*m2*b1*b2*ga1*ga2)/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2)))**2-(1j*O*a1+(H+4*np.pi*m1+m2*b1+(2*k1)/m1)*ga1-(m1*m2*b1*b2*ga1*ga2*(1j*O*a2-(-H-m1*b2-(2*k2)/m2)*ga2))/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2)))*(-1j*O*a1+(-H-m2*b1-(2*k1)/m1)*ga1-(m1*m2*b1*b2*ga1*ga2*(-1j*O*a2-(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2))/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2)))))))/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2))-(m2*ga2*(-1j*O*a2-(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2))/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2))-(m2*b2*ga2*(-1j*O*a2-(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2)*(((-1j*O*a1-(H+4*np.pi*m1+m2*b1+(2*k1)/m1)*ga1+(m1*m2*b1*b2*ga1*ga2*(1j*O*a2-(-H-m1*b2-(2*k2)/m2)*ga2))/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2)))*((m1*m2*b1*ga1*ga2*(-1j*O*a2-(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2))/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2))-m1*ga1))/((1j*O+(1j*O*m1*m2*b1*b2*ga1*ga2)/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2)))**2-(1j*O*a1+(H+4*np.pi*m1+m2*b1+(2*k1)/m1)*ga1-(m1*m2*b1*b2*ga1*ga2*(1j*O*a2-(-H-m1*b2-(2*k2)/m2)*ga2))/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2)))*(-1j*O*a1+(-H-m2*b1-(2*k1)/m1)*ga1-(m1*m2*b1*b2*ga1*ga2*(-1j*O*a2-(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2))/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2))))-(1j*O*m1*m2*b1*ga1*ga2*(1j*O+(1j*O*m1*m2*b1*b2*ga1*ga2)/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2))))/((-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2))*((1j*O+(1j*O*m1*m2*b1*b2*ga1*ga2)/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2)))**2-(1j*O*a1+(H+4*np.pi*m1+m2*b1+(2*k1)/m1)*ga1-(m1*m2*b1*b2*ga1*ga2*(1j*O*a2-(-H-m1*b2-(2*k2)/m2)*ga2))/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2)))*(-1j*O*a1+(-H-m2*b1-(2*k1)/m1)*ga1-(m1*m2*b1*b2*ga1*ga2*(-1j*O*a2-(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2))/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2)))))))/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2)))+d1*(((-1j*O*a1-(H+4*np.pi*m1+m2*b1+(2*k1)/m1)*ga1+(m1*m2*b1*b2*ga1*ga2*(1j*O*a2-(-H-m1*b2-(2*k2)/m2)*ga2))/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2)))*((m1*m2*b1*ga1*ga2*(-1j*O*a2-(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2))/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2))-m1*ga1))/((1j*O+(1j*O*m1*m2*b1*b2*ga1*ga2)/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2)))**2-(1j*O*a1+(H+4*np.pi*m1+m2*b1+(2*k1)/m1)*ga1-(m1*m2*b1*b2*ga1*ga2*(1j*O*a2-(-H-m1*b2-(2*k2)/m2)*ga2))/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2)))*(-1j*O*a1+(-H-m2*b1-(2*k1)/m1)*ga1-(m1*m2*b1*b2*ga1*ga2*(-1j*O*a2-(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2))/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2))))-(1j*O*m1*m2*b1*ga1*ga2*(1j*O+(1j*O*m1*m2*b1*b2*ga1*ga2)/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2))))/((-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2))*((1j*O+(1j*O*m1*m2*b1*b2*ga1*ga2)/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2)))**2-(1j*O*a1+(H+4*np.pi*m1+m2*b1+(2*k1)/m1)*ga1-(m1*m2*b1*b2*ga1*ga2*(1j*O*a2-(-H-m1*b2-(2*k2)/m2)*ga2))/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2)))*(-1j*O*a1+(-H-m2*b1-(2*k1)/m1)*ga1-(m1*m2*b1*b2*ga1*ga2*(-1j*O*a2-(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2))/(-O**2-((-H-m1*b2-(2*k2)/m2)*ga2-1j*O*a2)*(1j*O*a2+(H+4*np.pi*m2+m1*b2+(2*k2)/m2)*ga2)))))))
        self.ax.clear()

        self.ax.set_xlabel('\u03C9 [rad/s]')
        self.ax.set_ylabel('\u1d61')
        #self.ax.plot(self.freqfit,self.comp['line_']+self.comp['l_upper_']+self.comp['l_lower_'],label='Lorentzian')
        self.ax.plot(self.freqfit,Chi.real,label='Re fit')
        if self.varQuadBkg.get()==1:
            self.ax.plot(self.freqfit,self.comp['quad_']+Chi.imag,label='Im fit')
            self.ChiIecAlpha=self.comp['quad_']+Chi.imag
            dataout=np.column_stack((self.freqfit,Chi.real,self.comp['quad_']+Chi.imag))
        else:
            self.ax.plot(self.freqfit,self.comp['line_']+Chi.imag,label='Im fit')
            self.ChiIecAlpha=self.comp['line_']+Chi.imag
            dataout=np.column_stack((self.freqfit,Chi.real,self.comp['line_']+Chi.imag))

        self.ax.plot(self.freq,self.chii.real,label='Re meas')
        self.ax.plot(self.freq,self.chii.imag,label='Im meas')
        dataout1=np.column_stack((self.freq,self.chii.real,self.chii.imag))
        np.savetxt('chi_IEC_mes2.dat',dataout1,delimiter='\t',fmt='%.5e',comments='')
        np.savetxt('chi_IEC_fit2.dat',dataout,delimiter='\t',fmt='%.5e',comments='')
        print('saved')
        self.ax.legend()
        self.entryJ.delete(0,"end")
        self.entryJ.insert(0,J)
        self.entryAlpha1.delete(0,"end")
        self.entryAlpha1.insert(0,a1)
        self.entryAlpha2.delete(0,"end")
        self.entryAlpha2.insert(0,a2)
        if geomin!=geomax:
            self.entryGeo.delete(0,"end")
            self.entryGeo.insert(0,result.params['geo'].value)
        if M1Min!=M1Max:
            self.entryMs.delete(0,"end")
            self.entryMs.insert(0,result.params['m1'].value)
        if M2Min!=M2Max:
            self.entryMs1.delete(0,"end")
            self.entryMs1.insert(0,result.params['m2'].value)

        self.canvas.draw()

    def save_fit(self):
        filename = tk.filedialog.asksaveasfilename(initialdir='/home/fmrdata/Data', defaultextension="*.txt")
        skjal=open(filename,'w')
        skjal.write(f'Variable\tValue\tmin\tmax\tUncert.\t{datetime.datetime.now()}\n')
        skjal.write(f'Gamma1\t{self.entryGamma.get()}\t{0}\t{0}\n')    
        skjal.write(f'Gamma2\t{self.entryGamma1.get()}\t{0}\t{0}\n')
        skjal.write(f'Alpha1\t{self.entryAlpha1.get()}\t{self.entryAlpha1Min.get()}\t{self.entryAlpha1Max.get()}\n')
        skjal.write(f'Alpha2\t{self.entryAlpha2.get()}\t{self.entryAlpha2Min.get()}\t{self.entryAlpha2Max.get()}\n')
        skjal.write(f'Ku1\t{self.entryKu.get()}\t{self.entryKuMin.get()}\t{self.entryKuMax.get()}\n')
        skjal.write(f'Ku2\t{self.entryKu1.get()}\t{self.entryKuMin1.get()}\t{self.entryKuMax1.get()}\n')
        skjal.write(f'Ms1\t{self.entryMs.get()}\t{self.entryMsMin.get()}\t{self.entryMsMax.get()}\n')
        skjal.write(f'Ms2\t{self.entryMs1.get()}\t{self.entryMsMin1.get()}\t{self.entryMsMax1.get()}\n')
        skjal.write(f'J\t{self.entryJ.get()}\t{self.entryJMin.get()}\t{self.entryJMax.get()}\t{self.Jresult.stderr}\n')
        skjal.write(f'd1\t{self.entryd1.get()}\t{self.entryd1delta.get()}\n')
        skjal.write(f'd2\t{self.entryd2.get()}\t{self.entryd2delta.get()}\n')
        skjal.close()


    def fitJ(self,fit_indicator):
        #Importing the magnetic parameters and the applied field
        H=float(self.filelist[0].split('_')[-1].split('.')[0])

        d1=float(self.entryd1.get())*1e-7
        d2=float(self.entryd2.get())*1e-7
        d1_delta=float(self.entryd1delta.get())*1e-7
        d2_delta=float(self.entryd2delta.get())*1e-7
        M1=float(self.entryMs.get())
        M1Max=float(self.entryMsMax.get())
        M1Min=float(self.entryMsMin.get())
        M2=float(self.entryMs1.get())
        M2Max=float(self.entryMsMax1.get())
        M2Min=float(self.entryMsMin1.get())
        J=float(self.entryJ.get())
        Ku1=float(self.entryKu.get())
        Ku1Max=float(self.entryKuMax.get())
        Ku1Min=float(self.entryKuMin.get())
        Ku2=float(self.entryKu1.get())
        Ku2Max=float(self.entryKuMax1.get())
        Ku2Min=float(self.entryKuMin1.get())
        ga1=float(self.entryGamma.get())
        ga2=float(self.entryGamma1.get())

        if fit_indicator==0:
            #Anisotropy
            Ku1=Ku1Max
        elif fit_indicator==1:
            Ku1=Ku1Min
        elif fit_indicator==2:
            Ku2=Ku2Max
        elif fit_indicator==3:
            Ku2=Ku2Min
        elif fit_indicator==4:
            M1=M1Max
        elif fit_indicator==5:
            M1=M1Min
        elif fit_indicator==6:
            M2=M2Max
        elif fit_indicator==7:
            M2=M2Min
        elif fit_indicator==8:
            d1=d1+d1_delta
        elif fit_indicator==9:
            d1=d1-d1_delta
        elif fit_indicator==10:
            d2=d2+d2_delta
        elif fit_indicator==11:
            d2=d2-d2_delta 
        # def funcfsolve(params,x1,x2):
        #     J=params['J']
        #     #Function for the in the numerator, finding roots will give the resonance condition
        #     def func(w):
        #         B1=J/(d1*M1*M2)
        #         B2=J/(d2*M1*M2)
        #         Dx1=H+2*Ku1/M1+M2*B1+4*np.pi*M1
        #         Dy1=-H-2*Ku1/M1-M2*B1
        #         Dx2=H+2*Ku2/M2+M1*B2+4*np.pi*M2
        #         Dy2=-H-2*Ku2/M2-M1*B2
        #         return (d1+d2)*(J**2*B2*ga1**2*ga2**2*(w**2-ga2**2*Dx2*Dy2)+d1**2*(w**2+ga1**2*Dx1*Dy1)*(w**2+ga2**2*Dx2*Dy2)**2-J*d1*B2*ga1*ga2*(w**2+ga2**2*Dx2*Dy2)*(2*w**2+ga1*ga2*(Dx1*Dx2-Dy1*Dy2))) 

        #     #Finding a root near to the initial guess of x1
        #     w_solution = fsolve(func,x1)
        #     if x2==0:
        #         res2=0
        #     else: #When looking for two peaks we give the initial guess of x2
        #         w_solution1 = fsolve(func,x2)
        #         res2=x2-w_solution1
        #     res1=x1-w_solution
        #     return res1**2+res2**2
        
        # params = Parameters()
        # params.add('J',value=float(self.entryJ.get()),min=float(self.entryJMin.get()),max=float(self.entryJMax.get()))


        def funcfsolve(params,H,y):
            J=params['J']
            M2=params['M2']
            B1=J/(d1*M1*M2)
            B2=J/(d2*M1*M2)
            Dx1=H+2*Ku1/M1+M2*B1+4*np.pi*M1
            Dy1=-H-2*Ku1/M1-M2*B1
            Dx2=H+2*Ku2/M2+M1*B2+4*np.pi*M2
            Dy2=-H-2*Ku2/M2-M1*B2
            omega1=1/np.sqrt(2)*(np.sqrt(2*M1*M2*B1*B2*ga1*ga2-ga1**2*Dx1*Dy1-ga2**2*Dx2*Dy2-np.sqrt(-4*M1*M2*B1*B2*ga1*ga2*(-ga2*Dx2+ga1*Dy1)*(ga1*Dx1-ga2*Dy2)+(ga1**2*Dx1*Dy1-ga2**2*Dx2*Dy2)**2)))
            res1=(y-omega1)**2          
            return res1


    
        #running Levenberg marquardt non-linear least squares minimization for two initial guesses or one
        if self.varDoubleLor.get()==1:
            minner = Minimizer(funcfsolve, params,fcn_args=(self.modelower,self.modeupper))
            result = minner.minimize()
        elif self.varLor.get()==1:
            print(self.mode)
            minner = Minimizer(funcfsolve, params,fcn_args=(self.mode,0))
            result = minner.minimize()
        elif self.varSplitLor.get()==1:
            minner = Minimizer(funcfsolve, params,fcn_args=(self.mode,0))
            result = minner.minimize()

        
        # J=result.params['J'].value
        # def func(w):
        #     B1=J/(d1*M1*M2)
        #     B2=J/(d2*M1*M2)
        #     Dx1=H+2*Ku1/M1+M2*B1+4*np.pi*M1
        #     Dy1=-H-2*Ku1/M1-M2*B1
        #     Dx2=H+2*Ku2/M2+M1*B2+4*np.pi*M2
        #     Dy2=-H-2*Ku2/M2-M1*B2
        #     return (d1+d2)*(J**2*B2*ga1**2*ga2**2*(w**2-ga2**2*Dx2*Dy2)+d1**2*(w**2+ga1**2*Dx1*Dy1)*(w**2+ga2**2*Dx2*Dy2)**2-J*d1*B2*ga1*ga2*(w**2+ga2**2*Dx2*Dy2)*(2*w**2+ga1*ga2*(Dx1*Dx2-Dy1*Dy2)))

        if self.varDoubleLor.get()==1:
            w_solution = fsolve(func,self.modelower)
            w_solution1 = fsolve(func,self.modeupper)
            self.ax.vlines(w_solution,0,self.resultBkg.params['l_lower_height'].value*1.2)
            self.ax.vlines(w_solution1,0,self.resultBkg.params['l_upper_height'].value*1.2)
        elif self.varLor.get()==1:
            w_solution = fsolve(func,self.mode)
            self.ax.vlines(w_solution,0,self.resultBkg.params['l_height'].value*1.2)
        elif self.varSplitLor.get()==1:
            w_solution = fsolve(func,self.mode)
            self.ax.vlines(w_solution,0,self.resultBkg.params['sl_height'].value*1.2)

        self.entryJ.delete(0,"end")
        self.entryJ.insert(0,J)
        report_fit(result)
        self.canvas.draw()
        return J

    def chi(self):        
        try:
            self.ax1.remove()
        except:
            print('No axis 1')
        self.indicator=1
        #parameters to calc chi, susceptibility of film
        wid=float(self.entrywidth.get())*1e-3
        if int(self.circvar.get())==1 and int(self.squarevar.get())==0:
            A=np.pi*(wid/2)**2
        elif int(self.squarevar.get())==1 and int(self.circvar.get())==0:
            A=wid**2
        else:
            print('Choose shape of sample')
        mu=np.pi*4e-7
        t=(float(self.entryd1.get())+float(self.entryd2.get()))*1e-9
        V=t*A
        w=float(self.entrysampleh.get())*1e-3#width of loop is 4 mm
        W=w**2
        heightloop=1.6e-3 #height of loop is 1.6 mm
        k=2/np.pi*np.arctan(w/heightloop)

        if self.entryGeo.get()=='0':
            psi=0.8
        else:
            psi=float(self.entryGeo.get())

        k_h=k*psi
        selection=self.listboxopen.curselection()
        if len(selection) > 0:
            plotlist = [item for n, item in enumerate(self.filelist) if n in selection]
        else:
            plotlist = self.filelist

        self.ax.clear()

        self.ax.set_xlabel('\u03C9 [rad/s]')
        self.ax.set_ylabel('\u1d61')
        
        if self.axismin.get()!='0':
            minchi=0 #gera ráð fyrir axislimits
            
        for n, item in enumerate(plotlist):
            texti=pd.read_csv(item, index_col=False, comment= "#", sep='\t', engine='python')

            self.freq=texti['freq'].to_numpy(dtype=complex).real*2*np.pi
            real=texti['Za'].to_numpy(dtype=complex).real
            imag=texti['Za'].to_numpy(dtype=complex).imag
            try:
                curr=texti['I'].to_numpy(dtype=complex).real
                print(curr)
            except:
                print('No current measured')
                curr=np.empty(1)

            self.current=curr
            chi=imag*W/(k_h*mu*V*self.freq*4*np.pi)
            chii=real*W/(k_h*mu*V*self.freq*4*np.pi)    #deili með 4 pi til þess að fá í cgs    
            self.chii=chi+1j*chii

            if len(curr)!=1:
                re='Re(\u1d61) '+item.split('/')[-1]+' '+ str(np.nanmean(curr))
                im='Im(\u1d61) '+item.split('/')[-1]+' '+ str(np.nanmean(curr))
            else:
                re='Re(\u1d61) '+item.split('/')[-1]
                im='Im(\u1d61) '+item.split('/')[-1]

            if self.Re.get()==1:
                self.ax.plot(self.freq,self.chii.real,label=re)
            elif self.Im.get()==1:
                self.ax.plot(self.freq,self.chii.imag,label=im)
            else:
                self.ax.plot(self.freq,self.chii.real,label=re)                    
                self.ax.plot(self.freq,self.chii.imag,label=im)

        if self.axismin.get() !='0':
            self.ax.set_xlim(float(self.axismin.get()),float(self.axismax.get()))
            #self.ax.autoscale(axis='y',tight=False)
            #print(max(chi[np.where((self.freq>round(float(self.axismin.get()))) & (self.freq<round(float(self.axismax.get()))))]))# & self.freq<round(float(self.axismax.get()))))
            self.ax.set_ylim(minchi,1.5*max(chii[np.where((self.freq>round(float(self.axismin.get()))) & (self.freq<round(float(self.axismax.get()))))]))
        self.canvas.draw()

    def fwhm(self, dex):
        if self.varTest.get()==1:
            if self.varLinearBkg.get()==1:
                model=LorentzianModel(prefix='l_lower_')+LorentzianModel(prefix='l_upper_')+LinearModel(prefix='line_')
                params = model.make_params(l_upper_amplitude=self.amplupper,l_lower_center=self.modeupper,l_upper_sigma=self.sigmaupper,l_lower_amplitude=self.ampllower,l_lower_sigma=self.sigmalower,line_slope=0,line_intercept=dict(value=0,min=-60,max=60))
            elif self.varQuadBkg.get()==1:
                model=LorentzianModel(prefix='l_lower_')+LorentzianModel(prefix='l_upper_')+LinearModel(prefix='quad_')
                params = model.make_params(l_upper_amplitude=self.amplupper,l_lower_center=self.modeupper,l_upper_sigma=self.sigmaupper,l_lower_amplitude=self.ampllower,l_lower_sigma=self.sigmalower)

            params.add(name='peak_split',value=0.5e10)
            params.set(l_upper_center=dict(expr='l_lower_center + peak_split'))
            lowfreqfit = model.fit(self.ChiIecAlpha, params, x=self.freqfit)
            lowfreqcomp=lowfreqfit.eval_components()
            lowfreqpeak=lowfreqfit.chisqr
            if self.varLinearBkg.get()==1:
                params = model.make_params(l_upper_amplitude=self.amplupper,l_upper_center=self.modeupper,l_upper_sigma=self.sigmaupper,l_lower_amplitude=self.ampllower,l_lower_sigma=self.sigmalower,line_slope=0,line_intercept=dict(value=0,min=-60,max=60))
            elif self.varQuadBkg.get()==1:
                params = model.make_params(l_upper_amplitude=self.amplupper,l_upper_center=self.modeupper,l_upper_sigma=self.sigmaupper,l_lower_amplitude=self.ampllower,l_lower_sigma=self.sigmalower)
            params.add(name='peak_split',value=0.5e10)
            params.set(l_lower_center=dict(expr='l_upper_center - peak_split'))
            highfreqfit = model.fit(self.ChiIecAlpha, params, x=self.freqfit)                    
            highfreqcomp=highfreqfit.eval_components()
            highfreqpeak=highfreqfit.chisqr
            
            if lowfreqpeak<highfreqpeak:
                self.resultBkg=lowfreqfit
                self.comp=lowfreqcomp
            else:
                self.resultBkg=highfreqfit
                self.comp=highfreqcomp

            print(self.resultBkg.fit_report())
            if self.varQuadBkg.get()==1:
                self.ax.plot(self.freqfit,self.comp['l_lower_']+self.comp['l_upper_']+self.comp['quad_'])
            elif self.varLinearBkg.get()==1:
                self.ax.plot(self.freqfit,self.comp['l_lower_']+self.comp['l_upper_']+self.comp['line_'])
            self.ax.plot(self.freqfit,self.ChiIecAlpha)
            self.ax.legend()
            self.canvas.draw()
        if self.varBackgr.get()==1 and self.varTest.get()==0:
            if self.varDoubleLor.get()==1:
                freqspan=self.freq[-1]-self.freq[0]
                peakwith=float(self.entryPwidth.get())
                indexspan=int(round((peakwith/freqspan)*len(self.freq)))
                self.freqfit=self.nfreq[int(round(self.indexmax-indexspan/2)):int(round(self.indexmax+indexspan/2))]
                self.imagfit=self.nimag[int(round(self.indexmax-indexspan/2)):int(round(self.indexmax+indexspan/2))]
                amplitude=self.nimag[self.indexmax]*self.freqfit[0]
                center=self.nfreq[self.indexmax]
                sigma=peakwith/6
                model=LorentzianModel(prefix='l_lower_')+LorentzianModel(prefix='l_upper_')
                if self.varLinearBkg.get()==1 and self.varLogisticBkg.get()==0:
                    model = LinearModel(prefix='line_')+model
                    params = model.make_params(l_upper_amplitude=amplitude,l_lower_center=center,l_upper_sigma=sigma,l_lower_amplitude=amplitude,l_lower_sigma=sigma,line_slope=0,line_intercept=dict(value=0,min=-60,max=60))
                    params.add(name='peak_split',value=0.5e10)
                    params.set(l_upper_center=dict(expr='l_lower_center + peak_split'))
                    init = model.eval(params, x=self.nfreq)
                    lowfreqfit = model.fit(self.imagfit, params, x=self.freqfit)
                    lowfreqcomp=lowfreqfit.eval_components()
                    lowfreqpeak=lowfreqfit.chisqr
                    params = model.make_params(l_upper_amplitude=amplitude,l_upper_center=center,l_upper_sigma=sigma,l_lower_amplitude=amplitude,l_lower_sigma=sigma,line_slope=0,line_intercept=dict(value=0,min=-60,max=60))
                    params.add(name='peak_split',value=0.5e10)
                    params.set(l_lower_center=dict(expr='l_upper_center - peak_split'))
                    init = model.eval(params, x=self.nfreq)
                    highfreqfit = model.fit(self.imagfit, params, x=self.freqfit)                    
                    highfreqcomp=highfreqfit.eval_components()
                    highfreqpeak=highfreqfit.chisqr
            
                    if lowfreqpeak<highfreqpeak:
                        self.resultBkg=lowfreqfit
                        self.comp=lowfreqcomp
                        resonancebkg=self.comp['line_']
                    else:
                        self.resultBkg=highfreqfit
                        self.comp=highfreqcomp
                        resonancebkg=self.comp['line_']

                    self.ax.plot(self.freqfit,self.comp['line_'],'--')
                    self.ax.plot(self.freqfit,self.comp['l_upper_'],':')
                    self.ax.plot(self.freqfit,self.comp['l_lower_'],'.')
                elif self.varQuadBkg.get()==1:
                    model = QuadraticModel(prefix='quad_')+model
                    params = model.make_params(l_upper_amplitude=amplitude,l_lower_center=center,l_upper_sigma=sigma,l_lower_amplitude=amplitude,l_lower_sigma=sigma,line_slope=0,line_intercept=dict(value=0,min=-60,max=60))
                    params.add(name='peak_split',value=0.5e10)
                    params.set(l_upper_center=dict(expr='l_lower_center + peak_split'))
                    init = model.eval(params, x=self.nfreq)
                    lowfreqfit = model.fit(self.imagfit, params, x=self.freqfit)
                    lowfreqcomp=lowfreqfit.eval_components()
                    lowfreqpeak=lowfreqfit.chisqr
                    params = model.make_params(l_upper_amplitude=amplitude,l_upper_center=center,l_upper_sigma=sigma,l_lower_amplitude=amplitude,l_lower_sigma=sigma,line_slope=0,line_intercept=dict(value=0,min=-60,max=60))
                    params.add(name='peak_split',value=0.5e10)
                    params.set(l_lower_center=dict(expr='l_upper_center - peak_split'))
                    init = model.eval(params, x=self.nfreq)
                    highfreqfit = model.fit(self.imagfit, params, x=self.freqfit)                    
                    highfreqcomp=highfreqfit.eval_components()
                    highfreqpeak=highfreqfit.chisqr
            
                    if lowfreqpeak<highfreqpeak:
                        self.resultBkg=lowfreqfit
                        self.comp=lowfreqcomp
                        #resonancebkg=self.comp['line_']
                    else:
                        self.resultBkg=highfreqfit
                        self.comp=highfreqcomp
                        #resonancebkg=self.comp['line_']

                    self.ax.plot(self.freqfit,self.comp['quad_'],'--')
                    self.ax.plot(self.freqfit,self.comp['l_upper_'],':')
                    self.ax.plot(self.freqfit,self.comp['l_lower_'],'.')
                
                elif self.varLogisticBkg.get()==1 and self.varLinearBkg.get()==0:
                    model = model+ StepModel(prefix='step_',form='logistic')
                    params = model.make_params(l_upper_amplitude=amplitude,l_upper_center=center,l_upper_sigma=sigma,l_lower_amplitude=amplitude,l_lower_sigma=sigma,line_slope=0,line_intercept=0)
                    params.add(name='peak_split',value=0.3e10)
                    params.set(l_lower_center=dict(expr='l_upper_center - peak_split'))          
                    init=model.eval(params, x=self.nfreq)
                    self.resultBkg=model.fit(self.imagfit,params,x=self.freqfit)
                    self.comp=self.resultBkg.eval_components()
                    resonancebkg=self.comp['step_']
                    self.ax.plot(self.freqfit, self.comp['step_'],'--')
                    self.ax.plot(self.freqfit,self.comp['l_upper_'],':')
                    self.ax.plot(self.freqfit,self.comp['l_lower_'],'.')
                    
                elif self.varLinearBkg.get()==1 and self.varLogisticBkg.get()==1:
                    model=model + StepModel(prefix='step_',form='logistic')+ LinearModel(prefix='line_')
                    params = model.make_params(l_upper_amplitude=amplitude,l_upper_center=center,l_upper_sigma=sigma,l_lower_amplitude=amplitude,l_lower_sigma=sigma,line_slope=0,line_intercept=0)
                    params.add(name='peak_split',value=0.3e10)
                    params.set(l_lower_center=dict(expr='l_upper_center - peak_split'))
                
                    init = model.eval(params, x=self.nfreq)
                    self.resultBkg =model.fit(self.imagfit,params,x=self.freqfit)
                    self.comp=self.resultBkg.eval_components()
                    self.ax.plot(self.freqfit,self.comp['step_'],'--')
                    self.ax.plot(self.freqfit,self.comp['line_'],'o-',markersize=0.5)
                    resonancebkg=self.comp['step_']+self.comp['line_']
                    self.ax.plot(self.freqfit,self.comp['l_upper_'],':')
                    self.ax.plot(self.freqfit,self.comp['l_lower_'],'.')

            
                print(self.resultBkg.fit_report())
                self.status.insert(END, '-------------------------')
                self.status.insert(END, f'AIC {self.resultBkg.aic}')
                self.status.insert(END, f'Chisqr {self.resultBkg.chisqr}')
                self.status.insert(END, f'RedChi {self.resultBkg.redchi}')
                self.status.insert(END, f'Bic {self.resultBkg.bic}')
                self.status.yview(END)
                self.ax.plot(self.freqfit, self.resultBkg.best_fit,'-',label='fit',color=colors(0))

                self.amplupper=self.resultBkg.params['l_upper_amplitude'].value#+self.shift
                self.modeupper=self.resultBkg.params['l_upper_center'].value
                self.sigmaupper=self.resultBkg.params['l_upper_sigma'].value
                self.varianceupper=self.resultBkg.params['l_upper_fwhm'].value
                resonancearrayupper=self.comp['l_upper_']
                self.ampllower=self.resultBkg.params['l_lower_amplitude'].value#+self.shift
                self.modelower=self.resultBkg.params['l_lower_center'].value
                self.sigmalower=self.resultBkg.params['l_lower_sigma'].value
                self.variancelower=self.resultBkg.params['l_lower_fwhm'].value
                resonancearraylower=self.comp['l_lower_']
                
                self.maxima=self.freqfit[np.where(self.resultBkg.best_fit==max(self.resultBkg.best_fit))]            
                self.ax.legend()
                self.canvas.draw()

            elif self.varLor.get()==1:
                model=LorentzianModel(prefix='l_')
                freqspan=self.freq[-1]-self.freq[0]
                peakwith=float(self.entryPwidth.get())
                indexspan=int(round((peakwith/freqspan)*len(self.freq)))
                self.freqfit=self.nfreq[int(round(self.indexmax-indexspan/2)):int(round(self.indexmax+indexspan/2))]
                self.imagfit=self.nimag[int(round(self.indexmax-indexspan/2)):int(round(self.indexmax+indexspan/2))]
                amplitude=self.nimag[self.indexmax]*self.freqfit[0]
                center=self.nfreq[self.indexmax]
                sigma=peakwith/6          
                model = LinearModel(prefix='line_')+model
                params = model.make_params(l_amplitude=amplitude,l_center=center,l_sigma=sigma,line_slope=0,line_intercept=dict(value=0,min=-60,max=60))
                self.resultBkg=model.fit(self.imagfit,params,x=self.freqfit)
                self.comp=self.resultBkg.eval_components()
                self.ax.plot(self.freqfit,self.comp['line_'],'o-',markersize=0.5)
                self.ax.plot(self.freqfit,self.comp['l_'],'.',markersize=0.5)
                print(self.resultBkg.fit_report())
                self.status.insert(END, '-------------------------')
                self.status.insert(END, f'AIC {self.resultBkg.aic}')
                self.status.insert(END, f'Chisqr {self.resultBkg.chisqr}')
                self.status.insert(END, f'RedChi {self.resultBkg.redchi}')
                self.status.insert(END, f'Bic {self.resultBkg.bic}')
                self.status.yview(END)
                self.ax.plot(self.freqfit, self.resultBkg.best_fit,'-',label='fit',color=colors(0))

                self.ampl=self.resultBkg.params['l_amplitude'].value#+self.shift
                self.mode=self.resultBkg.params['l_center'].value
                self.sigma=self.resultBkg.params['l_sigma'].value
                self.variance=self.resultBkg.params['l_fwhm'].value
                
                self.maxima=self.freqfit[np.where(self.resultBkg.best_fit==max(self.resultBkg.best_fit))]            
                self.ax.legend()
                self.canvas.draw()
            elif self.varSplitLor.get()==1:
                model=SplitLorentzianModel(prefix='sl_')
                freqspan=self.freq[-1]-self.freq[0]
                peakwith=float(self.entryPwidth.get())
                indexspan=int(round((peakwith/freqspan)*len(self.freq)))
                self.freqfit=self.nfreq[int(round(self.indexmax-indexspan/2)):int(round(self.indexmax+indexspan/2))]
                self.imagfit=self.nimag[int(round(self.indexmax-indexspan/2)):int(round(self.indexmax+indexspan/2))]
                amplitude=self.nimag[self.indexmax]*self.freqfit[0]
                center=self.nfreq[self.indexmax]
                sigma=peakwith/6
                model = LinearModel(prefix='line_')+model
                params = model.make_params(sl_amplitude=amplitude,sl_center=center,sl_sigma=sigma,line_slope=0,line_intercept=dict(value=0,min=-60,max=60))
                self.resultBkg=model.fit(self.imagfit,params,x=self.freqfit)
                self.comp=self.resultBkg.eval_components()
                self.ax.plot(self.freqfit,self.comp['line_'],'o-',markersize=0.5)
                self.ax.plot(self.freqfit,self.comp['sl_'],'.',markersize=0.5)
                print(self.resultBkg.fit_report())
                self.status.insert(END, '-------------------------')
                self.status.insert(END, f'AIC {self.resultBkg.aic}')
                self.status.insert(END, f'Chisqr {self.resultBkg.chisqr}')
                self.status.insert(END, f'RedChi {self.resultBkg.redchi}')
                self.status.insert(END, f'Bic {self.resultBkg.bic}')
                self.status.yview(END)
                self.ax.plot(self.freqfit, self.resultBkg.best_fit,'-',label='fit',color=colors(0))
                self.ampl=self.resultBkg.params['sl_amplitude'].value#+self.shift
                self.mode=self.resultBkg.params['sl_center'].value
                self.sigma=self.resultBkg.params['sl_sigma'].value
                self.sigma_r=self.resultBkg.params['sl_sigma_r'].value
                self.variance=self.resultBkg.params['sl_fwhm'].value
                self.maxima=self.freqfit[np.where(self.resultBkg.best_fit==max(self.resultBkg.best_fit))]            
                self.ax.legend()
                self.canvas.draw()
            
        elif self.varBackgr.get()==0 and self.varTest.get()==0:
            freqspan=self.freq[-1]-self.freq[0]
            peakwith=float(self.entryPwidth.get())
            indexspan=int(round((peakwith/freqspan)*len(self.freq)))
            self.freqfit=self.nfreq[int(round(self.indexmax-indexspan/2)):int(round(self.indexmax+indexspan/2))]
            self.imagfit=self.nimag[int(round(self.indexmax-indexspan/2)):int(round(self.indexmax+indexspan/2))]
            amplitude=self.nimag[self.indexmax]*self.freqfit[0]
            center=self.nfreq[self.indexmax]
            sigma=peakwith/6
            model=LorentzianModel(prefix='l_lower_')+LorentzianModel(prefix='l_upper_')
            params = model.make_params(l_upper_amplitude=amplitude,l_upper_center=center,l_upper_sigma=sigma,l_lower_amplitude=amplitude,l_lower_sigma=sigma)
            params.add(name='peak_split',value=0.3e10)
            params.set(l_lower_center=dict(expr='l_upper_center - peak_split'))
                
            init = model.eval(params, x=self.nfreq)
            self.resultBkg =model.fit(self.imagfit,params,x=self.freqfit)
            self.comp=self.resultBkg.eval_components()
            print(self.resultBkg.fit_report())
            self.ax.plot(self.freqfit, self.resultBkg.best_fit,'-',label='fit',color=colors(0))
            self.amplupper=self.resultBkg.params['l_upper_amplitude'].value#+self.shift
            self.modeupper=self.resultBkg.params['l_upper_center'].value
            self.sigmaupper=self.resultBkg.params['l_upper_sigma'].value
            self.varianceupper=self.resultBkg.params['l_upper_fwhm'].value
            resonancearrayupper=self.comp['l_upper_']
            self.ampllower=self.resultBkg.params['l_lower_amplitude'].value#+self.shift
            self.modelower=self.resultBkg.params['l_lower_center'].value
            self.sigmalower=self.resultBkg.params['l_lower_sigma'].value
            self.variancelower=self.resultBkg.params['l_lower_fwhm'].value
            resonancearraylower=self.comp['l_lower_']
                
            self.maxima=self.freqfit[np.where(self.resultBkg.best_fit==max(self.resultBkg.best_fit))]            
            self.ax.legend()
            self.canvas.draw()
            

    def peak_finder(self):
        self.iterator=1
        
        entryorder=int(self.entryorder.get())
        print(self.filelist[0].split('_')[-1].replace('G.dat',''))

        self.chi()
        self.nfreq=self.freq[np.where(self.freq>0.3e10)]
        self.real=self.chii.real[np.where(self.freq>0.3e10)]
        self.nimag=self.chii.imag[np.where(self.freq>0.3e10)]
        
        if self.axismin.get() !='0':
            self.chi()
            self.imag=self.chii.imag
            self.real=self.chii.real
            self.nimag = self.imag[np.where((self.freq>round(float(self.axismin.get()))) & (self.freq<round(float(self.axismax.get()))))]
            self.nfreq = self.freq[np.where((self.freq>round(float(self.axismin.get()))) & (self.freq<round(float(self.axismax.get()))))]
            #self.ax.set_xlim(float(self.axismin.get()),float(self.axismax.get()))
            #self.ax.set_ylim(min(self.nimag),1.5*max(self.nimag))
            self.peaks_imag = signal.argrelextrema(self.nimag,np.greater,order=entryorder)
            self.ax.plot(self.nfreq[self.peaks_imag],self.nimag[self.peaks_imag], 'o')
            self.indexmax=int(np.where(max(self.nimag[self.peaks_imag])==self.nimag)[0])
            self.ax.plot(self.nfreq[self.indexmax],self.nimag[self.indexmax],'x')
            print(type(self.indexmax))
        else:
            self.peaks_imag = signal.argrelextrema(self.nimag,np.greater,order=entryorder)
            self.ax.plot(self.nfreq[self.peaks_imag],self.nimag[self.peaks_imag],'o')
            self.indexmax=np.where(max(self.nimag[self.peaks_imag])==self.nimag)[0][0]
            self.ax.plot(self.nfreq[self.indexmax],max(self.nimag[self.peaks_imag]),'x') 
        #self.ax.autoscale(axis='y',tight=True)
        self.canvas.draw()
        #self.peaks_real=np.array(self.peaks_real)
        self.peaks_imag=np.array(self.peaks_imag)
        self.fwhm(0)


class Viewer2(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.buttonframe=tk.Frame(self)
        self.buttonframe.grid(row=0,column=11, columnspan=2,rowspan=2,sticky='wn')
        tk.Button(self.buttonframe, text="Measure", command=lambda: controller.show_frame(Measure), width=8, height=1, font=fontconf).grid(row=0,column=0,padx=5)
        #tk.Button(self.buttonframe, text="Viewer", command=lambda: controller.show_frame(Viewer2), width=8, height=1, font=fontconf).grid(row=0,column=1)
        tk.Button(self.buttonframe, text="Batch", command=lambda: controller.show_frame(Batch), width=8, height=1, font=fontconf).grid(row=1, column=0, sticky='n', padx=5)
        tk.Button(self.buttonframe, text="Calibrate", command=lambda: controller.show_frame(Calibrate), width=8, height=1, font=fontconf).grid(row=1,column=1, sticky='n')
        tk.Button(self.buttonframe, text="IEC", command=lambda: controller.show_frame(IEC),width=8,height=1,font=fontconf).grid(row=0,column=1)
        tk.Button(self, text="Exit", command=self._quit, font=fontconf).grid(row=0, column=18, sticky='ne')
        self.buttonframe.columnconfigure(0,weight=1)
        self.buttonframe.columnconfigure(1,weight=1)
        self.plotframe=tk.Frame(self)
        self.plotframe.grid(row=4, column=15, columnspan=10,rowspan=6)
        tk.Button(self.plotframe, text="Open", command=self.file_open, font=fontconf).grid(row=0, column=0)
        tk.Button(self.plotframe, text="Plot", command=self.plot,width=6, font=fontconf).grid(row=1, column=1,sticky='w')
        tk.Label(self, text="Selection",relief='ridge', font=fontconf).grid(row=4, column=14)
        self.Re=tk.IntVar() 
        self.Im=tk.IntVar()
        self.Re.set(0)
        self.Im.set(0)
        tk.Checkbutton(self.plotframe, text='Re', variable=self.Re, font=fontconf).grid(row=2,column=0)
        tk.Checkbutton(self.plotframe, text='Im', variable=self.Im, font=fontconf).grid(row=2,column=1,sticky='w')       
        self.plotframe.columnconfigure(0,weight=1)
        self.plotframe.columnconfigure(1,weight=1)
        for i in np.arange(0,10):
            self.plotframe.rowconfigure(i,weight=1)
        
        self.listbox=tk.Listbox(self.plotframe, width=14, height=6, bg='Azure2')
        self.listbox.grid(row=3, column=0,columnspan=2)
        self.elements=["Za", "angle","polar","EA", "Ku", "EA-Ku", 'Cubic Koh (100)', "Cubic Koh (100)+uni","Cubic Koh (110)", "S11a", "S11m", "S11o", "S11l", "S11s", "Edf", "Erf", "Esf"]
        
        for i, ele in enumerate(self.elements):
            self.listbox.insert(i, ele)

        self.editframe=tk.Frame(self)
        self.editframe.grid(row=5,column=11,columnspan=2,rowspan=4,sticky='wn')
        self.chitype=tk.IntVar()
        self.chitype.set(0)
        self.titlevar=tk.IntVar()
        self.titlevar.set(0)
        tk.Checkbutton(self.editframe, text='Title', variable=self.titlevar, command=self.title, font=fontconf).grid(row=5,column=11,sticky='w')
        self.custvar=tk.IntVar()
        self.custvar.set(0)
        tk.Checkbutton(self.editframe, text='Legend', variable=self.custvar, command=self.custom, font=fontconf).grid(row=7,column=11,sticky='nw')
        self.shiftvar=tk.IntVar()
        self.shiftvar.set(0)
        tk.Checkbutton(self.editframe, text='Shift', variable=self.shiftvar, command=self.shift, font=fontconf).grid(row=6,column=11,sticky='w')
        #Self variable for saving fit parameters
        self.alpha_delta=0
        self.t_delta=0
        self.t_alpha_corr=0
        
        self.listboxopen=tk.Listbox(self.plotframe, selectmode=tk.EXTENDED, height=6, width=22)
        self.listboxopen.grid(row=3, column=2, rowspan=4, columnspan=8)
        tk.Button(self.plotframe, text="Remove", command=self.listbox_delete,width=6, font=fontconf).grid(row=0, column=1,sticky='w')
        self.plotframe.bind_all('<Delete>', lambda e:self.listbox_delete())
        self.filelist=[]
        tk.Button(self.plotframe, text='up', command=lambda: self.reArrangeListbox("up"), font=fontconf).grid(row=0, column=3)
        tk.Button(self.plotframe, text='dn', command=lambda: self.reArrangeListbox("dn"), font=fontconf).grid(row=1, column=3)
        
        #tk.Label(self, text="Analysis", relief='ridge').grid(row=7, column=13)

        self.chipeakframe=tk.Frame(self)
        self.chipeakframe.grid(row=10,column=14,columnspan=6,rowspan=3)
        self.peak=tk.Button(self.chipeakframe, text="Peak", command=self.peak_finder, width=4, font=fontconf).grid(row=0, column=1,sticky='w')
        #tk.Button(self.chipeakframe, text="+", command=lambda: self.jump_right(0)).grid(row=0, column=3, sticky='w')
        #tk.Button(self.chipeakframe, text="-", command=lambda: self.jump_left(0)).grid(row=0, column=2, sticky='e')
        self.chipeakframe.bind_all('<p>', lambda e:self.peak_finder())
        tk.Button(self.chipeakframe, text='Save', command=self.save, font=fontconf).grid(row=1, column=1)
        tk.Button(self.chipeakframe, text='Create', command=self.save_as,width=5, font=fontconf).grid(row=1, column=0)
        tk.Label(self.chipeakframe, text="Order", font=fontconf).grid(row=0, column=4, sticky='e')
        tk.Label(self.chipeakframe, text="Peak W.", font=fontconf).grid(row=1,column=4,sticky='e')
        self.savetype=tk.IntVar()
        self.savetype.set(0)
        tk.Checkbutton(self.chipeakframe, text='s. \u03B1', variable=self.savetype,font=fontconf).grid(row=0,column=6,sticky='e')
        self.entryPwidth=tk.Entry(self.chipeakframe,width=5)
        self.entryPwidth.insert(0,"8e9")
        self.entryPwidth.grid(row=1,column=5)
        self.entryorder=tk.Entry(self.chipeakframe, width=5)
        self.entryorder.insert(0,"50")
        self.entryorder.grid(row=0, column=5)
        tk.Button(self.chipeakframe, text="Chi", command=self.chi, width=5, font=fontconf).grid(row=0, column=0,sticky='e')
        self.chipeakframe.bind_all('<o>', lambda e:self.chi())
        self.chipeakframe.bind_all('<i>', lambda e:self.save())        

        self.circvar=tk.IntVar()
        self.circvar.set(1)
        self.squarevar=tk.IntVar()
        self.sampleframe=tk.Frame(self)
        self.sampleframe.grid(row=13,column=15,rowspan=4, columnspan=2)
        self.circ=tk.Checkbutton(self.sampleframe, text="Circular", variable=self.circvar, font=fontconf)
        self.square=tk.Checkbutton(self.sampleframe, text="Square", variable=self.squarevar, font=fontconf)
        tk.Label(self, text="Sample", relief='ridge', font=fontconf).grid(row=13, column=14)
        tk.Label(self.sampleframe, text="Width [mm]", font=fontconf).grid(row=0, column=0,sticky='e')
        tk.Label(self.sampleframe, text="Thickness [nm]", font=fontconf).grid(row=1, column=0,sticky='e')
        tk.Label(self.sampleframe, text="Sampleh. width [mm]", font=fontconf).grid(row=2,column=0,sticky='e')
        self.circ.grid(row=4, column=0)
        self.square.grid(row=4, column=1)
        self.entrywidth = tk.Entry(self.sampleframe,width=5)
        self.entrywidth.insert(0, "4")
        self.entrywidth.grid(row=0, column=1)
        self.entrythick = tk.Entry(self.sampleframe,width=5)
        self.entrythick.insert(0, "50")
        self.entrythick.grid(row=1, column=1)
        self.entrysampleh=tk.Entry(self.sampleframe,width=5)
        self.entrysampleh.insert(0,"4")
        self.entrysampleh.grid(row=2,column=1)
        
        tk.Label(self, text="FWHM", relief='ridge', font=fontconf).grid(row=17, column=14)
        self.fwhmframe=tk.Frame(self)
        self.fwhmframe.grid(row=17,column=15, rowspan=2,columnspan=4)
        self.fwhmframe.bind_all('<r>', lambda e:self.fwhm(1))
        for i in np.arange(0,3):
            self.fwhmframe.columnconfigure(i,weight=1)
        
        tk.Label(self, text='Axis limits',relief='ridge', font=fontconf).grid(row=18,column=14,sticky='n')
        tk.Label(self.fwhmframe,text='Horiz', font=fontconf).grid(row=1,column=0)
        fwhmfr=self.fwhmframe
        self.axismin,self.axismax=tk.Entry(fwhmfr,width=6),tk.Entry(fwhmfr,width=6)
        i=0
        for F in (self.axismin,self.axismax):
            F.insert(0,'0')
            if i<2:
                F.grid(row=1,column=i+1)
            else:
                F.grid(row=2,column=i-1)
            i+=1

        self.AngVar=tk.IntVar(self)
        self.AngVar.set(1)
        self.Changular=tk.Checkbutton(self.fwhmframe,text='Ang. freq', variable=self.AngVar, font=fontconf).grid(row=1,column=0)
        tk.Label(self, text='Fit')
        self.varGauss, self.varLor, self.varSplitLor, self.varDoubleLor=tk.IntVar(self),tk.IntVar(self), tk.IntVar(self), tk.IntVar(self)
        self.Gauss=tk.Checkbutton(self.fwhmframe, text="Gaussian", variable=self.varGauss, font=fontconf).grid(row=0,column=0)#,command=lambda: self.set_checkfit(0)
        self.Lorentz=tk.Checkbutton(self.fwhmframe, text="Lorentzian", variable=self.varLor, font=fontconf).grid(row=0,column=1)#,command=lambda: self.set_checkfit(1)
        self.Lorentzsplit=tk.Checkbutton(self.fwhmframe, text="Split.Lor", variable=self.varSplitLor, font=fontconf).grid(row=0,column=2)
        self.Lorentzdouble=tk.Checkbutton(self.fwhmframe, text="Double.Lor", variable=self.varDoubleLor, font=fontconf).grid(row=0,column=3)
        self.varGauss.set(0)
        self.varLor.set(1)

        self.fitchivar=tk.IntVar(self)
        self.fitchi=tk.Checkbutton(self,text="Fit Chi", variable=self.fitchivar,command=self.fitchiframe, relief='ridge', font=fontconf).grid(row=19,column=14)

        #tk.Button(self, text='Edit', command=self.openpop).grid(row=20,column=15)        
        self.fig = plt.figure(constrained_layout=True,figsize=[10,4.5])
        self.ax = plt.subplot()
        self.ax.set_xlabel('$f$ [Hz]')
        self.ax.set_ylabel('S11')
        
        self.canvas=FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().grid(row=0, column=0, rowspan=30, columnspan=10, sticky='nwse')
        self.toolbarframe=tk.Frame(self)
        self.toolbarframe.grid(row=31, column=0, columnspan=10, sticky='nswe')
        self.toolbar=NavigationToolbar2Tk(self.canvas, self.toolbarframe)
        self.toolbar.grid(row=0, column=0, columnspan=10, sticky='nswe')
        for i in np.arange(0,33):
            self.rowconfigure(i, weight=1)

        self.columnconfigure(0,weight=1)
        self.columnconfigure(1,weight=1)
        self.columnconfigure(2,weight=2)
        self.columnconfigure(3,weight=3)
                
        self.indexmax=4
        self.indexmin=0
        self.peakpos=[0,0]
        self.iterator=0

    def openpop(self):
        popup(self)

    def set_checkfit(self,arg):  #function that runs with the source checkbuttons, when current is chosen the voltage checkbutton unchecks and vice versa
        if arg==0:
            self.varGauss.set(1)
            self.varLor.set(0)
        elif arg==1:
            self.varGauss.set(0)
            self.varLor.set(1)
        elif arg==2:
            self.varLeastsq.set(1)
            self.varShgo.set(0)
        elif arg==3:
            self.varLeastsq.set(0)
            self.varShgo.set(1)
            
    def set_checkcurr(self,arg):
        for i, ele in enumerate(self.checklista):
            if i!=arg:
                ele.set(0)
                
    def save_as(self):
        filename = tk.filedialog.asksaveasfilename(defaultextension="*.txt")
        skjal=open(filename,'w')
        if int(self.savetype.get())==1:
            skjal.write('Field[G]\tGamma\tKu[erg/cm^3]\talpha\tdelta_alpha\tThickness[nm]\tdelta_Thickness[nm]\tM[emu/cm^3]\tThickness_alpha_correlation\tAkaike\tBayesian\tChi-squared\tReduced Chi-squared\n')
        else:
            if self.varDoubleLor.get()==1:
                skjal.write('Filename\tAmplitudeL\tMeanL[Hz]\tStddevL[Hz]\tFWHML[Hz]\tAmplitudeU\tMeanU[Hz]\tStddevU[Hz]\tFWHMU[Hz]\tI_EA [A]\n')
            else:
                skjal.write('Filename\tAmplitude\tMean[Hz]\tStddev[Hz]\tFWHM[Hz]\tI_EA [A]\n') 
        skjal.close()
        self.skjal=filename

    def save(self):
        try:
            t=self.skjal
        except:
            t=tk.filedialog.askopenfilename()
            self.skjal=t
            
        skjal=open(t,'a')
        if int(self.savetype.get())==1:
            gamma=float(self.entryGamma.get())
            M=float(self.entryMs.get())
            K_u=float(self.entryKu.get())
            t=float(self.entryT.get())*1e-9
            H=float(self.filelist[0].split('_')[-1].split('.')[0])
            alpha=float(self.entryAlpha.get())
            lina=f'{H}\t{gamma}\t{K_u}\t{alpha}\t{self.alpha_delta}\t{t}\t{self.t_delta}\t{M}\t{self.t_alpha_corr}\t{self.resultBkg.aic}\t{self.resultBkg.bic}\t{self.resultBkg.chisqr}\t{self.resultBkg.redchi}\n'
        else:
            selection=self.listboxopen.curselection()
            if len(selection) > 0:
                plotlist = [item for n, item in enumerate(self.filelist) if n in selection]
            else:
                plotlist = self.filelist
            nafn=plotlist[0].split('/')[-1].split('.')[0]+'G'
            if self.varDoubleLor.get()==1:
                lina=f'{nafn}\t{self.ampllower}\t{float(self.modelower)}\t{self.sigmalower}\t{self.variancelower}\t{self.amplupper}\t{self.modeupper}\t{self.sigmaupper}\t{self.varianceupper}\t{np.nanmean(self.current)}\t{self.variancelower_delta}\t{self.varianceupper_delta}\n'
            else:
                lina=f'{nafn}\t{self.ampl}\t{float(self.mode)}\t{self.sigma}\t{self.variance}\t{np.nanmean(self.current)}\n'
        skjal.write(lina)
        skjal.close()

    def fwhm(self, dex):
        if self.varBackgr.get()==1:
            model = LorentzianModel(prefix='l_') + LinearModel(prefix='line_')+GaussianModel(prefix='g_')
            freqspan=self.freq[-1]-self.freq[0]
            peakwith=float(self.entryPwidth.get())
            indexspan=int(round((peakwith/freqspan)*len(self.freq)))
            if self.indexmax+indexspan/2>len(self.nfreq):
                self.freqfit=self.nfreq[int(round(self.indexmax-indexspan/2)):-1]
                self.imagfit=self.nimag[int(round(self.indexmax-indexspan/2)):-1]
            else:
                self.freqfit=self.nfreq[int(round(self.indexmax-indexspan/2)):int(round(self.indexmax+indexspan/2))]
                self.imagfit=self.nimag[int(round(self.indexmax-indexspan/2)):int(round(self.indexmax+indexspan/2))]
            amplitude=self.nimag[self.indexmax]*self.freqfit[0]
            center=self.nfreq[self.indexmax]
            sigma=peakwith/6
            if self.varGauss.get()==1 and self.varLor.get()==1:
                model=LorentzianModel(prefix='l_')+GaussianModel(prefix='g_')
                typeoffit='both'
            elif self.varGauss.get()==1 and self.varLor.get()==0:
                model=GaussianModel(prefix='g_')
                typeoffit='gauss'
            elif self.varSplitLor.get()==1:
                model=SplitLorentzianModel(prefix='sl_')
                typeoffit='SplitLor'
            elif self.varDoubleLor.get()==1:
                model=LorentzianModel(prefix='l_lower_')+LorentzianModel(prefix='l_upper_')
                typeoffit='DoubleLor'
            else:
                model=LorentzianModel(prefix='l_')
                typeoffit='lor'
                
                
            if self.varLinearBkg.get()==0 and self.varQuadBkg.get()==1:
                model = QuadraticModel(prefix='line_')+model
                if typeoffit=='both':
                    params = model.make_params(l_amplitude=amplitude, l_center=center, l_sigma=sigma,g_sigma=0.5*sigma)
                    params.add(name='total_amplitude', value=amplitude*1.1)
                    params.set(g_amplitude=dict(expr='total_amplitude - l_amplitude',min=0))
                    params.set(g_center=dict(expr='l_center'))
        
                elif typeoffit=='gauss':
                    params = model.make_params(g_amplitude=amplitude, g_center=center, g_sigma=sigma)
                elif typeoffit=='SplitLor':
                    params = model.make_params(sl_amplitude=amplitude, sl_center=center, sl_sigma=sigma,sl_sigma_r=sigma)
                elif typeoffit=='DoubleLor':
                    params = model.make_params(l_upper_amplitude=amplitude,l_lower_center=center,l_upper_sigma=sigma,l_lower_amplitude=amplitude,l_lower_sigma=sigma)
                    params.add(name='peak_split',value=0.3e10)
                    params.set(l_upper_center=dict(expr='l_lower_center + peak_split'))
                    init = model.eval(params, x=self.nfreq)
                    lowfreqfit = model.fit(self.imagfit, params, x=self.freqfit)
                    lowfreqcomp=lowfreqfit .eval_components()
                    lowfreqpeak=lowfreqfit .chisqr

                    params = model.make_params(l_upper_amplitude=amplitude,l_upper_center=center,l_upper_sigma=sigma,l_lower_amplitude=amplitude,l_lower_sigma=sigma)
                    params.add(name='peak_split',value=0.3e10)
                    params.set(l_lower_center=dict(expr='l_upper_center - peak_split'))
                    init = model.eval(params, x=self.nfreq)
                    highfreqfit = model.fit(self.imagfit, params, x=self.freqfit)
                    highfreqcomp=highfreqfit.eval_components()
                    highfreqpeak=highfreqfit.chisqr
                    if lowfreqpeak<highfreqpeak:
                        self.resultBkg=lowfreqfit
                        self.comp=lowfreqcomp
                        resonancebkg=self.comp['line_']
                    else:
                        self.resultBkg=highfreqfit
                        self.comp=highfreqcomp
                        resonancebkg=self.comp['line_']

                else:
                    params = model.make_params(l_amplitude=amplitude, l_center=center, l_sigma=sigma)

                if typeoffit!='DoubleLor':    
                    init = model.eval(params, x=self.nfreq)
                    self.resultBkg = model.fit(self.imagfit, params, x=self.freqfit)
                    self.comp=self.resultBkg.eval_components()
                    resonancebkg=self.comp['line_']

                self.ax.plot(self.freqfit,self.comp['line_'],'--')
                if typeoffit=='both':
                    self.ax.plot(self.freqfit,self.comp['l_'],':')
                    self.ax.plot(self.freqfit,self.comp['g_'],'.')
                elif typeoffit=='gauss':
                    self.ax.plot(self.freqfit,self.comp['g_'],'.')
                elif typeoffit=='SplitLor':
                    self.ax.plot(self.freqfit,self.comp['sl_'],'.')
                elif typeoffit=='DoubleLor':
                    self.ax.plot(self.freqfit,self.comp['l_upper_'],':')
                    self.ax.plot(self.freqfit,self.comp['l_lower_'],'.')
                else:
                    self.ax.plot(self.freqfit,self.comp['l_'],':')
            
            if self.varLinearBkg.get()==1 and self.varLogisticBkg.get()==0:
                model = LinearModel(prefix='line_')+model
                if typeoffit=='both':
                    params = model.make_params(l_amplitude=amplitude, l_center=center, l_sigma=sigma,g_sigma=0.5*sigma,line_slope=0, line_intercept=0)
                    params.add(name='total_amplitude', value=amplitude*1.1)
                    params.set(g_amplitude=dict(expr='total_amplitude - l_amplitude',min=0))
                    params.set(g_center=dict(expr='l_center'))
        
                elif typeoffit=='gauss':
                    params = model.make_params(g_amplitude=amplitude, g_center=center, g_sigma=sigma,line_slope=0, line_intercept=0)
                elif typeoffit=='SplitLor':
                    params = model.make_params(sl_amplitude=amplitude, sl_center=center, sl_sigma=sigma,sl_sigma_r=sigma,line_slope=0, line_intercept=0)
                elif typeoffit=='DoubleLor':
                    params = model.make_params(l_upper_amplitude=amplitude,l_lower_center=center,l_upper_sigma=sigma,l_lower_amplitude=amplitude,l_lower_sigma=sigma,line_slope=0,line_intercept=0)
                    params.add(name='peak_split',value=0.3e10)
                    params.set(l_upper_center=dict(expr='l_lower_center + peak_split'))
                    init = model.eval(params, x=self.nfreq)
                    lowfreqfit = model.fit(self.imagfit, params, x=self.freqfit)
                    lowfreqcomp=lowfreqfit .eval_components()
                    lowfreqpeak=lowfreqfit .chisqr

                    params = model.make_params(l_upper_amplitude=amplitude,l_upper_center=center,l_upper_sigma=sigma,l_lower_amplitude=amplitude,l_lower_sigma=sigma,line_slope=0,line_intercept=0)
                    params.add(name='peak_split',value=0.3e10)
                    params.set(l_lower_center=dict(expr='l_upper_center - peak_split'))
                    init = model.eval(params, x=self.nfreq)
                    highfreqfit = model.fit(self.imagfit, params, x=self.freqfit)
                    highfreqcomp=highfreqfit.eval_components()
                    highfreqpeak=highfreqfit.chisqr
                    if lowfreqpeak<highfreqpeak:
                        self.resultBkg=lowfreqfit
                        self.comp=lowfreqcomp
                        resonancebkg=self.comp['line_']
                    else:
                        self.resultBkg=highfreqfit
                        self.comp=highfreqcomp
                        resonancebkg=self.comp['line_']

                else:
                    params = model.make_params(l_amplitude=amplitude, l_center=center, l_sigma=sigma,line_slope=0, line_intercept=0)

                if typeoffit!='DoubleLor':    
                    init = model.eval(params, x=self.nfreq)
                    self.resultBkg = model.fit(self.imagfit, params, x=self.freqfit)
                    self.comp=self.resultBkg.eval_components()
                    resonancebkg=self.comp['line_']

                self.ax.plot(self.freqfit,self.comp['line_'],'--')
                if typeoffit=='both':
                    self.ax.plot(self.freqfit,self.comp['l_'],':')
                    self.ax.plot(self.freqfit,self.comp['g_'],'.')
                elif typeoffit=='gauss':
                    self.ax.plot(self.freqfit,self.comp['g_'],'.')
                elif typeoffit=='SplitLor':
                    self.ax.plot(self.freqfit,self.comp['sl_'],'.')
                elif typeoffit=='DoubleLor':
                    self.ax.plot(self.freqfit,self.comp['l_upper_'],':')
                    self.ax.plot(self.freqfit,self.comp['l_lower_'],'.')
                else:
                    self.ax.plot(self.freqfit,self.comp['l_'],':')
                    
            elif self.varLogisticBkg.get()==1 and self.varLinearBkg.get()==0:
                model = model+ StepModel(prefix='step_',form='logistic')
                if typeoffit=='both':
                    params=model.make_params(l_amplitude=amplitude, l_center=center, l_sigma=sigma,g_sigma=0.5*sigma, step_amplitude=0,step_center=center,step_sigma=10e9)
                    params.add(name='total_amplitude', value=amplitude*1.1)
                    params.set(g_amplitude=dict(expr='total_amplitude - l_amplitude', min=0))
                    params.set(g_center=dict(expr='l_center'))

                elif typeoffit=='gauss':
                    params = model.make_params(g_amplitude=amplitude, g_center=center, g_sigma=sigma,step_amplitude=0,step_center=center,step_sigma=10e9)
                elif typeoffit=='SplitLor':
                    params = model.make_params(sl_amplitude=amplitude, sl_center=center, sl_sigma=sigma, sl_sigma_r=sigma,step_amplitude=0,step_center=center,step_sigma=10e9)
                elif typeoffit=='DoubleLor':
                    params = model.make_params(l_upper_amplitude=amplitude,l_upper_center=center,l_upper_sigma=sigma,l_lower_amplitude=amplitude,l_lower_sigma=sigma,line_slope=0,line_intercept=0)
                    params.add(name='peak_split',value=0.3e10)
                    params.set(l_lower_center=dict(expr='l_upper_center - peak_split'))
                else:
                    params = model.make_params(l_amplitude=amplitude, l_center=center, l_sigma=sigma,step_amplitude=0,step_center=center,step_sigma=10e9)
                    
                init=model.eval(params, x=self.nfreq)
                self.resultBkg=model.fit(self.imagfit,params,x=self.freqfit)
                self.comp=self.resultBkg.eval_components()
                resonancebkg=self.comp['step_']
                self.ax.plot(self.freqfit, self.comp['step_'],'--')
                if typeoffit=='both':
                    self.ax.plot(self.freqfit,self.comp['l_'],':')
                    self.ax.plot(self.freqfit,self.comp['g_'],'.')
                elif typeoffit=='gauss':
                    self.ax.plot(self.freqfit,self.comp['g_'],'.')
                elif typeoffit=='SplitLor':
                    self.ax.plot(self.freqfit,self.comp['sl_'],'.')
                elif typeoffit=='DoubleLor':
                    self.ax.plot(self.freqfit,self.comp['l_upper_'],':')
                    self.ax.plot(self.freqfit,self.comp['l_lower_'],'.')
                else:
                    self.ax.plot(self.freqfit,self.comp['l_'],':')
                    
            elif self.varLinearBkg.get()==1 and self.varLogisticBkg.get()==1:
                model=model + StepModel(prefix='step_',form='logistic')+ LinearModel(prefix='line_')
                if typeoffit=='both':
                    params=model.make_params(l_amplitude=amplitude, l_center=center, l_sigma=sigma, g_sigma=0.5*sigma,line_slope=0, line_intercept=0, step_amplitude=0,step_center=center,step_sigma=10e9)
                    params.add(name='total_amplitude', value=amplitude*1.1)
                    params.set(g_amplitude=dict(expr='total_amplitude - l_amplitude', min=0))
                    params.set(g_center=dict(expr='l_center'))
                elif typeoffit=='gauss':
                    params = model.make_params(g_amplitude=amplitude, g_center=center, g_sigma=sigma,line_slope=0, line_intercept=0, step_amplitude=0,step_center=center,step_sigma=10e9)
                elif typeoffit=='SplitLor':
                    params = model.make_params(sl_amplitude=amplitude, sl_center=center, sl_sigma=sigma, sl_sigma_r=sigma,line_slope=0, line_intercept=0, step_amplitude=0,step_center=center,step_sigma=10e9)
                elif typeoffit=='DoubleLor':
                    params = model.make_params(l_upper_amplitude=amplitude,l_upper_center=center,l_upper_sigma=sigma,l_lower_amplitude=amplitude,l_lower_sigma=sigma,line_slope=0,line_intercept=0)
                    params.add(name='peak_split',value=0.3e10)
                    params.set(l_lower_center=dict(expr='l_upper_center - peak_split'))
                else:
                    params = model.make_params(l_amplitude=amplitude, l_center=center, l_sigma=sigma,line_slope=0, line_intercept=0, step_amplitude=0,step_center=center,step_sigma=10e9)

                init = model.eval(params, x=self.nfreq)
                self.resultBkg =model.fit(self.imagfit,params,x=self.freqfit)
                self.comp=self.resultBkg.eval_components()
                self.ax.plot(self.freqfit,self.comp['step_'],'--')
                self.ax.plot(self.freqfit,self.comp['line_'],'o-',markersize=0.5)
                resonancebkg=self.comp['step_']+self.comp['line_']
                if typeoffit=='both':
                    self.ax.plot(self.freqfit,self.comp['l_'],':')
                    self.ax.plot(self.freqfit,self.comp['g_'],'.')
                elif typeoffit=='gauss':
                    self.ax.plot(self.freqfit,self.comp['g_'],'.')
                elif typeoffit=='SplitLor':
                    self.ax.plot(self.freqfit,self.comp['sl_'],'.')
                elif typeoffit=='DoubleLor':
                    self.ax.plot(self.freqfit,self.comp['l_upper_'],':')
                    self.ax.plot(self.freqfit,self.comp['l_lower_'],'.')
                    for pname,par in params.items():
                        print(pname,par)
                else:
                    self.ax.plot(self.freqfit,self.comp['l_'],':')
            
            print(self.resultBkg.fit_report())
            self.status.insert(END, '-------------------------')
            self.status.insert(END, f'AIC {self.resultBkg.aic}')
            self.status.insert(END, f'Chisqr {self.resultBkg.chisqr}')
            self.status.insert(END, f'RedChi {self.resultBkg.redchi}')
            self.status.insert(END, f'Bic {self.resultBkg.bic}')
            self.status.yview(END)
            self.ax.plot(self.freqfit, self.resultBkg.best_fit,'-',label='fit',color=colors(0))
            if typeoffit=='both':
                self.ampl=self.resultBkg.params['l_amplitude'].value+self.resultBkg.params['g_amplitude']#+self.shift
                self.mode=self.resultBkg.params['l_center'].value
                self.sigma=self.resultBkg.params['l_sigma'].value
                self.variance=self.resultBkg.params['l_fwhm'].value
                resonancearray=self.comp['l_']+self.comp['g_']
            elif typeoffit=='gauss':
                self.ampl=self.resultBkg.params['g_amplitude'].value#+self.shift
                self.mode=self.resultBkg.params['g_center'].value
                self.sigma=self.resultBkg.params['g_sigma'].value
                self.variance=self.resultBkg.params['g_fwhm'].value
                resonancearray=self.comp['g_']
            elif typeoffit=='SplitLor':
                self.ampl=self.resultBkg.params['sl_amplitude'].value#+self.shift
                self.mode=self.resultBkg.params['sl_center'].value
                self.sigma=self.resultBkg.params['sl_sigma'].value
                self.sigma_r=self.resultBkg.params['sl_sigma_r'].value
                self.variance=self.resultBkg.params['sl_fwhm'].value
                resonancearray=self.comp['sl_']
            elif typeoffit=='DoubleLor':
                self.amplupper=self.resultBkg.params['l_upper_amplitude'].value#+self.shift
                self.modeupper=self.resultBkg.params['l_upper_center'].value
                self.sigmaupper=self.resultBkg.params['l_upper_sigma'].value
                self.varianceupper=self.resultBkg.params['l_upper_fwhm'].value
                resonancearrayupper=self.comp['l_upper_']
                self.ampllower=self.resultBkg.params['l_lower_amplitude'].value#+self.shift
                self.modelower=self.resultBkg.params['l_lower_center'].value
                self.sigmalower=self.resultBkg.params['l_lower_sigma'].value
                self.variancelower=self.resultBkg.params['l_lower_fwhm'].value
                self.variancelower_delta=self.resultBkg.params['l_lower_fwhm'].stderr
                self.varianceupper_delta=self.resultBkg.params['l_upper_fwhm'].stderr
                resonancearraylower=self.comp['l_lower_']
            else:
                self.ampl=self.resultBkg.params['l_amplitude'].value#+self.shift
                self.mode=self.resultBkg.params['l_center'].value
                self.sigma=self.resultBkg.params['l_sigma'].value
                self.variance=self.resultBkg.params['l_fwhm'].value
                resonancearray=self.comp['l_']
                
            self.maxima=self.freqfit[np.where(self.resultBkg.best_fit==max(self.resultBkg.best_fit))]
            dataout=np.column_stack((self.freqfit, self.resultBkg.best_fit))
            np.savetxt("fit.txt",dataout,delimiter='\t', fmt='%.5e', comments='')            
            self.ax.legend(fontsize='xx-small')
            self.canvas.draw()
            
        else:
            freqspan=self.freq[-1]-self.freq[0]
            peakwith=float(self.entryPwidth.get())
            indexspan=int(round((peakwith/freqspan)*len(self.freq)))
        
            if self.varGauss.get() == 1:
                model=GaussianModel()
            elif self.varDoubleLor.get()==1:
                model=LorentzianModel(prefix='l_lower_')+LorentzianModel(prefix='l_upper_')
                typeoffit='DoubleLor'
            else:
                model=LorentzianModel()

            if dex==0:
                if self.axismin.get() != '0':
                    self.freqfit=self.nfreq[int(round(self.indexmax-indexspan/2)):int(round(self.indexmax+indexspan/2))]
                    self.imagfit=self.nimag[int(round(self.indexmax-indexspan/2)):int(round(self.indexmax+indexspan/2))]
                    self.realfit=self.real[int(round(self.indexmax-indexspan/2)):int(round(self.indexmax+indexspan/2))]
                    params=model.make_params(amplitude=self.nimag[self.indexmax]*self.freqfit[0], center=self.nfreq[self.indexmax], sigma=(self.freqfit[-1]-self.freqfit[0])/2)
                else:
                    self.freqfit=self.nfreq[int(round(self.indexmax-indexspan/2)):int(round(self.indexmax+indexspan/2))]
                    self.imagfit=self.nimag[int(round(self.indexmax-indexspan/2)):int(round(self.indexmax+indexspan/2))]
                    params=model.make_params(amplitude=self.nimag[self.indexmax]*self.freqfit[0], center=self.nfreq[self.indexmax], sigma=(self.freqfit[-1]-self.freqfit[0])/2)

                self.iteratorfwhm=0
            else:
                if self.entrySize.get() !='0':
                    factor=float(self.entrySize.get())
                else:
                    factor=7/8
                
                self.iteratorfwhm +=1    
                if self.axismin.get() !='0':
                    params=model.make_params(amplitude=self.ampl, center=self.mode, sigma=self.sigma)
                    print('iterator ' + str(self.iteratorfwhm))
                    self.freqfit=self.nfreq[(self.indexmax-int(round(indexspan*factor**self.iteratorfwhm/2))):(self.indexmax+int(round(indexspan*factor**self.iteratorfwhm/2)))]
                    self.imagfit=self.nimag[(self.indexmax-int(round(indexspan*factor**self.iteratorfwhm/2))):(self.indexmax+int(round(indexspan*factor**self.iteratorfwhm/2)))]
                    self.realfit=self.real[(self.indexmax-int(round(indexspan*factor**self.iteratorfwhm/2))):(self.indexmax+int(round(indexspan*factor**self.iteratorfwhm/2)))]
                else:
                    params=model.make_params(amplitude=self.ampl, center=self.mode, sigma=self.sigma)
                    print('iterator ' + str(self.iteratorfwhm))
                    self.freqfit=self.nfreq[(self.indexmax-int(round(indexspan*factor**self.iteratorfwhm/2))):(self.indexmax+int(round(indexspan*factor**self.iteratorfwhm/2)))]
                    self.imagfit=self.nimag[(self.indexmax-int(round(indexspan*factor**self.iteratorfwhm/2))):(self.indexmax+int(round(indexspan*factor**self.iteratorfwhm/2)))]

            result=model.fit(self.imagfit, params, x=self.freqfit)
            print(result.fit_report())
            self.ampl=result.params['amplitude'].value#+self.shift
            self.mode=result.params['center'].value
            self.sigma=result.params['sigma'].value
            self.variance=result.params['fwhm'].value
            self.ax.clear()
            self.chi()
            self.ax.plot(self.freqfit, result.best_fit)#+self.shift)
            self.maxima=self.freqfit[np.where(result.best_fit==max(result.best_fit))]
            if self.axismin.get() !='0':
                self.ax.set_xlim(float(self.axismin.get()),float(self.axismax.get()))
                self.ax.set_ylim(min(self.real[np.where((self.freq>round(float(self.axismin.get()))) & (self.freq<round(float(self.axismax.get()))))]),1.5*max(self.imag[np.where((self.freq>round(float(self.axismin.get()))) & (self.freq<round(float(self.axismax.get()))))]))

            self.ax.plot(self.maxima-self.variance/2,(max(result.best_fit)/2),'*',self.maxima+self.variance/2, max(result.best_fit)/2,'*')#tók self.shift
            self.ax.plot(self.maxima,max(result.best_fit),'o')#+self.shift,'o')
            self.ax.legend()


            self.canvas.draw()

    def peak_finder(self):
        self.iterator=1
        texti=pd.read_csv(self.filelist[0], index_col=False, comment= "#", sep='\t', engine='python')
        try:
            selected=self.elements[self.listbox.curselection()[0]]
        except:
            selected='Za'
        
        entryorder=int(self.entryorder.get())
        print(self.filelist[0].split('_')[-1].replace('G.dat',''))

        if self.indicator==0:
            self.plot()
            frequency=texti["freq"].to_numpy(dtype=np.complex).real
            self.freq=frequency
            self.real=texti[selected].to_numpy(dtype=np.complex).real
            self.imag=texti[selected].to_numpy(dtype=np.complex).imag
            
        elif self.indicator==1:
            self.chi()
            self.nfreq=self.freq[np.where(self.freq>0.3e10)]
            self.real=self.chii.real[np.where(self.freq>0.3e10)]
            self.nimag=self.chii.imag[np.where(self.freq>0.3e10)]
        
        if self.axismin.get() !='0':
            self.chi()
            self.imag=self.chii.imag
            self.real=self.chii.real
            self.nimag = self.imag[np.where((self.freq>round(float(self.axismin.get()))) & (self.freq<round(float(self.axismax.get()))))]
            self.nfreq = self.freq[np.where((self.freq>round(float(self.axismin.get()))) & (self.freq<round(float(self.axismax.get()))))]
            #self.ax.set_xlim(float(self.axismin.get()),float(self.axismax.get()))
            #self.ax.set_ylim(min(self.nimag),1.5*max(self.nimag))
            self.peaks_imag = signal.argrelextrema(self.nimag,np.greater,order=entryorder)
            self.ax.plot(self.nfreq[self.peaks_imag],self.nimag[self.peaks_imag], 'o')
            self.indexmax=int(np.where(max(self.nimag[self.peaks_imag])==self.nimag)[0])
            self.ax.plot(self.nfreq[self.indexmax],self.nimag[self.indexmax],'x')
            print(type(self.indexmax))
        else:
            self.peaks_imag = signal.argrelextrema(self.nimag,np.greater,order=entryorder)
            self.ax.plot(self.nfreq[self.peaks_imag],self.nimag[self.peaks_imag],'o')
            self.indexmax=int(np.where(max(self.nimag[self.peaks_imag])==self.nimag)[0])
            self.ax.plot(self.nfreq[self.indexmax],max(self.nimag[self.peaks_imag]),'x') 
            print(type(self.indexmax))
        #self.ax.autoscale(axis='y',tight=True)
        self.canvas.draw()
        #self.peaks_real=np.array(self.peaks_real)
        self.peaks_imag=np.array(self.peaks_imag)
        self.fwhm(0)
        

    def jump_right(self,dex):
        self.ax.clear()
        self.peak_finder()
        if dex==1:
            self.indexmin=self.indexmin+1
        elif dex==0:
            self.indexmax=self.indexmax+1
        self.ax.plot(self.freq[self.peaks_imag[0,self.indexmax]],self.imag[self.peaks_imag[0,self.indexmax]], 'x', markersize=12)
        #self.ax.plot(self.freq[self.minima_imag[0,self.indexmin]],self.imag[self.minima_imag[0,self.indexmin]], 'x')
        self.canvas.draw()
  
    def jump_left(self,dex):
        self.ax.clear()
        self.peak_finder()
        if dex==1:
            self.indexmin=self.indexmin-1
        elif dex==0:
            self.indexmax=self.indexmax-1
        self.ax.plot(self.freq[self.peaks_imag[0,self.indexmax]],self.imag[self.peaks_imag[0,self.indexmax]], 'x', markersize=12)
        #self.ax.plot(self.freq[self.minima_imag[0,self.indexmin]],self.imag[self.minima_imag[0,self.indexmin]], 'x')
        self.canvas.draw()

    def chi(self):        
        try:
            self.ax1.remove()
        except:
            print('No axis 1')
        self.indicator=1
        #parameters to calc chi, susceptibility of film
        wid=float(self.entrywidth.get())*1e-3
        if int(self.circvar.get())==1 and int(self.squarevar.get())==0:
            A=np.pi*(wid/2)**2
        elif int(self.squarevar.get())==1 and int(self.circvar.get())==0:
            A=wid**2
        else:
            print('Choose shape of sample')

        mu=np.pi*4e-7
        t=float(self.entrythick.get())*1e-9
        V=t*A
        w=float(self.entrysampleh.get())*1e-3#width of loop is 4 mm
        W=w**2
        heightloop=1.6e-3 #height of loop is 1.6 mm
        k=2/np.pi*np.arctan(w/heightloop)
        if self.entryGeo.get()=='0':
            psi=0.8
        else:
            psi=float(self.entryGeo.get())

        k_h=k*psi
        selection=self.listboxopen.curselection()
        if len(selection) > 0:
            plotlist = [item for n, item in enumerate(self.filelist) if n in selection]
        else:
            plotlist = self.filelist

        self.ax.clear()
        if self.AngVar.get()==1:
            self.ax.set_xlabel('\u03C9 [rad/s]')
        else:
            self.ax.set_xlabel('f [Hz]')

        self.ax.set_ylabel('\u1d61')
        if self.titlevar.get()==1:
            self.ax.set_title(self.titleentry.get())
        
        if self.axismin.get()!='0':
            minchi=0 #gera ráð fyrir axislimits
            
        for n, item in enumerate(plotlist):
            texti=pd.read_csv(item, index_col=False, comment= "#", sep='\t', engine='python')
            if self.AngVar.get()==1:
                self.freq=texti['freq'].to_numpy(dtype=complex).real*2*np.pi
            else:
                self.freq=texti['freq'].to_numpy(dtype=complex).real
            real=texti['Za'].to_numpy(dtype=complex).real
            imag=texti['Za'].to_numpy(dtype=complex).imag
            try:
                curr=texti['I'].to_numpy(dtype=complex).real
                print(curr)
            except:
                print('No current measured')
                curr=np.empty(1)

            #real=real-Zzero.real
            #imag=imag-Zzero.imag
            self.current=curr
            if self.AngVar.get()==1:
                chi=imag*W/(k_h*mu*V*self.freq*4*np.pi)
                chii=real*W/(k_h*mu*V*self.freq*4*np.pi)    #deili með 4 pi til þess að fá í cgs
            else:
                chi=imag*W/(k_h*mu*V*self.freq*8*np.pi**2)
                chii=real*W/(k_h*mu*V*self.freq*8*np.pi**2)

            if self.shiftvar.get()==1:
                self.chii=chi+n*int(self.shiftentry.get())+1j*(chii+n*int(self.shiftentry.get()))
                            
            else:
                self.chii=chi+1j*chii
            
            #if self.axismin.get() !='0':

                #if min(self.chii.real[np.where(np.where((self.freq>round(float(self.axismin.get()))) & (self.freq<round(float(self.axismax.get())))))])<minchi:
                 #   minchi= min(self.chii.real[np.where(np.where((self.freq>round(float(self.axismin.get()))) & (self.freq<round(float(self.axismax.get())))))])
            if len(curr)!=1:
                re='Re(\u1d61) '+item.split('/')[-1]+' '+ str(np.nanmean(curr))
                im='Im(\u1d61) '+item.split('/')[-1]+' '+ str(np.nanmean(curr))
            else:
                re='Re(\u1d61) '+item.split('/')[-1]
                im='Im(\u1d61) '+item.split('/')[-1]

            if self.Re.get()==1:
                self.ax.plot(self.freq,self.chii.real,label=re)
            elif self.Im.get()==1:
                self.ax.plot(self.freq,self.chii.imag,label=im)
            else:
                self.ax.plot(self.freq,self.chii.real,label=re)
                self.ax.plot(self.freq,self.chii.imag,label=im)
            
                        
            if self.custvar.get()==1:
                self.legendliststr=[]
                for i in range(0,self.n):
                    for n in range(0,1):
                        if self.Im.get()==1:
                            self.legendliststr.append(self.legendlist[i].get().split('.dat')[0].replace('_',' ').replace(' batch','')+' Im(\u1d61)')
                        else:
                            self.legendliststr.append(self.legendlist[i].get().split('.dat')[0].replace('_',' ').replace(' batch','')+' Re(\u1d61)')
                            self.legendliststr.append(self.legendlist[i].get().split('.dat')[0].replace('_',' ').replace(' batch','')+' Im(\u1d61)')

                self.ax.legend(self.legendliststr)
            else:
                self.ax.legend()#legend)
        if self.axismin.get() !='0':
            self.ax.set_xlim(float(self.axismin.get()),float(self.axismax.get()))
            #self.ax.autoscale(axis='y',tight=False)
            #print(max(chi[np.where((self.freq>round(float(self.axismin.get()))) & (self.freq<round(float(self.axismax.get()))))]))# & self.freq<round(float(self.axismax.get()))))
            self.ax.set_ylim(minchi,1.5*max(chii[np.where((self.freq>round(float(self.axismin.get()))) & (self.freq<round(float(self.axismax.get()))))]))
        self.canvas.draw()
        filename = "chi_gogn2.txt"
        intro=f'''#FMR data from {datetime.datetime.now()} freq\u1d61_r\u1d61_i'''
        #fmt=['%.5e', '%.5e %+.5ej', '%.5e %+.5ej', '%.5e %+.5ej', '%.5e %+.5ej', '%.5e %+.5ej', '%.5e %+.5ej', '%.5e %+.5ej', '%.5e %+.5ej', '%.5e %+.5ej']
        fmt='%.5e'
        dataout=np.column_stack((self.freq, chi, chii))
        np.savetxt(filename, dataout, delimiter='\t', header=intro, fmt=fmt, comments='')

    def accept(self):
        self.acceptindicator=True
        self.fit_chi()

    def fit_chi(self):
        start=self.mode-1*self.variance
        end=(self.mode+1*self.variance)
        if self.entryLower.get()!='0':
            start=float(self.entryLower.get())
            end=float(self.entrySuperior.get())
     
        gamma=float(self.entryGamma.get())
        gammaMin=float(self.entryGaMin.get())
        gammaMax=float(self.entryGaMax.get())
        M=float(self.entryMs.get())
        MMin=float(self.entryMsMin.get())
        MMax=float(self.entryMsMax.get())
        K_u=float(self.entryKu.get())
        K_uMin=float(self.entryKuMin.get())
        K_uMax=float(self.entryKuMax.get())
        K_c=float(self.entryKc.get())
        K_cMin=float(self.entryKcMin.get())
        K_cMax=float(self.entryKcMax.get())
        thickness=float(self.entrythick.get())*1e-9
        t=float(self.entryT.get())*1e-9
        tMin=float(self.entryTMin.get())*1e-9
        tMax=float(self.entryTMax.get())*1e-9
        #K_s=float(self.entryKs.get())
        #K_sMin=float(self.entryKsMin.get())
        #K_sMax=float(self.entryKsMax.get())
        H=float(self.filelist[0].split('_')[-1].split('.')[0])
        alpha=float(self.entryAlpha.get())
        alphavalueMin=float(self.entryAlMin.get())
        alphavalueMax=float(self.entryAlMax.get())
        d=float(self.entrythick.get())*1e-9
        geo=float(self.entryGeo.get())
        #Dx=H+(4*np.pi+2*K_u/(M**2)+4*K_s/(d*M**2))*M
        #Dy=2*H+(4*np.pi+4*K_u/(M**2)+4*K_s/(d*M**2))*M

        def fcn2min(params, x, y):
            alpha=params['alpha']
            if MMin!=MMax:
                M=params['M']
            else:
                M=float(self.entryMs.get())
            if K_uMin!=K_uMax:
                K_u=params['Ku']
            else:
                K_u=float(self.entryKu.get())
            if gammaMin!=gammaMax:
                gamma=params['gamma']
            else:
                gamma=float(self.entryGamma.get())
            if self.entryGeoMin.get()!=self.entryGeoMax.get():
                geo1=params['geo']
                y=y*geo/geo1
            if self.chitype.get()==1:
                K_c=params['Kc']
            else:
                K_c=0
            K_s=0
            if tMax!=tMin:
                t=params['t']
                y=y*thickness/t
                
            chi_num=gamma**2*M*(H+(4*np.pi+2*(K_u+K_c)/(M**2)+4*K_s/(d*M**2))*M)+1j*x*alpha*gamma*M
            omegarpow2=gamma**2*(H+(4*np.pi+2*(K_u+K_c)/(M**2)+4*K_s/(d*M**2))*M)*(H+2*(K_u+K_c)/M)
            chi_den=omegarpow2-x**2*(1+alpha**2)+1j*x*gamma*alpha*(2*H+(4*np.pi+4*(K_u+K_c)/(M**2)+4*K_s/(d*M**2))*M)
            chi=chi_num/chi_den
            resids=(y-chi.imag)**2#+(y.real-chi.real)**2
            return resids#.view(float)

        params=Parameters()
        if gammaMin!=gammaMax:
            params.add('gamma',value=gamma,min=gammaMin,max=gammaMax)

        if self.entryGeoMin.get()!=self.entryGeoMax.get():
            params.add('geo',value=geo,min=float(self.entryGeoMin.get()),max=float(self.entryGeoMax.get()))

        if alphavalueMin!=alphavalueMax:
            params.add('alpha',value=alpha,min=alphavalueMin,max=alphavalueMax)
                         
        #if K_sMin!=K_sMax:
        #    params.add('Ks',value=K_s,min=K_sMin,max=K_sMax)

        if tMin!=tMax:
            params.add('t',value=t,min=tMin,max=tMax)
            
        if MMin!=MMax:
            params.add('M',value=M,min=MMin,max=MMax)

        if K_uMin!=K_uMax:
            params.add('Ku',value=K_u,min=K_uMin,max=K_uMax)
        if K_cMin!=K_cMax:
            params.add('Kc',value=K_c,min=K_cMin,max=K_cMax)

        self.freqfit=self.freq[np.where((self.freq>start) & (self.freq<end))]
        self.imagfit=self.chii[np.where((self.freq>start) & (self.freq<end))]
        self.comp=self.resultBkg.eval_components(x=self.freqfit)
        if self.varLinearBkg.get()==1 and self.varLogisticBkg.get()==0:    
            y=self.imagfit-self.comp['line_']
        elif self.varLinearBkg.get()==0 and self.varLogisticBkg.get()==1:
            y=self.imagfit-self.comp['step_']
        elif self.varLinearBkg.get()==1 and self.varLogisticBkg.get()==1:
            y=self.imagfit-self.comp['step_']-self.comp['line_']           

        if self.varGauss.get()==1 and self.varLor.get()==1:
            yfit=self.comp['l_']+self.comp['g_']
        elif self.varGauss.get()==1 and self.varLor.get()==0:
            yfit=self.comp['g_']
        elif self.varSplitLor.get()==1:
            model=LorentzianModel()
            amplitude=self.ampl*2*self.sigma/(self.sigma+self.sigma_r)
            paramsLorentzian = model.make_params(amplitude=amplitude, center=self.mode, sigma=self.sigma)
            yfit=model.eval(paramsLorentzian, x=self.freqfit)
        elif self.varDoubleLor.get()==1:
            yfit=self.comp['l_upper_']
        else:
            yfit=self.comp['l_']
            
        minner = Minimizer(fcn2min, params, fcn_args=(self.freqfit, yfit))
        if self.varLeastsq.get()==1:
            metho='leastsq'
        else:
            metho='shgo'
        self.result = minner.minimize(method=metho)
        
        report_fit(self.result)
        self.alpha_delta=self.result.params['alpha'].stderr
        if tMin!=tMax:
            self.t_delta=self.result.params['t'].stderr
            self.t_alpha_corr=self.result.params['alpha'].correl['t']
        
        if alphavalueMin!=alphavalueMax:
            alpha=self.result.params['alpha'].value
            self.entryAlpha.delete(0,"end")
            self.entryAlpha.insert(0,self.result.params['alpha'].value)

        if MMin!=MMax:
            M=self.result.params['M'].value
            self.entryMs.delete(0,"end")
            self.entryMs.insert(0,self.result.params['M'].value)

        #if K_sMin!=K_sMax:
        #    K_s=self.result.params['Ks'].value
        #    self.entryKs.delete(0,"end")
        #    self.entryKs.insert(0,self.result.params['Ks'].value)

        if K_uMin!=K_uMax:
            K_u=self.result.params['Ku'].value
            self.entryKu.delete(0,"end")
            self.entryKu.insert(0,self.result.params['Ku'].value)

        if gammaMin!=gammaMax:
            gamma=self.result.params['gamma'].value
            self.entryGamma.delete(0,"end")
            self.entryGamma.insert(0,self.result.params['gamma'].value)

        if K_cMin!=K_cMax and self.chitype.get()==1:
            K_c=self.result.params['Kc'].value
            self.entryKc.delete(0,"end")
            self.entryKc.insert(0,self.result.params['Kc'].value)
        else:
            K_c=0

        if tMin!=tMax:
            t=self.result.params['t'].value
            self.entryT.delete(0,"end")
            self.entryT.insert(0,self.result.params['t'].value*1e9)
            
        if self.entryGeoMin.get()!=self.entryGeoMax.get():
            geo2=self.result.params['geo'].value
            self.entryGeo.delete(0,"end")
            self.entryGeo.insert(0,self.result.params['geo'].value)
        
        K_s=0

        freq=self.freq
        chi_num=gamma**2*M*(H+(4*np.pi+2*(K_u+K_c)/(M**2)+4*K_s/(d*M**2))*M)+1j*freq*alpha*gamma*M
        omegarpow2=gamma**2*(H+(4*np.pi+2*(K_u+K_c)/(M**2)+4*K_s/(d*M**2))*M)*(H+2*(K_u+K_c)/M)
        chi_den=omegarpow2-freq**2*(1+alpha**2)+1j*freq*gamma*alpha*(2*H+(4*np.pi+4*(K_u+K_c)/(M**2)+4*K_s/(d*M**2))*M)
        chi=chi_num/chi_den
        self.ax.clear()
        if self.titlevar.get()==1:
            self.ax.set_title(self.titleentry.get())

        if tMin!=tMax:
            self.ax.plot(self.freq, self.chii.real*thickness/t, label='$Re(\u1d61)$')  #+min(self.chii.imag[100:-1])
            self.ax.plot(self.freq, self.chii.imag*thickness/t, label='$Im(\u1d61)$',color=colors(0))   #-min(self.chii.imag[100:-1])
            self.entrythick.delete(0,"end")
            self.entrythick.insert(0,t*1e9)
        elif self.entryGeoMin.get()!=self.entryGeoMax.get():
            self.ax.plot(self.freq, self.chii.real*geo/geo2, label='$Re(\u1d61)$')  #+min(self.chii.imag[100:-1])
            self.ax.plot(self.freq, self.chii.imag*geo/geo2, label='$Im(\u1d61)$',color=colors(0))
        else:
            self.ax.plot(self.freq, self.chii.real, label='$Re(\u1d61)$')  #+min(self.chii.imag[100:-1])
            self.ax.plot(self.freq, self.chii.imag, label='$Im(\u1d61)$')   #-min(self.chii.imag[100:-1])
            
        self.ax.plot(freq,chi.real,label="$Re(\u1d61)$ fit")
        self.ax.plot(freq,chi.imag,label="$Im(\u1d61)$ fit",color=colors(2))      
        self.ax.plot(self.freq[np.abs(self.freq-start).argmin()],self.chii.imag[np.abs(self.freq-start).argmin()],'+')
        self.ax.plot(self.freq[np.abs(self.freq-end).argmin()],self.chii.imag[np.abs(self.freq-end).argmin()],'+')
        self.ax.plot(self.freqfit,yfit,'--',color=colors(4))
        self.ax.set_ylim(min(chi.real),max(chi.imag)*1.3)
        #self.ax.plot(freq,self.chii.imag-chi.imag,label='res')
        #self.ax.plot(freq,self.chii.real-chi.real,label='res-real')
        #if self.varBackgr.get()==1:
            #self.ax.plot(self.freq, self.freq**3*a+self.freq**2*b+self.freq*c+d)
            #self.ax.plot(self.freq,np.polyval(self.polyvallinfit,self.freq))
            #self.ax.plot(freqlin,chiilin, '*',label='imaglin')
        #indexid=np.where(chi.real==max(chi.real))
        #print(self.freq[np.where(self.freq==freqmax)])
        #self.ax.plot(self.freq[np.where(self.freq==freqmax)],self.chii.real[np.where(self.freq==freqmax)],'^')
        #self.ax.plot(self.freq[np.where(self.freq==freqmin)],self.chii.real[np.where(self.freq==freqmin)],'^')
        self.ax.set_xlabel('\u03C9 [rad/s]')
        self.ax.set_ylabel('\u1d61')
        #self.ax.plot(omegarpow2,max(chi.imag),'*')
        self.ax.legend()
        self.acceptindicator=False
        filename = "G:/My Drive/Vinna/Analysis/FMR/chi_fit.txt"
        intro=f'''#FMR data from {datetime.datetime.now()} freq\u1d61_r\u1d61_i'''
        fmt='%.5e'
        dataout=np.column_stack((freq, chi.real, chi.imag))
# =============================================================================
#         np.savetxt(filename, dataout, delimiter='\t', header=intro, fmt=fmt, comments='')
# =============================================================================
        self.canvas.draw()  
        
    def _quit(self):
        app.quit()
        app.destroy()
    def file_open(self):
        t=tk.filedialog.askopenfilenames(initialdir='/home/fmrdata/Data',filetypes=(('dat files', '*.dat'),('txt files', '*.txt'),('all files','*.*')))
        self.filelist.extend(list(t))
        self.listboxopen.delete(0,self.listboxopen.size())

        for i in range(len(self.filelist)):
            self.listboxopen.insert(i, self.filelist[i].split('/')[-1])

        #remove .dat files from the list to plot

    def listbox_delete(self):
        END = self.listboxopen.size()
        self.removelist = self.listboxopen.curselection()
        self.filelist = [item for n, item in enumerate(self.filelist) if n not in self.removelist]
        self.listboxopen.delete(0,END)
        for i in range(len(self.filelist)):
            self.listboxopen.insert(i, self.filelist[i].split('/')[-1])

        #plot the all the .dat files but only the selected item in the self.listbox, which corresponds the the S11 measurement

    def reArrangeListbox(self, direction):
        items=list(self.listboxopen.curselection())
        if not items:
            print("Nothing")
            return
        if direction == "up":
            for pos in items:
                if pos == 0:
                    continue
                text=self.listboxopen.get(pos)
                fileName = self.filelist[pos]
                self.filelist.pop(pos)
                self.listboxopen.delete(pos)
                self.filelist.insert(pos-1, fileName)
                self.listboxopen.insert(pos-1, text)
            self.listboxopen.selection_clear(0,self.listboxopen.size())
            self.listboxopen.selection_set(tuple([i-1 for i in items]))

        if direction == "dn":
            for pos in items:
                if pos ==self.listboxopen.size():
                    continue
                text=self.listboxopen.get(pos)
                fileName = self.filelist[pos]
                self.listboxopen.delete(pos)
                self.filelist.pop(pos)
                self.filelist.insert(pos+1, fileName)
                self.listboxopen.insert(pos+1, text)
            self.listboxopen.selection_clear(0,self.listboxopen.size())
            self.listboxopen.selection_set(tuple([i+1 for i in items]))
        else:
            return

    def import_fit(self):
            file=tk.filedialog.askopenfilename(initialdir='/home/fmrdata/Data')
            texti=pd.read_csv(file, index_col=False, comment= "#", sep='\t', engine='python')
            self.imported_values=texti['Value'].to_numpy()
            self.imported_min=texti['min'].to_numpy()
            self.imported_max=texti['max'].to_numpy()
            self.entryGamma.delete(0, END)
            self.entryGamma.insert(0,str(self.imported_values[0]))
            i=0
            for F in (self.entryGamma, self.entryAlpha, self.entryKu, self.entryMs, self.entryShift):
                F.delete(0, END)
                F.insert(0,str(self.imported_values[i]))
                i+=1
            i=0
            for F in (self.entryGaMin, self.entryAlMin, self.entryKuMin, self.entryMsMin, self.entryShiftMin):
                F.delete(0, END)
                F.insert(0,str(self.imported_min[i]))
                i+=1
            i=0
            for F in (self.entryGaMax, self.entryAlMax, self.entryKuMax, self.entryMsMax, self.entryShiftMax):
                F.delete(0, END)
                F.insert(0,str(self.imported_max[i]))
                i+=1
                
    def save_fit(self):
        filename = tk.filedialog.asksaveasfilename(initialdir='/home/fmrdata/Data', defaultextension="*.txt")
        skjal=open(filename,'w')
        skjal.write('Variable\tValue\tmin\tmax\n')
        skjal.write(f'Gamma\t{self.entryGamma.get()}\t{self.entryGaMin.get()}\t{self.entryGaMax.get()}\n')
        skjal.write(f'Alpha\t{self.entryAlpha.get()}\t{self.entryAlMin.get()}\t{self.entryAlMax.get()}\n')
        skjal.write(f'Ku\t{self.entryKu.get()}\t{self.entryKuMin.get()}\t{self.entryKuMax.get()}\n')
        #skjal.write(f'Ks\t{self.entryKs.get()}\t{self.entryKsMin.get()}\t{self.entryKsMax.get()}\n')
        skjal.write(f'Ms\t{self.entryMs.get()}\t{self.entryMsMin.get()}\t{self.entryMsMax.get()}\n')
        skjal.write(f'shift\t{self.entryShift.get()}\t{self.entryShiftMin.get()}\t{self.entryShiftMax.get()}')
        skjal.close()


    def fitchiframe(self):
        if self.fitchivar.get()==1:
            self.rowconfigure(20, weight=5)
            self.custframe=tk.Frame(self)
            self.custframe.grid(row=19, column=15, columnspan=3, rowspan=12, sticky='nsew')

            tk.Button(self.custframe, text='Save fit', command=self.save_fit).grid(row=0, column=1)
            tk.Button(self.custframe, text='Import fit', command=self.import_fit,width=6).grid(row=0,column=0) 
            tk.Button(self.custframe, text="Fit chi", command=self.fit_chi, width=6).grid(row=1, column=1)
            tk.Label(self.custframe,text='Min').grid(row=1,column=2)
            tk.Label(self.custframe,text='Max').grid(row=1,column=3)
            tk.Label(self.custframe,text="\u03b3").grid(row=2,column=0)
            self.entryGamma=tk.Entry(self.custframe,width=10)
            self.entryGamma.insert(0,'0')
            self.entryGamma.grid(row=2, column=1)
            
            tk.Checkbutton(self.custframe, text='Uni+Cubic', variable=self.chitype).grid(row=0,column=2)

            self.entryGaMin=tk.Entry(self.custframe,width=10)
            self.entryGaMin.insert(0,'0')
            self.entryGaMin.grid(row=2,column=2)
            self.entryGaMax=tk.Entry(self.custframe,width=10)
            self.entryGaMax.insert(0,'0')
            self.entryGaMax.grid(row=2,column=3)
            
            tk.Label(self.custframe,text="\u03b1").grid(row=3,column=0)
            self.entryAlpha=tk.Entry(self.custframe,width=10)
            self.entryAlpha.insert(0, '0')
            self.entryAlpha.grid(row=3,column=1)

            self.entryAlMin=tk.Entry(self.custframe,width=10)
            self.entryAlMin.insert(0,'0')
            self.entryAlMin.grid(row=3,column=2)
            self.entryAlMax=tk.Entry(self.custframe,width=10)
            self.entryAlMax.insert(0,'0')
            self.entryAlMax.grid(row=3,column=3)
            
            tk.Label(self.custframe,text="K\u0075 [erg/cm³]").grid(row=4,column=0)
            self.entryKu=tk.Entry(self.custframe,width=10)
            self.entryKu.insert(0,'0')
            self.entryKu.grid(row=4,column=1)

            self.entryKuMin=tk.Entry(self.custframe,width=10)
            self.entryKuMin.insert(0,'0')
            self.entryKuMin.grid(row=4,column=2)
            self.entryKuMax=tk.Entry(self.custframe,width=10)
            self.entryKuMax.insert(0,'0')
            self.entryKuMax.grid(row=4,column=3)
            
            #tk.Label(self.custframe,text='K\u0073').grid(row=5,column=0)
            #self.entryKs=tk.Entry(self.custframe,width=10)
           # self.entryKs.insert(0,'0')
           # self.entryKs.grid(row=5,column=1)

            #self.entryKsMin=tk.Entry(self.custframe,width=10)
            #self.entryKsMin.insert(0,'0')
            #self.entryKsMin.grid(row=5,column=2)
            #self.entryKsMax=tk.Entry(self.custframe,width=10)
            #self.entryKsMax.insert(0,'0')
            #self.entryKsMax.grid(row=5,column=3)

            tk.Label(self.custframe,text='Kc [emu/cm^3]').grid(row=5,column=0)
            self.entryKc=tk.Entry(self.custframe,width=10)
            self.entryKc.insert(0,'0')
            self.entryKc.grid(row=5,column=1)
            self.entryKcMin=tk.Entry(self.custframe,width=10)
            self.entryKcMin.insert(0,'0')
            self.entryKcMin.grid(row=5,column=2)
            self.entryKcMax=tk.Entry(self.custframe,width=10)
            self.entryKcMax.insert(0,'0')
            self.entryKcMax.grid(row=5,column=3)


            tk.Label(self.custframe,text='M\u0073 [emu/cm^3]').grid(row=6,column=0)
            self.entryMs=tk.Entry(self.custframe,width=10)
            self.entryMs.insert(0,'0')
            self.entryMs.grid(row=6,column=1)
            self.entryMsMin=tk.Entry(self.custframe,width=10)
            self.entryMsMin.insert(0,'0')
            self.entryMsMin.grid(row=6,column=2)
            self.entryMsMax=tk.Entry(self.custframe,width=10)
            self.entryMsMax.insert(0,'0')
            self.entryMsMax.grid(row=6,column=3)

            tk.Label(self.custframe,text='Shift (\u03c1)').grid(row=7,column=0)
            self.entryShift=tk.Entry(self.custframe,width=10)
            self.entryShift.insert(0,'0')
            self.entryShift.grid(row=7,column=1)
            self.entryShiftMin=tk.Entry(self.custframe,width=10)
            self.entryShiftMin.insert(0,'0')
            self.entryShiftMin.grid(row=7,column=2)
            self.entryShiftMax=tk.Entry(self.custframe,width=10)
            self.entryShiftMax.insert(0,'0')
            self.entryShiftMax.grid(row=7,column=3)

            tk.Label(self.custframe,text='Shift (\u03A8)').grid(row=8,column=0)
            self.entryPsi=tk.Entry(self.custframe,width=10)
            self.entryPsi.insert(0,'0')
            self.entryPsi.grid(row=8,column=1)
            self.entryPsiMin=tk.Entry(self.custframe,width=10)
            self.entryPsiMin.insert(0,'0')
            self.entryPsiMin.grid(row=8,column=2)
            self.entryPsiMax=tk.Entry(self.custframe,width=10)
            self.entryPsiMax.insert(0,'0')
            self.entryPsiMax.grid(row=8,column=3)
            tk.Label(self.custframe,text='Thickness [nm]').grid(row=9,column=0)
            self.entryT=tk.Entry(self.custframe,width=10)
            self.entryT.insert(0,'0')
            self.entryT.grid(row=9,column=1)
            self.entryTMin=tk.Entry(self.custframe,width=10)
            self.entryTMin.insert(0,'0')
            self.entryTMin.grid(row=9,column=2)
            self.entryTMax=tk.Entry(self.custframe,width=10)
            self.entryTMax.insert(0,'0')
            self.entryTMax.grid(row=9,column=3)
            tk.Label(self.custframe,text='Geo. \u03A8').grid(row=10,column=0)
            self.entryGeo=tk.Entry(self.custframe,width=10)
            self.entryGeo.insert(0,'0')
            self.entryGeo.grid(row=10,column=1)
            self.entryGeoMin=tk.Entry(self.custframe,width=10)
            self.entryGeoMin.insert(0,'0')
            self.entryGeoMin.grid(row=10,column=2)
            self.entryGeoMax=tk.Entry(self.custframe,width=10)
            self.entryGeoMax.insert(0,'0')
            self.entryGeoMax.grid(row=10,column=3)
            
            
            self.varLinearBkg,self.varLogisticBkg,self.varQuadBkg=tk.IntVar(self),tk.IntVar(self),tk.IntVar(self)
            self.varLinearBkg.set(1)
            self.varLogisticBkg.set(0)
            self.varQuadBkg.set(0)

            self.QuadBkg=tk.Checkbutton(self.custframe,text='Quadratic',variable=self.varQuadBkg).grid(row=13,column=1)
            self.LinearBkg=tk.Checkbutton(self.custframe,text='Linear', variable=self.varLinearBkg).grid(row=13,column=2)
            self.LogisticBkg=tk.Checkbutton(self.custframe,text='Logistic',variable=self.varLogisticBkg).grid(row=13,column=3)


            #tk.Label(self.custframe,text='\u03C6'+'u').grid(row=7,column=0)
            #self.entryPhu=tk.Entry(self.custframe,width=10)
            #self.entryPhu.insert(0,'0')
            #self.entryPhu.grid(row=7,column=1)
            #self.entryPhuMin=tk.Entry(self.custframe,width=10)
            #self.entryPhuMin.insert(0,'0')
            #self.entryPhuMin.grid(row=7,column=2)
            #self.entryPhuMax=tk.Entry(self.custframe,width=10)
            #self.entryPhuMax.insert(0,'0')
            #self.entryPhuMax.grid(row=7,column=3)
            tk.Button(self.custframe, text='Export report', command=self.exportPdf).grid(row=11,column=0)

            self.varLeastsq, self.varShgo=tk.IntVar(self), tk.IntVar(self)
            self.Leastsq=tk.Checkbutton(self.custframe, text="Leastsq", variable=self.varLeastsq,command=lambda: self.set_checkfit(2)).grid(row=11, column=1)
            self.Shgo=tk.Checkbutton(self.custframe, text="Shgo", variable=self.varShgo,command=lambda: self.set_checkfit(3)).grid(row=11,column=2)
            self.varLeastsq.set(1)
            self.varBackgr=tk.IntVar(self)
            self.Backgr=tk.Checkbutton(self.custframe, text="Backgr", variable=self.varBackgr).grid(row=11,column=3)
            self.varBackgr.set(1)
            tk.Button(self.custframe, text='Resize', command=self.fit_chi).grid(row=12,column=0)
            self.entryLower=tk.Entry(self.custframe,width=5)
            self.entryLower.insert(0,'0')
            self.entryLower.grid(row=12,column=1)
            self.entrySuperior=tk.Entry(self.custframe,width=5)
            self.entrySuperior.insert(0,'0')
            self.entrySuperior.grid(row=12, column=2)
            tk.Button(self.custframe, text='Accept', command=self.accept).grid(row=12,column=3)
            self.acceptindicator=False
            self.status=tk.Listbox(self, width=20, height=9, bg='#E0E0E0', bd=2)
            self.status.grid(row=21, column=10, rowspan=5, columnspan=4)

            for i in np.arange(0,12):
                self.custframe.rowconfigure(i, weight=1)
        else:
            self.custframe.destroy()
    
    def plot(self):
        try:
            selected=self.elements[self.listbox.curselection()[0]]
            self.selectedlast=selected
        except:
            selected=self.selectedlast

        selection=self.listboxopen.curselection()
        if len(selection) > 0:
            plotlist = [item for n, item in enumerate(self.filelist) if n in selection]
        else:
            plotlist = self.filelist

        self.indexmax=0
        self.indicator=0
        self.ax.clear()
        #self.ax.remove()
        if self.titlevar.get()==1:
            self.ax.set_title(self.titleentry.get())
        if self.custvar.get()==1:
            self.legendliststr=[]
            for i in range(0,self.n):
                for n in range(0,1):
                    self.legendliststr.append(self.legendlist[i].get().split('.dat')[0].replace('_',' ').replace(' batch','')+' Re(\u1d61)')
                    self.legendliststr.append(self.legendlist[i].get().split('.dat')[0].replace('_',' ').replace(' batch','')+' Im(\u1d61)')

            self.ax.legend(self.legendliststr)

        self.ax.set_xlabel('$f$ [Hz]')
        self.ax.set_ylabel(selected +' [\u03A9]')
        for item in plotlist:
            texti=pd.read_csv(item, index_col=False, comment= "#", sep='\t', engine='python')
            if selected == 'angle':
                field=np.loadtxt(item,usecols=[0], dtype='str', skiprows=1, delimiter='\t')
                resonance=np.loadtxt(item, usecols=[2], skiprows=1, delimiter='\t')
                try:
                    current=np.loadtxt(item, usecols=[5], skiprows=1, delimiter='\t')
                    current_indicator=True
                except:
                    current_indicator=False
                angle=np.array([float(i.split('_')[-1].split('G')[0]) for i in field])
                H=float(field[0].split('_')[-2].split('G')[0])
                print(angle)

                self.ax.clear()
                self.ax.set_xlabel('\u03B8 [°]')
                self.ax.set_ylabel('$\u03C9_r  [rad/s]$')
                if current_indicator:
                    self.ax1=self.ax.twinx()
                    self.ax.plot(angle,resonance,'*')
                    #self.ax1.plot(angle,abs(current),'ro')
                    print(myos)
                    
                    if myos=='Darwin':
                        curr_results=np.loadtxt('/Users/asgeirtryggvason/Library/CloudStorage/GoogleDrive-asgeir13@gmail.com/My Drive/Vinna/Kodi/Calibration files/calib_curr_results_Ls.dat')
                    elif myos=='Windows':
                        curr_results=np.loadtxt('G:/My Drive/Vinna/Kodi/Calibration files/calib_curr_results_Ls.dat')
                    print(curr_results)
                    self.ax1.plot(angle,abs(current*curr_results[0]+curr_results[1]),'ro')
                    self.ax1.set_ylabel('I EA [A]')
                else:
                    self.ax.plot(angle,resonance,'*')

                if self.fitchivar.get()==1:
                    try:
                        M=float(self.entryMs.get())
                        Ku=float(self.entryKu.get())
                        gamma=float(self.entryGamma.get())
                        Ks=0
                        d=float(self.entrythick.get())*10**-9
                        angles=np.arange(angle[0],angle[-1],1)
                        res=-1*gamma*np.sqrt((H+4*np.pi*M-2*Ku*np.cos(angles*np.pi/180)**2+4*Ks/(d*M))*(H-2*Ku*np.cos(2*angles*np.pi/180)/M))
                        self.ax.plot(angles,res)
                    except:
                        print('Check fit parameters')


            elif selected== 'polar':
                self.ax.remove()
                self.ax=plt.subplot(projection='polar')
                field=np.loadtxt(plotlist[0],usecols=[0], dtype='str', skiprows=1, delimiter='\t')
                resonance=np.loadtxt(plotlist[0], usecols=[2], skiprows=1, delimiter='\t')
                field=np.array([float(i.split('_')[-1].split('G')[0]) for i in field])
                self.ax.plot(field*np.pi/180,resonance/max(resonance),'*')
                self.ax.grid(True)
                self.ax.set_ylim(bottom=min(resonance/max(resonance)))

            elif selected=='4-fold':
                try:
                    self.ax1.remove()
                except:
                    print('No axis 1')
                self.ax.set_xlabel('\u03B8 [rad]')
                self.ax.set_ylabel('$\u03C9_r [rad/s]$')
                field=np.loadtxt(plotlist[0],usecols=[0],dtype='str',skiprows=1, delimiter='\t')
                resonance=np.loadtxt(plotlist[0],usecols=[2], skiprows=1, delimiter='\t')
                angle=np.array([float(i.split('_')[-1].split('G')[0]) for i in field])
                angle=angle*np.pi/180
                M=float(self.entryMs.get())
                H=float(plotlist[0].split('_')[-2].split('G')[0])
                gamma=float(self.entryGamma.get())
                #ddEth=H*M*np.sin(th)*np.cos(ph-phh)+k1(2*np.cos(2*th)**2-1+np.sin(2*ph)**2*np.sin(th)**2*(4*np.cos(th)**2-1))+(2*np.cos(th)**2-1)*(2*ku*np.sin(ph-phh)**2-4*np.pi*M**2)
                #ddEph=M*H*np.sin(th)*np.cos(ph-phh)+k1*(2*np.cos(2*ph)**2-1)*np.sin(th)**4+4*ku*np.sin(th)**2*(2*np.cos(ph-phh)**2-1)
                #ddEthph=M*H*np.cos(th)*np.sin(ph-phh)+4*k1*np.sin(2*ph)*np.cos(2*ph)*np.sin(th)**3*np.cos(th)+4*ku*np.sin(th)*np.cos(th)*np.sin(ph-phu)*np.cos(ph-phu)
                
                def fcn2min(params,ph,y):
                    ku=params['ku']
                    k1=params['k1']
                    th=np.pi/2
                    phh=ph
                    phu=params['phu']
                    ddEth=H*M*np.sin(th)*np.cos(ph-phh)+k1*(2*np.cos(2*th)**2-1+np.sin(2*ph)**2*np.sin(th)**2*(4*np.cos(th)**2-1))+(2*np.cos(th)**2-1)*(2*ku*np.sin(ph-phh)**2-4*np.pi*M**2)
                    ddEph=M*H*np.sin(th)*np.cos(ph-phh)+k1*(2*np.cos(2*ph)**2-1)*np.sin(th)**4+4*ku*np.sin(th)**2*(2*np.cos(ph-phu)**2-1)
                    ddEthph=M*H*np.cos(th)*np.sin(ph-phh)+4*k1*np.sin(2*ph)*np.cos(2*ph)*np.sin(th)**3*np.cos(th)+4*ku*np.sin(th)*np.cos(th)*np.sin(ph-phu)*np.cos(ph-phu)
                    Y=(M**2*np.sin(th)**2)**-1*(ddEth*ddEph-ddEthph**2)
                    resids = (Y-y)**2
                    return resids
                
                params=Parameters()
                if float(self.entryKuMin.get())!=0:
                    params.add('ku', value=float(self.entryKu.get()),min=float(self.entryPhuMin.get()),max=float(self.entryPhuMax.get()))
                else:
                    params.add('ku', value=float(self.entryKu.get()))
                if float(self.entryK1Min.get())!=0:
                    params.add('k1',value=float(self.entryK1.get()),min=float(self.entryK1Min.get()),max=float(self.entryK1Max.get()))
                else:
                    params.add('k1',value=float(self.entryK1.get()))
                if float(self.entryPhuMin.get())!=0:
                    params.add('phu',value=float(self.entryPhu.get()),min=float(self.entryPhuMin.get()),max=float(self.entryPhuMax.get()))
                else:
                    params.add('phu',value=float(self.entryPhu.get()))

                minner =Minimizer(fcn2min,params, fcn_args=(angle, (resonance/gamma)**2))
                result=minner.minimize()
                report_fit(result)
                ph=np.arange(min(angle),max(angle),np.pi/360)
                phh=ph
                k1=result.params['k1'].value
                ku=result.params['ku'].value
                th=np.pi/2
                phu=result.params['phu'].value
                ddEth=H*M*np.sin(th)*np.cos(ph-phh)+k1*(2*np.cos(2*th)**2-1+np.sin(2*ph)**2*np.sin(th)**2*(4*np.cos(th)**2-1))+(2*np.cos(th)**2-1)*(2*ku*np.sin(ph-phh)**2-4*np.pi*M**2)
                ddEph=M*H*np.sin(th)*np.cos(ph-phh)+k1*(2*np.cos(2*ph)**2-1)*np.sin(th)**4+4*ku*np.sin(th)**2*(2*np.cos(ph-phu)**2-1)
                ddEthph=M*H*np.cos(th)*np.sin(ph-phh)+4*k1*np.sin(2*ph)*np.cos(2*ph)*np.sin(th)**3*np.cos(th)+4*ku*np.sin(th)*np.cos(th)*np.sin(ph-phu)*np.cos(ph-phu)
                Y=(M**2*np.sin(th)**2)**-1*(ddEth*ddEph-ddEthph**2)
                self.ax.plot(ph,Y)
                self.ax.plot(angle,(resonance/gamma)**2,'*')
                self.entryKu.delete(0,"end")
                self.entryKu.insert(0,result.params['ku'].value)
                self.entryK1.delete(0,"end")
                self.entryK1.insert(0,result.params['k1'].value)
                self.entryPhu.delete(0,"end")
                self.entryPhu.insert(0,result.params['phu'].value)

            elif selected == 'Ku':
                try:
                    self.ax1.remove()
                except:
                    print('No axis 1')
                field=np.loadtxt(plotlist[0],usecols=[0], dtype='str', skiprows=1, delimiter='\t')
                resonance=np.loadtxt(plotlist[0], usecols=[2], skiprows=1, delimiter='\t')
                angle=np.array([float(i.split('_')[-1].split('G')[0]) for i in field])
                angle=angle*np.pi/180
                M=float(self.entryMs.get())
                H=float(plotlist[0].split('_')[-2].split('G')[0])
                gamma=float(self.entryGamma.get())
                print(H)
                K_s=0
                d=float(self.entrythick.get())*1e-9

                def fcn2min(params, x, y):
                    ku=params['ku']
                    shift=params['shift']
                    gamma=params['gamma']
                    Y=gamma**2*(H+4*np.pi*M+(2*ku/M)*np.cos(x+shift)**2+4*K_s/(d*M))*(H+(2*ku/M)*np.cos(2*(x+shift)))
                    resids = (Y-y)**2

                    return resids
                params = Parameters()
                if float(self.entryKu.get())!=0:
                    params.add('ku', value=float(self.entryKu.get()))
                else:
                    params.add('ku', value=4000)
                if float(self.entryKuMax.get())!=0:
                    params.add('ku', value=float(self.entryKu.get()), min=float(self.entryKuMin.get()), max=float(self.entryKuMax.get()))
                params.add('shift', value=float(self.entryShift.get()))
                if float(self.entryShiftMin.get())!=0:
                    params.add('shift', value=float(self.entryShift.get()),min=float(self.entryShiftMin.get()),max=float(self.entryShiftMax.get()))
                
                params.add('gamma', value=float(self.entryGamma.get()))
                if float(self.entryGaMax.get())!=0:
                    params.add('gamma', value=float(self.entryGamma.get()),min=float(self.entryGaMin.get()),max=float(self.entryGaMax.get()))
                

                minner = Minimizer(fcn2min, params, fcn_args = (angle,resonance**2))
                result = minner.minimize()
                report_fit(result)
                
                self.ax.clear()
                self.ax.set_xlabel('$\u03B8 [rad]$')
                self.ax.set_ylabel('($\u03C9/\u0263$)^2 [Oe$^2$]')
                self.ax.plot(angle, (resonance/gamma)**2,'*')
                angles=np.arange(min(angle),max(angle),np.pi/500) 
                Y=(H+4*np.pi*M+(2*result.params['ku']/M)*np.cos(angles+result.params['shift'].value)**2+4*K_s/(d*M))*(H+2*result.params['ku']*np.cos(2*(angles+result.params['shift'].value))/M)
                self.ax.plot(angles, Y)
                self.entryKu.delete(0,"end")
                self.entryKu.insert(0,result.params['ku'].value)
                self.entryShift.delete(0,"end")
                self.entryShift.insert(0, result.params['shift'].value)
            
            elif selected == 'EA-Ku':
                try:
                    self.ax1.remove()
                except:
                    print('No axis 1')
                print(plotlist)
                if plotlist[0].find('angle')==-1:
                    EA_x=np.loadtxt(plotlist[0],usecols=[0], dtype='str', skiprows=1, delimiter='\t')
                    EA_resonance=np.loadtxt(plotlist[0], usecols=[2], skiprows=1, delimiter='\t')
                    EA_x=np.array([float(i.split('_')[-1].split('G')[0]) for i in EA_x])
                    Angle_x=np.loadtxt(plotlist[1],usecols=[0], dtype='str', skiprows=1, delimiter='\t')
                    Angle_resonance=np.loadtxt(plotlist[1], usecols=[2], skiprows=1, delimiter='\t')
                    Angle_x=np.array([float(i.split('_')[-1].split('G')[0]) for i in Angle_x])*np.pi/180
                    H=float(plotlist[1].split('_')[-2].split('G')[0])
                else:
                    EA_x=np.loadtxt(plotlist[1],usecols=[0], dtype='str', skiprows=1, delimiter='\t')
                    EA_resonance=np.loadtxt(plotlist[1], usecols=[2], skiprows=1, delimiter='\t')
                    EA_x=np.array([float(i.split('_')[-1].split('G')[0]) for i in EA_x])
                    Angle_x=np.loadtxt(plotlist[0],usecols=[0], dtype='str', skiprows=1, delimiter='\t')
                    Angle_resonance=np.loadtxt(plotlist[0], usecols=[2], skiprows=1, delimiter='\t')
                    Angle_x=np.array([float(i.split('_')[-1].split('G')[0]) for i in Angle_x])*np.pi/180
                    H=float(plotlist[0].split('_')[-2].split('G')[0])

                M=float(self.entryMs.get())
                gamma=float(self.entryGamma.get())

                def fcn2min(params, EA_x, EA_y, Angle_x, Angle_y):
                    ku=params['Ku']
                    shift=params['Shift']
                    gamma=params['Gamma']
                    #M=params['M']
                    Angle_Y=gamma**2*(H+4*np.pi*M+(2*ku/M)*np.cos(Angle_x+shift)**2)*(H+(2*ku/M)*np.cos(2*(Angle_x+shift)))
                    EA_Y=gamma**2*(EA_x+4*np.pi*M+2*(ku)/M)*(EA_x+2*(ku)/M)

                    resids =np.concatenate(((Angle_Y-Angle_y)**2, 8*(EA_Y-EA_y)**2))
                    #  resids=resids.flatten()
                    return resids
                
                params = Parameters()
                params.add('Ku', value=float(self.entryKu.get()), min=float(self.entryKuMin.get()), max=float(self.entryKuMax.get()))
                params.add('Shift', value=float(self.entryShift.get()))
                params.add('Gamma', value=float(self.entryGamma.get()),min=float(self.entryGaMin.get()),max=float(self.entryGaMax.get()))
                #params.add('M', value=float(self.entryMs.get()),min=float(self.entryMsMin.get()),max=float(self.entryMsMax.get()))

                minner = Minimizer(fcn2min, params, fcn_args = (EA_x,EA_resonance**2,Angle_x,Angle_resonance**2))
                result = minner.minimize()
                report_fit(result)
                self.entryShift.delete(0,"end")
                self.entryShift.insert(0, result.params['Shift'].value)
                self.entryGamma.delete(0, 'end')
                self.entryGamma.insert(0, result.params['Gamma'].value)
                self.entryKu.delete(0, 'end')
                self.entryKu.insert(0,result.params['Ku'].value)
                #self.entryMs.delete(0,'end')
                #self.entryMs.insert(0,result.params['M'].value)

                self.ax.plot(EA_x,EA_resonance**2,'*')
                self.ax.plot(EA_x, result.params['Gamma']**2*(EA_x+4*np.pi*M+2*result.params['Ku']/M)*(EA_x+2*result.params['Ku']/M))


                self.ax.set_xlabel('H [Oe]')
                self.ax.set_ylabel('$\u03C9^2 [rad^2/s^2]$')


            elif selected == 'Cubic Koh (100)':
                try:
                    self.ax1.remove()
                except:
                    print('No axis 1')
                field=np.loadtxt(plotlist[0],usecols=[0], dtype='str', skiprows=1, delimiter='\t')
                resonance=np.loadtxt(plotlist[0], usecols=[2], skiprows=1, delimiter='\t')
                field=np.array([float(i.split('_')[-1].split('G')[0]) for i in field])
                angle=field*np.pi/180
                
                M=float(self.entryMs.get())
                H=float(plotlist[0].split('_')[-2].split('G')[0])
                gamma=float(self.entryGamma.get())
                
                def fcn2min(params, phi, y):
                    Ku=params['Ku']
                    shift=params['shift']
                    a=H+2*(Ku/M)*np.cos(4*(phi+shift))
                    b=H+4*np.pi*M+(Ku/(2*M))*(3+np.cos(4*(phi+shift)))
                    #(K2/(2*M))*np.sin(2*(phi+shift))**2
              
                    Y=a*b
                    resids = (Y-y)**2

                    return resids
                params = Parameters()
                if float(self.entryKu.get())!=0:
                    params.add('Ku', value=float(self.entryKu.get()))
                else:
                    params.add('Ku', value=4000)
                params.add('shift', value=float(self.entryShift.get()))

                if float(self.entryShiftMin.get())!=0:
                    params.add('shift', value=float(self.entryShift.get()),min=float(self.entryShiftMin.get()),max=float(self.entryShiftMax.get()))
                if float(self.entryKuMin.get())!=0:
                    params.add('Ku', value=float(self.entryKu.get()), min=float(self.entryKuMin.get()), max=float(self.entryKuMax.get()))
                    
                minner = Minimizer(fcn2min, params, fcn_args = (angle,(resonance/gamma)**2))
                result = minner.minimize()
                report_fit(result)
                
                self.ax.clear()
                self.ax.set_xlabel('$\u03B8 [rad]$')
                self.ax.set_ylabel('($\u03C9/\u0263$)^2')
                self.ax.plot(angle, (resonance/gamma)**2,'*')
                phi=np.arange(min(angle),max(angle),np.pi/500)
                shift=result.params['shift'].value
                Ku=result.params['Ku'].value
                a=H+2*(Ku/M)*np.cos(4*(phi+shift))
                b=H+4*np.pi*M+(Ku/(2*M))*(3+np.cos(4*(phi+shift)))
                Y=a*b
                self.ax.plot(phi, Y)
                self.entryShift.delete(0,"end")
                self.entryShift.insert(0, result.params['shift'].value)
                self.entryKu.delete(0,"end")
                self.entryKu.insert(0,result.params['Ku'].value)
            

            elif selected == 'Cubic Koh (100)+uni':
                try:
                    self.ax1.remove()
                except:
                    print('No axis 1')
                field=np.loadtxt(plotlist[0],usecols=[0], dtype='str', skiprows=1, delimiter='\t')
                resonance=np.loadtxt(plotlist[0], usecols=[2], skiprows=1, delimiter='\t')
                field=np.array([float(i.split('_')[-1].split('G')[0]) for i in field])
                angle=field*np.pi/180
                
                M=float(self.entryMs.get())
                H=float(plotlist[0].split('_')[-2].split('G')[0])
                gamma=float(self.entryGamma.get())
                
                def fcn2min(params, phi, y):
                    Kc=params['Kc']
                    #K2=params['K2']
                    Ku=params['Ku']
                    rho=params['rho']
                    psi=params['psi']
                    a=H+2*(Kc/M)*np.cos(4*phi+psi)+2*(Ku/M)*np.cos(2*phi+rho)
                    b=H+4*np.pi*M+(Kc/(2*M))*(3+np.cos(4*phi+psi))+2*(Ku/M)*np.cos(phi+rho)**2
                    #(K2/(2*M))*np.sin(2*(phi+shift))**2
              
                    Y=a*b
                    resids = (Y-y)**2

                    return resids
                params = Parameters()
                if float(self.entryKc.get())!=0:
                    params.add('Kc', value=float(self.entryKc.get()))
                else:
                    params.add('Kc', value=4000)
                
                params.add('psi',value=float(self.entryPsi.get()))
                params.add('rho', value=float(self.entryShift.get()))
                if float(self.entryKu.get())!=0:
                    params.add('Ku', value=float(self.entryKu.get()))
                else:
                    params.add('Ku',value=4000)

                if float(self.entryShiftMin.get())!=0:
                    params.add('rho', value=float(self.entryShift.get()),min=float(self.entryShiftMin.get()),max=float(self.entryShiftMax.get()))
                if float(self.entryPsiMin.get())!=0:
                    params.add('psi', value=float(self.entryPsi.get()),min=float(self.entryPsiMin.get()),max=float(self.entryPsiMax.get()))
                if float(self.entryKcMin.get())!=0:
                    params.add('Kc', value=float(self.entryKc.get()), min=float(self.entryKcMin.get()), max=float(self.entryKcMax.get()))
                if float(self.entryKuMin.get())!=0:
                    params.add('Ku', value=float(self.entryKu.get()), min=float(self.entryKuMin.get()), max=float(self.entryKuMax.get()))
                    
                minner = Minimizer(fcn2min, params, fcn_args = (angle,(resonance/gamma)**2))
                result = minner.minimize()
                report_fit(result)
                
                self.ax.clear()
                self.ax.set_xlabel('$\u03B8 [rad]$')
                self.ax.set_ylabel('($\u03C9/\u0263$)^2')
                self.ax.plot(angle, (resonance/gamma)**2,'*')
                phi=np.arange(min(angle),max(angle),np.pi/500)
                rho=result.params['rho'].value
                psi=result.params['psi'].value
                Kc=result.params['Kc'].value
                Ku=result.params['Ku'].value
                a=H+2*(Kc/M)*np.cos(4*phi+psi)+2*(Ku/M)*np.cos(2*phi+rho)
                b=H+4*np.pi*M+(Kc/(2*M))*(3+np.cos(4*phi+psi))+2*(Ku/M)*np.cos(phi+rho)**2
                Y=a*b
                self.ax.plot(phi, Y)
                self.entryKu.delete(0,"end")
                self.entryKu.insert(0,result.params['Ku'].value)
                self.entryShift.delete(0,"end")
                self.entryShift.insert(0, result.params['rho'].value)
                self.entryKc.delete(0,"end")
                self.entryKc.insert(0,result.params['Kc'].value)
                self.entryPsi.delete(0,"end")
                self.entryPsi.insert(0,result.params['psi'].value)
            

            elif selected == 'Cubic Koh (110)':
                try:
                    self.ax1.remove()
                except:
                    print('No axis 1')
                field=np.loadtxt(plotlist[0],usecols=[0], dtype='str', skiprows=1, delimiter='\t')
                resonance=np.loadtxt(plotlist[0], usecols=[2], skiprows=1, delimiter='\t')
                field=np.array([float(i.split('_')[-1].split('G')[0]) for i in field])
                angle=field*np.pi/180
                
                M=float(self.entryMs.get())
                H=float(plotlist[0].split('_')[-2].split('G')[0])
                gamma=float(self.entryGamma.get())
                
                def fcn2min(params, phi, y):
                    K1=params['K1']
                    K2=params['K2']
                    shift=params['shift']
                    a=H+(K1/(2*M))*(np.cos(2*(phi+shift))+3*np.cos(4*(phi+shift)))+(K2/(8*M))*np.sin(phi+shift)**2*(9*np.cos(4*(phi+shift))+10*np.cos(2*(phi+shift))+5)
                    b=H+4*np.pi*M+(K1/(8*M))*(3*np.cos(4*(phi+shift))+16*np.cos(2*(phi+shift))-3)-(K2/(8*M))*np.sin(2*(phi+shift))**2*(2+3*np.sin(phi+shift)**2)
                    
                    Y=a*b
                    resids = (Y-y)**2

                    return resids
                params = Parameters()
                if float(self.entryK1.get())!=0:
                    params.add('K1', value=float(self.entryK1.get()))
                else:
                    params.add('K1', value=4000)
                params.add('shift', value=float(self.entryShift.get()))
                if float(self.entryKs.get())!=0:
                    params.add('K2', value=float(self.entryKs.get()))
                else:
                    params.add('K2',value=4000)

                if float(self.entryShiftMin.get())!=0:
                    params.add('shift', value=float(self.entryShift.get()),min=float(self.entryShiftMin.get()),max=float(self.entryShiftMax.get()))
                if float(self.entryK1Min.get())!=0:
                    params.add('K1', value=float(self.entryKu.get()), min=float(self.entryKuMin.get()), max=float(self.entryKuMax.get()))
                if float(self.entryKsMin.get())!=0:
                    params.add('K2', value=float(self.entryKs.get()), min=float(self.entryKsMin.get()), max=float(self.entryKsMax.get()))
                    
                minner = Minimizer(fcn2min, params, fcn_args = (angle,(resonance/gamma)**2))
                result = minner.minimize()
                report_fit(result)
                
                self.ax.clear()
                self.ax.set_xlabel('$\u03B8 [rad]$')
                self.ax.set_ylabel('($\u03C9/\u0263$)^2')
                self.ax.plot(angle, (resonance/gamma)**2,'*')
                phi=np.arange(min(angle),max(angle),np.pi/500)
                #alpha=result.params['alpha'].value
                K1=result.params['K1'].value
                K2=result.params['K2'].value
                shift=result.params['shift'].value
                a=H+(K1/(2*M))*(np.cos(2*(phi+shift))+3*np.cos(4*(phi+shift)))+(K2/(8*M))*np.sin(phi+shift)**2*(9*np.cos(4*(phi+shift))+10*np.cos(2*(phi+shift))+5)
                b=H+4*np.pi*M+(K1/(8*M))*(3*np.cos(4*(phi+shift))+16*np.cos(2*(phi+shift))-3)-(K2/(8*M))*np.sin(2*(phi+shift))**2*(2+3*np.sin(phi+shift)**2)
 
                Y=a*b
                self.ax.plot(phi, Y)
                self.entryKu.delete(0,"end")
                self.entryKu.insert(0,result.params['K1'].value)
                self.entryShift.delete(0,"end")
                self.entryShift.insert(0, result.params['shift'].value)
                self.entryKs.delete(0,"end")
                self.entryKs.insert(0,result.params['K2'].value)
                
            elif selected == 'Oblique':
                try:
                    self.ax1.remove()
                except:
                    print('No axis 1')
                field=np.loadtxt(plotlist[0],usecols=[0], dtype='str', skiprows=1, delimiter='\t')
                resonance=np.loadtxt(plotlist[0], usecols=[2], skiprows=1, delimiter='\t')
                field=np.array([float(i.split('_')[-1].split('G')[0]) for i in field])
                angle=field*np.pi/180
                
                M=float(self.entryMs.get())
                H=float(plotlist[0].split('_')[-2].split('G')[0])
                gamma=float(self.entryGamma.get())
                def fcn2min(params, phi, y):
                    Ku1=params['Ku1']
                    Ku2=params['Ku2']
                    alpha=params['alpha']
                    a=H+2*Ku1/M*np.sin(alpha)**2*np.cos(2*phi)+4*(Ku2/M)*(np.cos(2*phi)+(4*np.sin(phi)**2-1)*np.cos(phi)**2*np.sin(alpha)**2)*np.sin(alpha)**2
                    b=H+4*np.pi*M-(2*Ku1/M)*(np.cos(2*alpha)+np.sin(alpha)**2*np.sin(phi)**2)+4*(Ku2/M)*(np.cos(phi)**2*np.sin(alpha)**2*(2*np.cos(alpha)**2-np.cos(phi)**2*np.sin(alpha)**2)+np.cos(phi)**2*np.sin(alpha)**2*(np.cos(alpha)**2+1)-np.cos(alpha)**2)
                    Y=a*b
                    resids = (Y-y)**2

                    return resids
                params = Parameters()
                if float(self.entryKu.get())!=0:
                    params.add('Ku1', value=float(self.entryKu.get()))
                else:
                    params.add('Ku1', value=4000)
                params.add('alpha', value=float(self.entryShift.get()))
                if float(self.entryKs.get())!=0:
                    params.add('Ku2', value=float(self.entryKs.get()))
                else:
                    params.add('Ku2',value=4000)

                if float(self.entryShiftMin.get())!=0:
                    params.add('alpha', value=float(self.entryShift.get()),min=float(self.entryShiftMin.get()),max=float(self.entryShiftMax.get()))
                if float(self.entryKuMin.get())!=0:
                    params.add('Ku1', value=float(self.entryKu.get()), min=float(self.entryKuMin.get()), max=float(self.entryKuMax.get()))
                if float(self.entryKsMin.get())!=0:
                    params.add('Ku2', value=float(self.entryKs.get()), min=float(self.entryKsMin.get()), max=float(self.entryKsMax.get()))
                    
                minner = Minimizer(fcn2min, params, fcn_args = (angle,(resonance/gamma)**2))
                result = minner.minimize()
                report_fit(result)
                
                self.ax.clear()
                self.ax.set_xlabel('$\u03B8 [rad]$')
                self.ax.set_ylabel('($\u03C9/\u0263$)^2')
                self.ax.plot(angle, (resonance/gamma)**2,'*')
                phi=np.arange(min(angle),max(angle),np.pi/500)
                alpha=result.params['alpha'].value
                Ku1=result.params['Ku1'].value
                Ku2=result.params['Ku2'].value
                a=H+2*Ku1/M*np.sin(alpha)**2*np.cos(2*phi)+4*(Ku2/M)*(np.cos(2*phi)+(4*np.sin(phi)**2-1)*np.cos(phi)**2*np.sin(alpha)**2)*np.sin(alpha)**2
                b=H+4*np.pi*M-(2*Ku1/M)*(np.cos(2*alpha)+np.sin(alpha)**2*np.sin(phi)**2)+4*(Ku2/M)*(np.cos(phi)**2*np.sin(alpha)**2*(2*np.cos(alpha)**2-np.cos(phi)**2*np.sin(alpha)**2)+np.cos(phi)**2*np.sin(alpha)**2*(np.cos(alpha)**2+1)-np.cos(alpha)**2)
                Y=a*b
                self.ax.plot(phi, Y)
                self.entryKu.delete(0,"end")
                self.entryKu.insert(0,result.params['Ku1'].value)
                self.entryShift.delete(0,"end")
                self.entryShift.insert(0, result.params['alpha'].value)
                self.entryKs.delete(0,"end")
                self.entryKs.insert(0,result.params['Ku2'].value)

            elif selected == 'Ku_comment':
                field=np.loadtxt(plotlist[0],usecols=[0], dtype='str', skiprows=1, delimiter='\t')
                resonance=np.loadtxt(plotlist[0], usecols=[2], skiprows=1, delimiter='\t')
                field=np.array([float(i.split('_')[-1].split('G')[0]) for i in field])
                x=np.cos(field*np.pi/180)

                def fcn2min(params, x, y):
                    a=params['a']
                    b=params['b']
                    c=params['c']

                    Y=a*x**2+b*x+c
                    resids = (Y-y)**2

                    return resids
                params = Parameters()
                params.add('a',value=-7E18)
                params.add('b',value=1E19)
                params.add('c',value=2E18)
                minner = Minimizer(fcn2min, params, fcn_args = (x**2, resonance**2))
                result = minner.minimize()
                report_fit(result)
                self.ax.clear()
                self.ax.set_xlabel('cos($ \u03B8$ )^2')
                self.ax.set_ylabel('$\u03C9 ^2 [rad^2/s^2]$')
                self.ax.plot(x**2, resonance**2,'*')
                self.ax.plot(x**2, result.params['a']*x**4+result.params['b']*x**2+result.params['c'],'X')

                M=float(self.entryMs.get())
                H=float(plotlist[0].split('_')[-2].split('G')[0])
                gamma=float(self.entryGamma.get())
                print(H)
                K_s=0
                d=float(self.entrythick.get())*1e-9
                a=result.params['a']
                b=result.params['b']
                c=result.params['c']
                r=4/(M**2)
                s=-6*H/M-16*np.pi-8*np.pi*(a+b)/c-2*(H/M)*((a+b)/c)-16*K_s/(d*M**2)-8*K_s*(a+b)/(d*c*M**2)
                t=(-H**2-4*np.pi*M*H-4*K_s*H/(d*M))*(a+b)/c
                deltaabc=(result.params['a'].stderr+result.params['b'].stderr)/abs(c)+result.params['c'].stderr/abs(c)*abs((a+b)/c)
                deltas=abs(8*np.pi+2*H/M+8*K_s*H/(d*M))*deltaabc
                deltat=abs(4*K_s*H/(d*M))*deltaabc

                try:
                    x=(-s+np.sqrt(s**2-4*r*t))/(2*r)
                    print(f'x er {x} erg/cm^3')
                except:
                    print('x er ekki lausn')

                try:    
                    x1=(-s-np.sqrt(s**2-4*r*t))/(2*r)
                    deltax1=abs(1/2*r+2*s/(4*r*np.sqrt(s**2-4*r*t)))*deltas+abs(1/np.sqrt(s**2-4*r*t))*deltat
                    print(f'x1 er {x1} erg/cm^3')
                    #x1=np.sqrt(M**2/(8*gamma**2))
                    print(f'x1 er {np.sqrt(M**2/(8*gamma**2))}')
                except:
                    print('x1 er ekki lausn')

                self.entryKu.delete(0,"end")
                self.entryKu.insert(0,abs(x1))
                self.entryKuMin.delete(0,"end")
                self.entryKuMax.delete(0,"end")
                self.entryKuMax.insert(0,abs(x1)+deltax1)
                self.entryKuMin.insert(0,abs(x1)-deltax1)

            elif selected == 'EA_comment':
                field=np.loadtxt(plotlist[0],usecols=[0], dtype='str', skiprows=1, delimiter='\t')
                resonance=np.loadtxt(plotlist[0], usecols=[2], skiprows=1, delimiter='\t')
                field=np.array([float(i.split('_')[-1].split('G')[0]) for i in field])
                H=field
                M=float(self.entryMs.get())
                Ku=float(self.entryKu.get())
                b=4*np.pi*M+4*Ku/M
                c=(4*np.pi*M+2*Ku/M)*(2*Ku/M)
                x=H**2+H*b+c
                x=(H+4*np.pi*M+2*Ku/M)*(H+2*Ku/M)

                self.ax.plot(x,resonance**2,'*')

                def fcn2min(params, x, y):
                    a=params['a']
                    b=params['b']

                    Y=a*x+b
                    resids = (Y-y)**2

                    return resids

                params = Parameters()
                params.add('a',value=1e14)
                params.add('b',value=1e19)

                minner=Minimizer(fcn2min, params, fcn_args = (x, resonance**2))
                result = minner.minimize()
                report_fit(result)
                self.ax.plot(x, result.params['a']*x+result.params['b'], 'X')

                self.entryGamma.delete(0, 'end')
                self.entryGamma.insert(0, -np.sqrt(result.params['a']))
                self.entryGaMax.delete(0, "end")
                self.entryGaMin.delete(0,"end")
                self.entryGaMax.insert(0,-np.sqrt(result.params['a']+result.params['a'].stderr/(2*abs(np.sqrt(result.params['a'])))))
                self.entryGaMin.insert(0,-np.sqrt(result.params['a']-result.params['a'].stderr/(2*abs(np.sqrt(result.params['a'])))))

            elif selected == 'EA':
                try:
                    self.ax1.remove()
                except:
                    print('No axis 1')
                field=np.loadtxt(plotlist[0],usecols=[0], dtype='str', skiprows=1, delimiter='\t')
                resonance=np.loadtxt(plotlist[0], usecols=[2], skiprows=1, delimiter='\t')
                field=np.array([float(i.split('_')[-1].split('G')[0]) for i in field])
                H=field
                M=float(self.entryMs.get())
                Ku=float(self.entryKu.get())
                Kc=float(self.entryKc.get())
                x=(H+4*np.pi*M+2*Ku/M)*(H+2*Ku/M)

                self.ax.plot(H,resonance**2,'*')

                def fcn2min(params, x, y):
                    Ku=params['Ku']
                    Gamma=params['Gamma']
                    try:
                        M=params['M']
                    except:
                        print('M is a fixed variable')
                        M=float(self.entryMs.get())

                    Y=Gamma**2*(x+4*np.pi*M+2*(Ku+Kc)/M)*(x+2*(Ku+Kc)/M)
                    resids = (Y-y)**2

                    return resids

                params = Parameters()
                if self.entryKu.get()=="0":
                    params.add('Ku',value=5000)
                else:
                    params.add('Ku',value=float(self.entryKu.get()),min=float(self.entryKuMin.get()), max=float(self.entryKuMax.get()))
                if self.entryGamma.get()=="0":
                    params.add('Gamma',value=-1.7e7)
                else:
                    params.add('Gamma',value=float(self.entryGamma.get()))
                if self.chitype.get()==1 and self.entryKc.get()!="0":
                    params.add('Kc', value=float(self.entryKc.get()),min=float(self.entryKcMin.get()),max=float(self.entryKcMax.get()))
                elif self.chitype.get()==1:
                    params.add('Kc', value=2000)
                if float(self.entryMsMin.get())!=float(self.entryMsMax.get()):
                    params.add('M', value=float(self.entryMs.get()),min=float(self.entryMsMin.get()),max=float(self.entryMsMax.get()))
                    M_fitting=1
                else:
                    M_fitting=0

                minner=Minimizer(fcn2min, params, fcn_args = (H, resonance**2))
                result = minner.minimize()
                report_fit(result)
                if self.chitype.get()==1 & M_fitting==0:
                    self.ax.plot(H, result.params['Gamma']**2*(H+4*np.pi*M+2*(result.params['Ku']+result.params['Kc'])/M)*(H+2*(result.params['Ku']+result.params['Kc'])/M))
                elif self.chitype.get()==1 & M_fitting==1:
                    self.ax.plot(H, result.params['Gamma']**2*(H+4*np.pi*result.params['M']+2*(result.params['Ku']+result.params['Kc'])/result.params['M'])*(H+2*(result.params['Ku']+result.params['Kc'])/result.params['M']))
                elif M_fitting==0:
                    self.ax.plot(H, result.params['Gamma']**2*(H+4*np.pi*M+2*result.params['Ku']/M)*(H+2*result.params['Ku']/M))
                else:
                    self.ax.plot(H, result.params['Gamma']**2*(H+4*np.pi*result.params['M']+2*result.params['Ku']/result.params['M'])*(H+2*result.params['Ku']/result.params['M']))

                self.ax.set_xlabel('H [Oe]')
                self.ax.set_ylabel('$\u03C9^2 [rad^2/s^2]$')

                
                self.entryGamma.delete(0, 'end')
                self.entryGamma.insert(0, result.params['Gamma'].value)
                self.entryGaMax.delete(0, "end")
                self.entryGaMin.delete(0,"end")
                try:
                    self.entryGaMax.insert(0,result.params['Gamma']+result.params['Gamma'].stderr/(2*abs(result.params['Gamma'])))
                    self.entryGaMin.insert(0,result.params['Gamma']-result.params['Gamma'].stderr/(2*abs(result.params['Gamma'])))
                except:
                    print("Gamma errorbars can't be evaluated")
                self.entryKu.delete(0, 'end')
                self.entryKu.insert(0,result.params['Ku'].value)
                if self.chitype.get()==1:
                    self.entryKc.delete(0,'end')
                    self.entryKc.insert(0,result.params['Kc'].value)

            else:
                try:
                    self.ax1.remove()
                except:
                    print('No ax1 axis defined')
                print(selected)
                x=texti['freq'].to_numpy(dtype=complex).real
                y=texti[selected].to_numpy(dtype=complex).real
                y1=texti[selected].to_numpy(dtype=complex).imag
                self.ax.plot(x,y,x,y1)
            
        legend=[item.split('/')[-1] for item in plotlist]
        self.ax.legend(legend)
        if self.axismin.get() !='0':
            self.ax.set_xlim(float(self.axismin.get()),float(self.axismax.get()))
        self.canvas.draw()

    def exportPdf(self):
        imagefilename=tk.filedialog.askopenfilename()
        canvas=Canvas(imagefilename.split(".png")[0]+'.pdf')
        #canvas.drawString(72, 72, codecs.encode(self.reportstring))
        print(self.result.params['alpha'].value)
        canvas.drawString(72,130, 'Parameter   Value   Stderr')
        canvas.drawString(20, 825, f'{datetime.datetime.now()}')
        i=0
        for name, param in self.result.params.items():
            canvas.drawString(72, 120-i, f'{name}    {self.result.params[name].value}    {self.result.params[name].stderr}')
            i+=15
        
        canvas.drawImage(imagefilename,0,132,width=600,preserveAspectRatio=True)
        canvas.save()
        #pdf=PdfPages(imagefilename.split('/')self.titleenty.get()+'.pdf')
        #pdf.savefig()

    def title(self):
        if self.titlevar.get()==1:
            self.titleentry=tk.Entry(self.editframe, width=18)
            self.titleentry.grid(row=5,column=12,sticky='s')
        else:
            try:
                self.titleentry.destroy()
            except:
                print('no title entry')

    def shift(self):
        if self.shiftvar.get()==1:
            self.shiftentry=tk.Entry(self.editframe, width=5)
            self.shiftentry.grid(row=6,column=12)
        else:
            try:
                self.shiftentry.destroy()
            except:
                print('no shift entry')
    def custom(self):
        
        if self.custvar.get()==1:
            print('reyna')
            try:
                self.n=len(self.listboxopen.curselection())
            except:
                self.n=0
            
            setpoints=[self.titlevar.get(),self.custvar.get(),self.shiftvar.get()]
            try:
                shiftentry=self.shiftentry.get()
            except:
                print('')

            try:
                titleentry=self.titleentry.get()
            except:
                print('')
            self.editframe.destroy()
            self.editframe=tk.Frame(self)
            self.editframe.grid(row=5,column=11,columnspan=2,rowspan=4+9,sticky='wn')
            self.titlevar=tk.IntVar()
            self.titlevar.set(setpoints[0])
            tk.Checkbutton(self.editframe, text='Title', variable=self.titlevar, command=self.title).grid(row=5,column=11,sticky='w')
            self.custvar=tk.IntVar()
            self.custvar.set(setpoints[1])
            tk.Checkbutton(self.editframe, text='Legend', variable=self.custvar, command=self.custom).grid(row=7,column=11,sticky='nw')
            self.shiftvar=tk.IntVar()
            self.shiftvar.set(setpoints[2])
            tk.Checkbutton(self.editframe, text='Shift', variable=self.shiftvar, command=self.shift).grid(row=6,column=11,sticky='w')
            self.title()
            self.shift()
            try:
                self.titleentry.insert(0,titleentry)
            except:
                print('')
            try:
                self.shiftentry.insert(0,shiftentry)
            except:
                print('')
            self.customframe=tk.Frame(self.editframe)
            self.customframe.grid(row=7,column=12, columnspan=1,rowspan=9,sticky='nes')
            for i in range(0,8+self.n):
                self.customframe.rowconfigure(i,weight=1)
            self.legendlist=[]
            for i in range(0, self.n):
                print(self.n)
                
                entr = tk.Entry(self.customframe, width=18)
                entr.grid(row=i,column=0)
                entr.insert(0,self.filelist[self.listboxopen.curselection()[i]].split("/")[-1].split('.dat')[0].replace('_',' ').replace(' batch',''))
                self.legendlist.append(entr)
                #self.customframe.rowconfigure(i,weight=1)
            print(self.legendlist)
            for i in range(0,8+self.n):
                self.customframe.rowconfigure(i,weight=1)
        else:
            self.customframe.destroy()
fontconf='aria 10 bold'
# class popup(tk.Toplevel):
#     def __init__(self, master, **kwargs):
#         tk.Toplevel.__init__(self, master, **kwargs)
#         #win=tk.Toplevel.frame()
#         self.geometry('400x300')
#         self.focus()
#         self.lift()
#         #self.focus_set()
#         self.grab_set()
#         self.titlevar=tk.IntVar()
#         self.titlevar.set(0)
#         tk.Checkbutton(self, text='Title', variable=self.titlevar, command=self.title).grid(row=0,column=0)
#         self.custvar=tk.IntVar()
#         self.custvar.set(0)
#         tk.Checkbutton(self, text='Legend', variable=self.custvar, command=self.custom).grid(row=1,column=0)
#         tk.Button(self, text='Apply', command=self.set).grid(row=2,column=0)


#     def set(self):
#         title=self.titleentry.get()
#         legendlist=self.legendlist

#     def titleedit(self):
#         if self.titlevar.get()==1:
#             self.titleentry=tk.Entry(self, width=18)
#             self.titleentry.grid(row=5,column=12,sticky='s')
#         else:
#             self.titleentry.destroy()
    
#     def custom(self):
        
#         if self.custvar.get()==1:
#             print('reyna')
#             try:
#                 self.n=len(self.filelist)
#                 print(f'{self.n} self.n náði að prenntast')
#             except:
#                 self.n=0

#             self.customframe=tk.Frame(self)
#             self.customframe.grid(row=23,column=15, columnspan=1,rowspan=5,sticky='nes')
#             self.legendlist=[]
#             for i in range(0, self.n):
                
#                 entr = tk.Entry(self.customframe, width=18)
#                 entr.grid(row=i,column=0)
#                 entr.insert(0,self.filelist[i].split("/")[-1])
#                 self.legendlist.append(entr)
#                 self.customframe.rowconfigure(i,weight=1)
#             print(self.legendlist)
#         else:
#             self.customframe.destroy()

#use try here so the GUI can be used outside the experimental setup
#this sets up the connection to the network analyzer and the magnet
try:
    from RsInstrument import *
    resource='TCPIP0::192.168.1.200::inst0::INSTR'
    inst=RsInstrument(resource,True,True)
    inst.visa_timeout=5000
    inst.opc_timeout=500000
    inst.instrument_status_checking = True
    inst.clear_status()
    print(f'Connected to {inst.query_str("*IDN?")}')
    inst.write_str_with_opc("CALC2:PAR:SDEF 'Trc2', 'S11'")

    inst.write_str_with_opc("DISP:WIND2:STAT ON; TRAC:FEED 'Trc2'")
    inst.write_str_with_opc("DISP:WIND:STAT OFF")
    inst.write_str_with_opc("INIT2:CONT:ALL OFF")
    inst.write_str_with_opc("SENS2:FREQ:STAR 50e6; STOP 4e9")
    savelist=[]
    nfpoints=10
except:
    print('Network analyzer is not responding')


#try:
#    import instruments as ik 
#    inst= ik.generic_scpi.SCPIInstrument.open_vxi11("192.168.1.200")
#    #inst.write("*RST")
#    inst.write("CALC2:PAR:SDEF 'Trc2', 'S11'")
#    #inst.write("CALC2:FORM:WQUT POW")
#    #inst.write("CALC2:FORM SMIT")
#    #inst.write("SENS2:CORR:EDEL1:ELEN 0.602")
#    #inst.write("SENS2:CORR:EDEL1:DIEL 2.1")
#    inst.write("DISP:WIND2:STAT ON; TRAC:FEED 'Trc2'")
#    inst.write("DISP:WIND:STAT OFF")
#    inst.write("INIT2:CONT:ALL OFF")
#    inst.write("SENS2:FREQ:STAR 50e6; STOP 4e9")
#    nave=10
#    savelist=[]
#    nfpoints=10
#except:
#    nfpoints=10
#    print('Network analyser is not responding')

# Comedi setup, configuration for read and write
dev=None
try:
    import nidaqmx
    
    path = f=open("C:/Users/Notandi/Documents/FMR/magnari/Mælingar/calib_results.dat")
    lines = (line for line in f if not line.startswith('#'))
    FH = np.loadtxt(lines)
    f.close()
    path = f=open("C:/Users/Notandi/Documents/FMR/magnari/Mælingar/calib_results_Ls.dat")
    lines = (line for line in f if not line.startswith('#'))
    FH1 = np.loadtxt(lines)
    f.close()
except:
    print('Magnet not responding')

multimeter=0
try:
    import pyvisa
    
    multimeter=1
    rm=pyvisa.ResourceManager()
    instCurr=rm.open_resource('GPIB0::17::INSTR')
    instCurr.write('F5R5S2T0Y1')
except:
    print('Multimeter not responding')


if __name__=='__main__':
    app = App()
    #app.tk.call('tk_getOpenFile','-foobarbaz')
    #app.tk.call('set','::tk::dialog::file:showHiddenBtn','0')
    #app.tk.call('set','::tk::dialog::file::showHiddenVar','0')
    app.mainloop()
