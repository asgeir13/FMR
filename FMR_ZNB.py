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
import pandas as pd
import datetime
from scipy import signal, optimize
import math
from astropy import modeling
from lmfit.models import GaussianModel, LorentzianModel
import cmath
from reportlab.pdfgen.canvas import Canvas
from PIL import Image
import codecs
from lmfit import Minimizer, report_fit, Parameters

    #App class makes the frames and allows easy switching between them, frames are the different windows that pop up and cover the GUI,
    #calibrate, batch and viewer are "independent" frames

class App(tk.Tk):
    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.wm_title(self, "FMR")
        container = tk.Frame(self)
        container.pack(side=TOP, fill=BOTH, expand=True)

        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)
        
        x, y = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry("%dx%d+%d+%d" % (1500,900,x/2-1500/2,y/2-900/2))

        self.frames = {}
        #for-loop to place each page in the container or parent page
        for F in (Measure, Calibrate, Batch, Viewer2):

            frame = F(container, self)

            self.frames[F] = frame


            frame.grid(row = 0, column = 0, sticky="nsew")

        self.show_frame(Batch)
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

        self.fig = plt.figure(constrained_layout=False, figsize=[10,9])
        gs1 = self.fig.add_gridspec(nrows=1, ncols=2, left=0.1, right=0.95, wspace=0.3)
        self.ax = self.fig.add_subplot(gs1[0,0])
        self.ax1 = self.fig.add_subplot(gs1[0,1])
        self.ax.set_xlabel('$f$ [Hz]')
        self.ax1.set_xlabel('$f$ [Hz]')
        self.ax.set_ylabel('S11 resistance [$\Omega$]')
        self.ax1.set_ylabel('S11 reactance [$\Omega$]')
        self.canvas=FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().grid(row=0, column=0, rowspan=30, columnspan=10, sticky='nswe')
        self.toolbarframe=tk.Frame(self)
        self.toolbarframe.grid(row=32, column=0, columnspan=10, sticky='nwe')
        self.toolbar=NavigationToolbar2Tk(self.canvas, self.toolbarframe)
        self.toolbar.grid(row=0, column=0, columnspan=10, sticky='nwe')
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
        tk.Button(self.scanframe, text="Calibrate IF", command=self.cal, font=fontconf).grid(row=5, column=1,columnspan=2)


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

    def cal(self):
        inst.write("HCT")
        self.status.insert(END, 'Running IF calibration')
        self.status.yview(END)

        #saves all the arrays, filedialog.asksaveasfile creates pop up save window
    def file_save(self):
        f = tk.filedialog.asksaveasfile(mode="w", defaultextension="*.txt")
        intro=f"#FMR data, this file includes calibration measurements, correction factor and corrected S11, Number of measurments: {nave+1}, number of points {nfpoints}, IF BW {IF_BW}\n"
        intro2=f"#Notes: {self.notes.get('1.0','end')}"
        intro1="freq\tS11a\tS11m\tS11o\tS11l\tS11s\tZa\tEdf\tErf\tEsf\n"
        dataout=np.column_stack((self.freq, self.S11a, self.S11m, S11o, S11l, S11s, self.Za, Edf, Erf, Esf))
        #write the two headers and then writing the array dataout with a double for-loop
        f.write(intro)
        f.write(intro2)
        f.write(intro1)
        for i in np.arange(len(dataout)):
            for n in np.arange(len(dataout[0])):
                if n==0:
                    f.write(str(dataout[i][n].real))
                    f.write("\t")
                else:
                    f.write(str(dataout[i][n]))
                    f.write("\t")
            f.write("\n")
        f.close

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
        real_p, imag_p, self.freq = self.measure()
        plt.ion() #enable interactive plotting
        self.S11m=real_p+1j*imag_p
        self.docal() #run docal function to receive Za and S11a
        self.ax.clear()
        self.ax1.clear()
        self.ax.set_xlabel('$f$ [Hz]')
        self.ax1.set_xlabel('$f$ [Hz]')
        self.ax.set_ylabel('$Z_a$ resistance [$\Omega$]')
        self.ax1.set_ylabel('$Z_a$ reactance [$\Omega$]')
        self.ax.plot(self.freq, self.Za.real)
        self.ax1.plot(self.freq, self.Za.imag)
        self.canvas.draw_idle()  #enables gentile plotting, doesn't interupt the GUI's internal loops
        self.canvas.flush_events()
        self.status.insert(END, 'Measurement complete')
        self.status.yview(END)

    def measure(self):
        inst.write("INIT2:IMM; *WAI")
        valu=inst.ask("CALC2:DATA? SDATA")
        values=np.array([float(x) for x in valu.rsplit(',')])
        real=values[0:-1:2]
        imag=values[1::2]
        start=float(inst.ask("FREQ:STAR?"))
        stop=float(inst.ask("FREQ:STOP?"))
        point=int(inst.ask("SENS2:SWEEP:POINTS?"))
        step=int(inst.ask("SENS2:SWEEP:STEP?"))
        freq=np.linspace(start,stop,num=point)
        frek=np.arange(start,stop,step)
        return real, imag, freq
  
    #set the magnetic field. FH are values read from a calibration file, which can be updated 
    def writevolt(self):
        dev = comedi.comedi_open("/dev/comedi0")

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
        val, val1 = int(np.around(val)), int(np.around(val1))
        if val < 0 and val > 4095 and val1<0 and val1 > 4095:
            val, val1 = datazero, datazero
            print('Input value not available')
            self.status.insert(END, 'Input value not available')
            self.status.yview(END)
        retvalw = comedi.comedi_data_write(dev, subdevw, chanw, rngw, aref, val)
        retvalw1 = comedi.comedi_data_write(dev, subdevw, chanw1, rngw, aref, val1)
        comedi.comedi_close(dev)
           
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

        dev = comedi.comedi_open("/dev/comedi0")
        retval = comedi.comedi_data_write(dev, subdevw, chanw, rngw, aref, datazero)
        retval1 = comedi.comedi_data_write(dev, subdevw, chanw1, rngw, aref, datazero)
        print(f'Resetting DAQs to zero: {retval}')
        self.status.insert(END, f'Resetting DAQs to zero')
        self.status.yview(END)
        comedi.comedi_close(dev)

    #page to set the initial values
class Calibrate(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.fig = plt.figure(constrained_layout=False, figsize=[10,9])
        gs1 = self.fig.add_gridspec(nrows=1, ncols=2, left=0.1, right=0.95, wspace=0.3)
        self.ax = self.fig.add_subplot(gs1[0,0])
        self.ax1 = self.fig.add_subplot(gs1[0,1])
        self.ax.set_xlabel('$f$ [Hz]')
        self.ax1.set_xlabel('$f$ [Hz]')
        self.ax.set_ylabel('S11 resistance [$\Omega$]')
        self.ax1.set_ylabel('S11 reactance [$\Omega$]')
        self.canvas=FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().grid(row=0, column=0, rowspan=30, columnspan=10, sticky='nswe')
        self.toolbarframe=tk.Frame(self)
        self.toolbarframe.grid(row=31, column=0, columnspan=10, sticky='nwe')
        self.toolbar=NavigationToolbar2Tk(self.canvas, self.toolbarframe)
        self.toolbar.grid(row=0, column=0, columnspan=10, sticky='nwe')
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

        tk.Button(self.magfield, text="Reset", command=self.zerofield, font=fontconf).grid(row=2, column=2,columnspan=2,sticky='w')
        tk.Button(self.magfield, text="Set", command=self.writevolt, width=2, font=fontconf).grid(row=2, column=1, sticky='e')
        
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
        self.stopentry.insert(0, "10000")
        self.stopentry.grid(row=1, column=1)
        tk.Label(self.sweepframe, text="MHz").grid(row=1, column=2)

        tk.Label(self.sweepframe, text="Nr. of meas.", font=fontconf).grid(row=2, column=0,sticky='e')
        self.numberentry=tk.Entry(self.sweepframe, width=5)
        self.numberentry.insert(0, "10")
        self.numberentry.grid(row=2, column=1)

        tk.Label(self.sweepframe, text="Data points", font=fontconf).grid(row=3,column=0,sticky='e')
        self.pointsbox=tk.Entry(self.sweepframe, width=6)
        self.pointsbox.insert(0, "401")
        self.pointsbox.grid(row=3, column=1)
        self.pointlist=["51", "101", "201", "401", "801", "1601"]
        tk.Button(self.sweepframe, text="+", width=2, command=lambda: self._up(0), font=fontconf).grid(row=3, column=3)
        tk.Button(self.sweepframe, text="-", width=2, command=lambda: self._down(0), font=fontconf).grid(row=3,column=2)

        tk.Label(self.sweepframe, text="IF BW", font=fontconf).grid(row=4, column=0,sticky='e')
        self.IF_list=["10 Hz", "100 Hz", "1 kHz", "10 kHz"]
        self.IF_BW=tk.Entry(self.sweepframe,width=6)
        self.IF_BW.insert(0,"1 kHz")
        self.IF_BW.grid(row=4, column=1)
        tk.Button(self.sweepframe, text="+", width=2, command=lambda: self._up(1), font=fontconf).grid(row=4, column=3)
        tk.Button(self.sweepframe, text="-", width=2, command=lambda: self._down(1), font=fontconf).grid(row=4,column=2)
        tk.Button(self.sweepframe, text="Set values", width=8, command=self.set_values, font=fontconf).grid(row=1, column=4)
        tk.Button(self.sweepframe, text="Calibrate IF", width=8, command=self.cal, font=fontconf).grid(row=2, column=4)
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
        global nave, nfpoints, IF_BW
        start=self.startentry.get()
        stop=self.stopentry.get()
        start="STAR "+start+"e6"
        stop="STOP "+stop+"e6"
        freqstring="FREQ:"+start+"; "+stop
        inst.write(freqstring)
        #set IF_BW value
        IF_BW=self.IF_BW.get()
        inst.write(f"BAND {IF_BW}")
        ask=inst.ask("BAND?")
        self.status.insert(END, f"IF BW: {ask}")
        #number of data points set, 
        inst.write("SENS2:SWE:POIN "+self.pointsbox.get())
        nfpoints=int(self.pointsbox.get())
        inst.write(f"SENS2:SWEEP:COUN {self.numberentry.get()}")
        ask=inst.ask('SENS2:SWEEP:COUN?')
        self.status.insert(END,f"Count: {ask}")
        nave=int(self.numberentry.get())-1
        self.status.insert(END, 'Setting current values')
        self.status.yview(END)


        #set the magnetic field. FH are values read from a calibration file, which can be updated 
    def writevolt(self):
        dev = comedi.comedi_open("/dev/comedi0")

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
        val, val1 = int(np.around(val)), int(np.around(val1))
        if val < 0 and val > 4095 and val1<0 and val1 > 4095:
            val, val1 = datazero, datazero
            print('Input value not available')
            self.status.insert(END, 'Input value not available')
        retvalw = comedi.comedi_data_write(dev, subdevw, chanw, rngw, aref, val)
        retvalw1 = comedi.comedi_data_write(dev, subdevw, chanw1, rngw, aref, val1)
        comedi.comedi_close(dev)
        print(f"Value set to: {val}")
          
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

        dev = comedi.comedi_open("/dev/comedi0")
        retval = comedi.comedi_data_write(dev, subdevw, chanw, rngw, aref, datazero)
        retval = comedi.comedi_data_write(dev, subdevw, chanw1, rngw, aref, datazero)
        print(f'Resetting DAQs to zero: {retval}')
        self.status.insert(END, f'Resetting DAQs to zero')
        self.status.yview(END)

        comedi.comedi_close(dev)

        #receiving measurements from the network analyzer
    def measure(self):
        inst.write("INIT2:IMM; *WAI")
        
        valu=inst.ask("CALC2:DATA? SDATA")
        values=np.array([float(x) for x in valu.rsplit(',')])
        real=values[0:-1:2]
        imag=values[1::2]
        start=float(inst.ask("FREQ:STAR?"))
        stop=float(inst.ask("FREQ:STOP?"))
        point=int(inst.ask("SENS2:SWEEP:POINTS?"))
        step=int(inst.ask("SENS2:SWEEP:STEP?"))
        freq=np.linspace(start,stop,num=point)
        frek=np.arange(start,stop,step)
        print(len(frek))
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
        self.ax.set_ylabel('S11 resistance [$\Omega$]')
        self.ax1.set_ylabel('S11 reactance [$\Omega$]')
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

        self.fig = plt.figure(constrained_layout=False, figsize=[10,9])
        gs1 = self.fig.add_gridspec(nrows=1, ncols=2, left=0.1, right=0.95, wspace=0.3)
        self.ax = self.fig.add_subplot(gs1[0,0])
        self.ax1 = self.fig.add_subplot(gs1[0,1])
        self.ax.set_xlabel('$f$ [Hz]')
        self.ax1.set_xlabel('$f$ [Hz]')
        self.ax.set_ylabel('S11 resistance [$\Omega$]')
        self.ax1.set_ylabel('S11 reactance [$\Omega$]')
        self.canvas=FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().grid(row=0, column=0, rowspan=30, columnspan=10, sticky='nswe')
        self.toolbarframe=tk.Frame(self)
        self.toolbarframe.grid(row=31, column=0, columnspan=10, sticky='nwe')
        self.toolbar=NavigationToolbar2Tk(self.canvas, self.toolbarframe)
        self.toolbar.grid(row=0, column=0, columnspan=10, sticky='nwe')
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
        tk.Button(self.scanframe, text="IF calibrate", command=self.cal, font=fontconf).grid(row=2,column=2,columnspan=2,sticky='w')
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

    def cal(self):
       inst.write("HCT")
       self.status.insert(END, 'Running IF calibration')
       self.status.yview(END)

    def calcvect(self):
        try:
            if int(self.stepang.get())!=0:
                step = float(self.stepang.get())
                self.angles = np.arange(float(self.startang.get())*np.pi/180, (float(self.stopang.get())+step)*np.pi/180, step*np.pi/180)
                print(self.angles)
                self.status.insert(END, f'{np.arange(float(self.startang.get()),float(self.stopang.get())+step, step)}')
                self.status.yview(END)
                mag = float(self.mag.get())
                par=[int(np.around(mag*np.cos(element)*FH1[0]+FH1[1])) for n, element in enumerate(self.angles)]
                per=[int(np.around(mag*np.sin(element)*FH[0]+FH[1])) for n, element in enumerate(self.angles)]
                self.values=np.row_stack((par,per))
                self.type="ang"
            elif int(self.step.get())!=0:
                step = float(self.step.get())
                self.values=np.arange(float(self.start.get()), float(self.stop.get())+float(step), float(step))
                self.status.insert(END, f'{self.values}')
                self.values=[int(element*FH1[0]+FH1[1]) for n, element in enumerate(self.values)]
                self.type="parallel"
            
            elif self.vector.get()!='':
                print(self.vector.get())
                for n, i in enumerate(self.vector.get().split(':')):
                    print(n)
                    print(i)
                    if n==0:
                        mag=float(i)
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
                par=[int(np.around(mag*np.cos(element)*FH1[0]+FH1[1])) for n, element in enumerate(self.angles)]
                per=[int(np.around(mag*np.sin(element)*FH[0]+FH[1])) for n, element in enumerate(self.angles)]
                self.values=np.row_stack((par,per))
                self.type="ang"

        except:
            print('Dividing by zero')
            self.status.insert(END, 'Dividing by zero')
            self.status.yview(END)
    
        #set the magnetic field. FH are values read from a calibration file, which can be updated 
    def writevolt(self):
        dev = comedi.comedi_open("/dev/comedi0")
        
        if len(self.values)==2 or self.blank==True: 
            val, val1=int(self.val[0]), int(self.val[1])

            if val < 0 and val > 4095 and val1<0 and val1 > 4095:
                val, val1 = datazero, datazero
                print('Input value not available')
                self.status.insert(END, 'Input value not available')
            retvalw = comedi.comedi_data_write(dev, subdevw, chanw, rngw, aref, val)
            retvalw1 = comedi.comedi_data_write(dev, subdevw, chanw1, rngw, aref, val1)
            comedi.comedi_close(dev)
            print(f"Value set to: {val}")
            self.status.insert(END, f'Value set to: {val}')
            self.status.yview(END)

        else:
            if self.val<0 and self.val>4095:
                self.val=datazero
                print('Input value not available')
                self.status.insert(END, 'Input value not available')
                self.status.yview(END)
            retvalw=comedi.comedi_data_write(dev, subdevw,chanw,rngw,aref, int(self.val))

        #reset the magnet
    def zerofield(self):
        dev = comedi.comedi_open("/dev/comedi0")
        retval = comedi.comedi_data_write(dev, subdevw, chanw, rngw, aref, datazero)
        retval = comedi.comedi_data_write(dev, subdevw, chanw1, rngw, aref, datazero)
        print(f'Resetting DAQs to zero: {retval}')
        self.status.insert(END, f'Resetting DAQs to zero: {retval}')
        self.status.yview(END)
        comedi.comedi_close(dev)

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
        par=[int(np.around(mag*np.cos(element)*FH1[0]+FH1[1])) for n, element in enumerate(angles)]
        per=[int(np.around(mag*np.sin(element)*FH[0]+FH[1])) for n, element in enumerate(angles)]
        values=np.row_stack((par,per))

        for i, item in enumerate(angles):
            self.val=values[:,i]
            print(round(item*180/np.pi))
            self.status.insert(END, str(round(item*180/np.pi)))
            self.status.yview(END)
            self.writevolt()
            time.sleep(0.5)
        
        self.blank=False


    def batchscan(self):
        self.run=True
        self.blank=False
       
        if self.type=="ang":
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
            self.takecal()
            #if self.type=="ang":
            #    print("ang")

            if i ==0:
                self.array=np.column_stack((self.S11a, self.Za, self.S11m))
            else:
                self.array=np.column_stack((self.array, self.S11a, self.Za, self.S11m))

        print('done')
        self.status.insert(END, 'Done')
        self.status.yview(END)
        self.zerofield()
      
        #receiving measurements from the network analyzer
    def measure(self):
        inst.write("INIT2:IMM; *WAI")
        
        valu=inst.ask("CALC2:DATA? SDATA")
        values=np.array([float(x) for x in valu.rsplit(',')])
        real=values[0:-1:2]
        imag=values[1::2]
        start=float(inst.ask("FREQ:STAR?"))
        stop=float(inst.ask("FREQ:STOP?"))
        point=int(inst.ask("SENS2:SWEEP:POINTS?"))
        step=int(inst.ask("SENS2:SWEEP:STEP?"))
        freq=np.linspace(start,stop,num=point)
        frek=np.arange(start,stop,step)
        print(len(frek))
        return real, imag, freq

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
        real_p, imag_p, self.freq = self.measure()
        plt.ion()
        self.S11m=real_p+1j*imag_p
        self.docal()
        self.ax.clear()
        self.ax1.clear()
        self.ax.set_xlabel('$f$ [Hz]')
        self.ax1.set_xlabel('$f$ [Hz]')
        self.ax.set_ylabel('$Z_a$ resistance [$\Omega$]')
        self.ax1.set_ylabel('$Z_a$ reactance [$\Omega$]')

        if len(self.values)==2:
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
        filename = tk.filedialog.asksaveasfilename(defaultextension="*.txt")
        intro=f'''#FMR data from {datetime.datetime.now()}, this file includes calibration measurements, correction factor and corrected S11, Number of measurments: {nave+1}, number of points {nfpoints}, IF BW {IF_BW} 
#Notes: {self.notes.get('1.0','end')}
freq\tS11o\tS11l\tS11s\tEdf\tErf\tEsf\tS11a\tZa\tS11m'''
        fmt='%.5e'
        np.savetxt('prufa.dat', np.arange(1,4) ,header=intro)
        dataout=np.column_stack((self.freq, S11o, S11l, S11s, Edf, Erf, Esf))
        
        if self.type=="ang":
            for i, n in enumerate(self.values[0,:]):
                looparray=np.column_stack((dataout, self.array[:,i*3:(i*3+3)]))
                label=self.mag.get()+'G_'+str(np.around(self.angles[i]*180/np.pi))+'deg.dat'
                np.savetxt(filename.rsplit('.')[0]+label, looparray, delimiter='\t', header=intro, fmt=fmt, comments='')
 
        elif self.type=="parallel":
            for i, n in enumerate(self.values):
                looparray=np.column_stack((dataout, self.array[:,i*3:(i*3+3)]))
                label=str(np.around((n-FH1[1])/FH1[0]))+'G.dat'
                np.savetxt(filename.rsplit('.')[0]+label, looparray, delimiter='\t', header=intro, fmt=fmt, comments='')



class Viewer2(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.buttonframe=tk.Frame(self)
        self.buttonframe.grid(row=0,column=11, columnspan=2,rowspan=2,sticky='wn')
        tk.Button(self.buttonframe, text="Measure", command=lambda: controller.show_frame(Measure), width=8, height=1, font=fontconf).grid(row=0,column=0,padx=5)
        tk.Button(self.buttonframe, text="Viewer", command=lambda: controller.show_frame(Viewer2), width=8, height=1, font=fontconf).grid(row=0,column=1)
        tk.Button(self.buttonframe, text="Batch", command=lambda: controller.show_frame(Batch), width=8, height=1, font=fontconf).grid(row=1, column=0, sticky='n', padx=5)
        tk.Button(self.buttonframe, text="Calibrate", command=lambda: controller.show_frame(Calibrate), width=8, height=1, font=fontconf).grid(row=1,column=1, sticky='n')
        tk.Button(self, text="Exit", command=self._quit, font=fontconf).grid(row=0, column=18, sticky='ne')
        #tk.Button(self, text="Single", command=lambda: controller.show_frame(Viewer2), width=8, height=1).grid(row=2, column=11, sticky='n')
        #tk.Button(self, text="Pair", command=lambda: controller.show_frame(Viewer), width=8, height=1).grid(row=2, column=12, sticky='n')
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
        
        self.listbox=tk.Listbox(self.plotframe, width=6, height=1)
        self.listbox.grid(row=1, column=0)
        self.elements=["EA_1","Za", "angle","polar", "ku", "Ku", "4-fold","Oblique", "Cubic Kohmoto (100) + uni","Cubic Kohmoto (110)", "EA", "S11a", "S11m", "S11o", "S11l", "S11s", "Edf", "Erf", "Esf"]
        
        for i, ele in enumerate(self.elements):
            self.listbox.insert(i, ele)

        self.editframe=tk.Frame(self)
        self.editframe.grid(row=5,column=11,columnspan=2,rowspan=4,sticky='wn')
        self.titlevar=tk.IntVar()
        self.titlevar.set(0)
        tk.Checkbutton(self.editframe, text='Title', variable=self.titlevar, command=self.title, font=fontconf).grid(row=5,column=11,sticky='w')
        self.custvar=tk.IntVar()
        self.custvar.set(0)
        tk.Checkbutton(self.editframe, text='Legend', variable=self.custvar, command=self.custom, font=fontconf).grid(row=7,column=11,sticky='nw')
        self.shiftvar=tk.IntVar()
        self.shiftvar.set(0)
        tk.Checkbutton(self.editframe, text='Shift', variable=self.shiftvar, command=self.shift, font=fontconf).grid(row=6,column=11,sticky='w')
        
        self.listboxopen=tk.Listbox(self.plotframe, selectmode=tk.EXTENDED, height=6, width=22)
        self.listboxopen.grid(row=3, column=0, rowspan=4, columnspan=10)
        tk.Button(self.plotframe, text="Remove", command=self.listbox_delete,width=6, font=fontconf).grid(row=0, column=1,sticky='w')
        self.plotframe.bind_all('<Delete>', lambda e:self.listbox_delete())
        self.filelist=[]
        tk.Button(self.plotframe, text='up', command=lambda: self.reArrangeListbox("up"), font=fontconf).grid(row=0, column=3)
        tk.Button(self.plotframe, text='dn', command=lambda: self.reArrangeListbox("dn"), font=fontconf).grid(row=1, column=3)
        
        #tk.Label(self, text="Analysis", relief='ridge').grid(row=7, column=13)

        self.chipeakframe=tk.Frame(self)
        self.chipeakframe.grid(row=10,column=14,columnspan=5,rowspan=3)
        self.peak=tk.Button(self.chipeakframe, text="Peak", command=self.peak_finder, width=4, font=fontconf).grid(row=0, column=1,sticky='w')
        #tk.Button(self.chipeakframe, text="+", command=lambda: self.jump_right(0)).grid(row=0, column=3, sticky='w')
        #tk.Button(self.chipeakframe, text="-", command=lambda: self.jump_left(0)).grid(row=0, column=2, sticky='e')
        self.chipeakframe.bind_all('<p>', lambda e:self.peak_finder())
        tk.Button(self.chipeakframe, text='Save', command=self.save, font=fontconf).grid(row=1, column=1)
        tk.Button(self.chipeakframe, text='Create', command=self.save_as,width=5, font=fontconf).grid(row=1, column=0)
        tk.Label(self.chipeakframe, text="Order", font=fontconf).grid(row=0, column=4, sticky='e')
        tk.Label(self.chipeakframe, text="Peak W.", font=fontconf).grid(row=1,column=4,sticky='e')
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
        self.sampleframe.grid(row=13,column=15,rowspan=3, columnspan=2)
        self.circ=tk.Checkbutton(self.sampleframe, text="Circular", variable=self.circvar, font=fontconf)
        self.square=tk.Checkbutton(self.sampleframe, text="Square", variable=self.squarevar, font=fontconf)
        tk.Label(self, text="Sample", relief='ridge', font=fontconf).grid(row=13, column=14)
        tk.Label(self.sampleframe, text="Width [mm]", font=fontconf).grid(row=0, column=0,sticky='e')
        tk.Label(self.sampleframe, text="Thickness [nm]", font=fontconf).grid(row=1, column=0,sticky='e')
        self.circ.grid(row=3, column=0)
        self.square.grid(row=3, column=1)
        self.entrywidth = tk.Entry(self.sampleframe,width=5)
        self.entrywidth.insert(0, "4")
        self.entrywidth.grid(row=0, column=1)
        self.entrythick = tk.Entry(self.sampleframe,width=5)
        self.entrythick.insert(0, "50")
        self.entrythick.grid(row=1, column=1)
        
        tk.Label(self, text="FWHM", relief='ridge', font=fontconf).grid(row=16, column=14)
        self.fwhmframe=tk.Frame(self)
        self.fwhmframe.grid(row=16,column=15, rowspan=3,columnspan=4)
        tk.Button(self.fwhmframe, text='Determine', command=lambda: self.fwhm(0), font=fontconf).grid(row=0, column=0)
        tk.Button(self.fwhmframe, text='Rerun', command=lambda: self.fwhm(1), font=fontconf).grid(row=0,column=1)
        self.fwhmframe.bind_all('<r>', lambda e:self.fwhm(1))
        tk.Label(self.fwhmframe, text='Resize', font=fontconf).grid(row=0,column=2)
        self.entrySize=tk.Entry(self.fwhmframe,width=4)
        self.entrySize.insert(0,'0')
        self.entrySize.grid(row=0,column=3)
        for i in np.arange(0,3):
            self.fwhmframe.columnconfigure(i,weight=1)
        
        tk.Label(self, text='Axis limits',relief='ridge', font=fontconf).grid(row=17,column=14)
        #tk.Label(self.fwhmframe,text='Vert').grid(row=3,column=0)
        tk.Label(self.fwhmframe,text='Horiz', font=fontconf).grid(row=2,column=0)
        fwhmfr=self.fwhmframe
        self.axismin,self.axismax=tk.Entry(fwhmfr,width=6),tk.Entry(fwhmfr,width=6)
        i=0
        for F in (self.axismin,self.axismax):
            F.insert(0,'0')
            if i<2:
                F.grid(row=2,column=i+1)
            else:
                F.grid(row=3,column=i-1)
            i+=1

        #tk.Label(self.fwhmframe,text='Ang. freq').grid(row=3,column=0)
        self.AngVar=tk.IntVar(self)
        self.AngVar.set(1)
        self.Changular=tk.Checkbutton(self.fwhmframe,text='Ang. freq', variable=self.AngVar, font=fontconf).grid(row=3,column=0)
        tk.Label(self, text='Fit')
        self.varGauss, self.varLor=tk.IntVar(self), tk.IntVar(self)
        self.Gauss=tk.Checkbutton(self.fwhmframe, text="Gaussian", variable=self.varGauss,command=lambda: self.set_checkfit(0), font=fontconf).grid(row=1,column=0)
        self.Lorentz=tk.Checkbutton(self.fwhmframe, text="Lorentzian", variable=self.varLor,command=lambda: self.set_checkfit(1), font=fontconf).grid(row=1,column=1)
        self.varGauss.set(0)
        self.varLor.set(1)

        self.fitchivar=tk.IntVar(self)
        self.fitchi=tk.Checkbutton(self,text="Fit Chi", variable=self.fitchivar,command=self.fitchiframe, relief='ridge', font=fontconf).grid(row=20,column=14)

        #tk.Button(self, text='Edit', command=self.openpop).grid(row=20,column=15)        
        self.fig = plt.figure(figsize=[10,9])
        self.ax = plt.subplot()
        self.ax.set_xlabel('$f$ [Hz]')
        self.ax.set_ylabel('S11')
        
        self.canvas=FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().grid(row=0, column=0, rowspan=30, columnspan=10, sticky='nswe')
        self.toolbarframe=tk.Frame(self)
        self.toolbarframe.grid(row=31, column=0, columnspan=10, sticky='nwe')
        self.toolbar=NavigationToolbar2Tk(self.canvas, self.toolbarframe)
        self.toolbar.grid(row=0, column=0, columnspan=10, sticky='nwe')
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
        skjal.write('Filename\tAmplitude\tMean[Hz]\tStddev[Hz]\tFWHM[Hz]\n') 
        skjal.close()
        self.skjal=filename

    def save(self):
        try:
            t=self.skjal
        except:
            t=tk.filedialog.askopenfilename()
            self.skjal=t
            
        skjal=open(t,'a')
        selection=self.listboxopen.curselection()
        if len(selection) > 0:
            plotlist = [item for n, item in enumerate(self.filelist) if n in selection]
        else:
            plotlist = self.filelist
        nafn=plotlist[0].split('/')[-1].split('.')[0]+'G'
        
        lina=f'{nafn}\t{self.ampl}\t{float(self.maxima)}\t{self.sigma}\t{self.variance}\n'
        skjal.write(lina)
        skjal.close()

    def fwhm(self, dex):
        
        freqspan=self.freq[-1]-self.freq[0]
        peakwith=float(self.entryPwidth.get())
        indexspan=int(round((peakwith/freqspan)*len(self.freq)))
        #dw=int((self.peaks_imag[0,self.indexmax]-self.peaks_imag[0,self.indexmax-1])/2)
        #dw1=int((self.peaks_imag[0,self.indexmax+1]-self.peaks_imag[0,self.indexmax])/2)
        #if dw>dw1:
        #    dw=dw1

        if self.varGauss.get() == 1:
            model=GaussianModel()
        else:
            model=LorentzianModel()

        if dex==0:
            if self.axismin.get() != '0':
                self.freqfit=self.nfreq[int(round(self.indexmax-indexspan/2)):int(round(self.indexmax+indexspan/2))]
                self.imagfit=self.nimag[int(round(self.indexmax-indexspan/2)):int(round(self.indexmax+indexspan/2))]
                self.realfit=self.real[int(round(self.indexmax-indexspan/2)):int(round(self.indexmax+indexspan/2))]
                params=model.make_params(amplitude=self.nimag[self.indexmax]*self.freqfit[0], center=self.nfreq[self.indexmax], sigma=(self.freqfit[-1]-self.freqfit[0])/2)
            else:
                self.freqfit=self.freq[int(round(self.indexmax-indexspan/2)):int(round(self.indexmax+indexspan/2))]
                self.imagfit=self.imag[int(round(self.indexmax-indexspan/2)):int(round(self.indexmax+indexspan/2))]
                params=model.make_params(amplitude=self.imag[self.indexmax]*self.freqfit[0], center=self.freq[self.indexmax], sigma=(self.freqfit[-1]-self.freqfit[0])/2)

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
                self.freqfit=self.freq[(self.indexmax-int(round(indexspan*factor**self.iteratorfwhm/2))):(self.indexmax+int(round(indexspan*factor**self.iteratorfwhm/2)))]
                self.imagfit=self.imag[(self.indexmax-int(round(indexspan*factor**self.iteratorfwhm/2))):(self.indexmax+int(round(indexspan*factor**self.iteratorfwhm/2)))]

        result=model.fit(self.imagfit, params, x=self.freqfit)
        print(result.fit_report())
        self.ampl=result.params['amplitude'].value#+self.shift
        self.mode=result.params['center'].value
        self.sigma=result.params['sigma'].value
        self.variance=result.params['fwhm'].value
        self.ax.clear()
        self.chi()
        self.ax.plot(self.freqfit, result.best_fit)#+self.shift)
        print(self.variance)
        self.maxima=self.freqfit[np.where(result.best_fit==max(result.best_fit))]
        if self.axismin.get() !='0':
            self.ax.set_xlim(float(self.axismin.get()),float(self.axismax.get()))
            self.ax.set_ylim(min(self.real[np.where((self.freq>round(float(self.axismin.get()))) & (self.freq<round(float(self.axismax.get()))))]),1.5*max(self.imag[np.where((self.freq>round(float(self.axismin.get()))) & (self.freq<round(float(self.axismax.get()))))]))
            #self.ax.autoscale(axis='y',tight=True)
#
        self.ax.plot(self.maxima-self.variance/2,(max(result.best_fit)/2),'*',self.maxima+self.variance/2, max(result.best_fit)/2,'*')#tók self.shift
        self.ax.plot(self.maxima,max(result.best_fit),'o')#+self.shift,'o')
        self.ax.autoscale(axis='y',tight=True)
        self.ax.legend()
        #if self.vaxismin.get() !='0':
         #   sefl.ax.set_ylim(float)
        self.canvas.draw()
        #laga peak_finder hægt að skoða hæðsta toppinn, þá væri gagnasöfnunin miklu hraðari

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
            frequency=self.freq
            self.real=self.chii.real
            self.imag=self.chii.imag
		
        if self.axismin.get() !='0':
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
            self.peaks_imag = signal.argrelextrema(self.imag,np.greater,order=entryorder)
            self.ax.plot(frequency[self.peaks_imag],self.imag[self.peaks_imag],'o')
            self.indexmax=int(np.where(max(self.imag[self.peaks_imag])==self.imag)[0])
            self.ax.plot(self.freq[self.indexmax],max(self.imag[self.peaks_imag]),'x') 
            print(type(self.indexmax))
        self.ax.autoscale(axis='y',tight=True)
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
        #self.chii = np.zeros(nfpoints, dtype=np.complex128)
        #string=self.filelist[0].rsplit('_')
        #string.pop(-1)
        #string.append('-0.0G.dat')
        #nstring='_'
        #nstring=nstring.join(string)
        #filezero=pd.read_csv(nstring, index_col=False, comment='#', sep='\t', engine='python')
        #Zzero=filezero['Za'].to_numpy(dtype=complex)

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
        w=4e-3 #width of loop is 4 mm
        W=w**2
        heightloop=1.6e-3 #height of loop is 1.6 mm
        k=2/np.pi*np.arctan(w/heightloop)
        psi=0.8
        k_h=k*psi

        selection=self.listboxopen.curselection()
        if len(selection) > 0:
            plotlist = [item for n, item in enumerate(self.filelist) if n in selection]
        else:
            plotlist = self.filelist

        self.ax.clear()
        self.ax.set_xlabel('$\omega$ [rad/s]')
        self.ax.set_ylabel('$\chi$')
        if self.titlevar.get()==1:
            self.ax.set_title(self.titleentry.get())
        
        if self.axismin.get()!='0':
            minchi=0 #gera ráð fyrir axislimits
            
        for n, item in enumerate(plotlist):
            texti=pd.read_csv(item, index_col=False, comment= "#", sep='\t', engine='python')
            self.freq=texti['freq'].to_numpy(dtype=complex).real*2*np.pi
            real=texti['Za'].to_numpy(dtype=complex).real
            imag=texti['Za'].to_numpy(dtype=complex).imag
            #real=real-Zzero.real
            #imag=imag-Zzero.imag
            chi=imag*W/(k_h*mu*V*self.freq*4*np.pi)
            chii=real*W/(k_h*mu*V*self.freq*4*np.pi)    #deili með 4 pi til þess að fá í cgs
            if self.shiftvar.get()==1:
                self.chii=chi+n*int(self.shiftentry.get())+1j*(chii+n*int(self.shiftentry.get()))
                            
            else:
                self.chii=chi+1j*chii
            
            #if self.axismin.get() !='0':

                #if min(self.chii.real[np.where(np.where((self.freq>round(float(self.axismin.get()))) & (self.freq<round(float(self.axismax.get())))))])<minchi:
                 #   minchi= min(self.chii.real[np.where(np.where((self.freq>round(float(self.axismin.get()))) & (self.freq<round(float(self.axismax.get())))))])

            re='Re($\chi$) '+item.split('/')[-1]
            im='Im($\chi$) '+item.split('/')[-1]
            if self.Re.get()==1 or self.Im.get()==1:
            	if self.Re.get()==1:
            		self.ax.plot(self.freq,self.chii.real,label=re)
            	else:
            		self.ax.plot(self.freq,self.chii.imag,label=im)
            else:
            	self.ax.plot(self.freq,self.chii.real,label=re)
            	self.ax.plot(self.freq,self.chii.imag,label=im)
            
            if self.custvar.get()==1:
                self.legendliststr=[]
                for i in range(0,self.n):
                    for n in range(0,1):
                        self.legendliststr.append(self.legendlist[i].get().split('.dat')[0].replace('_',' ').replace(' batch','')+' Re($\chi$)')
                        self.legendliststr.append(self.legendlist[i].get().split('.dat')[0].replace('_',' ').replace(' batch','')+' Im($\chi$)')

                self.ax.legend(self.legendliststr)
            #else:
                #self.ax.legend()#legend)
        if self.axismin.get() !='0':
            self.ax.set_xlim(float(self.axismin.get()),float(self.axismax.get()))
            #self.ax.autoscale(axis='y',tight=False)
            #print(max(chi[np.where((self.freq>round(float(self.axismin.get()))) & (self.freq<round(float(self.axismax.get()))))]))# & self.freq<round(float(self.axismax.get()))))
            self.ax.set_ylim(minchi,1.5*max(chii[np.where((self.freq>round(float(self.axismin.get()))) & (self.freq<round(float(self.axismax.get()))))]))
        self.canvas.draw()
        filename = "C:/Users/Geiri/Documents/Master/measurements/chi_gogn.txt"
        intro=f'''#FMR data from {datetime.datetime.now()} freq\chi_r\chi_i'''
        #fmt=['%.5e', '%.5e %+.5ej', '%.5e %+.5ej', '%.5e %+.5ej', '%.5e %+.5ej', '%.5e %+.5ej', '%.5e %+.5ej', '%.5e %+.5ej', '%.5e %+.5ej', '%.5e %+.5ej']
        fmt='%.5e'
        dataout=np.column_stack((self.freq, chi, chii))
        #np.savetxt(filename, dataout, delimiter='\t', header=intro, fmt=fmt, comments='')



    def fit_chi(self):
        freq=self.freq[200:-1]
        chii=self.chii.imag[200:-1]

        start=self.mode-3*self.variance
        end=(self.mode+3*self.variance)
        if self.entryLower.get()!='0':
            start=float(self.entryLower.get())
            end=float(self.entrySuperior.get())

        freqlin=freq[np.where(freq<start)]
        chiilin=chii[np.where(freq<start)]
        paralin=Parameters()
        paralin.add('a', value=-1E-6)
        paralin.add('b',value =-0.001)

        def linfunc(paralin,x,y):
            a=paralin['a']
            b=paralin['b']
            Y=a*x+b
            resids= (Y-y)**2

            return resids
        #minne = Minimizer(linfunc, paralin,fcn_args=(freqlin,chiilin))
        #resultlin = minne.minimize()
        #report_fit(resultlin)
        #a=resultlin.params['a'].value
        #b=resultlin.params['b'].value
        #tverhluti=self.chii.imag-a*self.freq-b
        #raunhluti=self.chii.real+a*self.freq+b

        #self.chii=raunhluti+1j*tverhluti

        #freq=np.linspace(0,max(self.freq),num=20000)
        gamma=float(self.entryGamma.get())
        gammaMin=float(self.entryGaMin.get())
        gammaMax=float(self.entryGaMax.get())
        M=float(self.entryMs.get())
        MMin=float(self.entryMsMin.get())
        MMax=float(self.entryMsMax.get())
        K_u=float(self.entryKu.get())
        K_uMin=float(self.entryKuMin.get())
        K_uMax=float(self.entryKuMax.get())
        #K_s=float(self.entryKs.get())
        #K_sMin=float(self.entryKsMin.get())
        #K_sMax=float(self.entryKsMax.get())
        H=float(self.filelist[0].split('_')[-1].split('.')[0])
        alpha=float(self.entryAlpha.get())
        alphavalueMin=float(self.entryAlMin.get())
        alphavalueMax=float(self.entryAlMax.get())
        d=float(self.entrythick.get())*1e-9
        #Dx=H+(4*np.pi+2*K_u/(M**2)+4*K_s/(d*M**2))*M
        #Dy=2*H+(4*np.pi+4*K_u/(M**2)+4*K_s/(d*M**2))*M

        def fcn2min(params, x, y):
            if alphavalueMin!=alphavalueMax:
                alpha=params['alpha']

            if MMin!=MMax:
                M=params['M']

            #if K_sMin!=K_sMax:
            #    K_s=params['Ks']

            if K_uMin!=K_uMax:
                K_u=params['Ku']

            if gammaMin!=gammaMax:
                gamma=params['gamma']
            
            alpha=params['alpha']
            M=params['M']
            #K_s=params['Ks']
            K_u=params['Ku']
            gamma=params['gamma']
            K_s=0

            chi_num=gamma**2*M*(H+(4*np.pi+2*K_u/(M**2)+4*K_s/(d*M**2))*M)+1j*x*alpha*gamma*M
            omegarpow2=gamma**2*(H+(4*np.pi+2*K_u/(M**2)+4*K_s/(d*M**2))*M)*(H+2*K_u/M)
            chi_den=omegarpow2-x**2*(1+alpha**2)+1j*x*gamma*alpha*(2*H+(4*np.pi+4*K_u/(M**2)+4*K_s/(d*M**2))*M)
            chi=chi_num/chi_den
            resids=(y.imag-chi.imag)**2+(y.real-chi.real)**2
            #resids=y-chi
            return resids#.view(float)

        params=Parameters()
        if gammaMin!=gammaMax:
            params.add('gamma',value=gamma,min=gammaMin,max=gammaMax)

        if alphavalueMin!=alphavalueMax:
            params.add('alpha',value=alpha,min=alphavalueMin,max=alphavalueMax)
                         
        #if K_sMin!=K_sMax:
        #    params.add('Ks',value=K_s,min=K_sMin,max=K_sMax)
            
        if MMin!=MMax:
            params.add('M',value=M,min=MMin,max=MMax)

        if K_uMin!=K_uMax:
            params.add('Ku',value=K_u,min=K_uMin,max=K_uMax)


        #tverhluti=self.chii-min(self.chii[np.where((self.freq>start*0.66) & (self.freq<end))].imag)
        #raunhluti=self.chii+min(self.chii[np.where((self.freq>start*0.66) & (self.freq<end))].imag)
        #chitoppur=raunhluti+1j*tverhluti
        #minner = Minimizer(fcn2min, params, fcn_args=(self.freq[np.where((self.freq>start*0.66) & (self.freq<end))],chitoppur[np.where((self.freq>start*0.66) & (self.freq<end))]))
        minner = Minimizer(fcn2min, params, fcn_args=(self.freq[np.where((self.freq>start) & (self.freq<end))], self.chii[np.where((self.freq>start) & (self.freq<end))]))
        #minner=Minimizer(fcn2min, params, fcn_args=(self.freq,self.chii))
        if self.varLeastsq.get()==1:
            metho='leastsq'
        else:
            metho='shgo'
        self.result = minner.minimize(method=metho)
        report_fit(self.result)
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
        
        K_s=0
        freq=self.freq[np.where((self.freq>start) & (self.freq<end))]
        chi_num=gamma**2*M*(H+(4*np.pi+2*K_u/(M**2)+4*K_s/(d*M**2))*M)+1j*freq*alpha*gamma*M
        omegarpow2=gamma**2*(H+(4*np.pi+2*K_u/(M**2)+4*K_s/(d*M**2))*M)*(H+2*K_u/M)
        chi_den=omegarpow2-freq**2*(1+alpha**2)+1j*freq*gamma*alpha*(2*H+(4*np.pi+4*K_u/(M**2)+4*K_s/(d*M**2))*M)
        chi=chi_num/chi_den
        self.ax.clear()
        if self.titlevar.get()==1:
            self.ax.set_title(self.titleentry.get())
        #self.ax.plot(freqlin,chiilin, '*',label='imaglin')
        self.ax.plot(self.freq, self.chii.real, label='$Re(\chi)$')  #+min(self.chii.imag[100:-1])
        self.ax.plot(self.freq, self.chii.imag, label='$Im(\chi)$')   #-min(self.chii.imag[100:-1])
        self.ax.plot(freq,chi.real,label="$Re(\chi)$ fit")
        self.ax.plot(freq,chi.imag,label="$Im(\chi)$ fit")
        self.ax.set_xlabel('$\omega$ [rad/s]')
        self.ax.set_ylabel('$\chi$')
        #self.ax.plot(omegarpow2,max(chi.imag),'*')
        self.ax.legend()
        self.canvas.draw()  
        
    def _quit(self):
        app.quit()
        app.destroy()

        #creates a list of .dat files to plot

    def file_open(self):
        t=tk.filedialog.askopenfilenames(initialdir='/home/fmrdata/',filetypes=(('dat files', '*.dat'),('all files','*.*')))
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
            file=tk.filedialog.askopenfilename()
            texti=pd.read_csv(file, index_col=False, comment= "#", sep='\t', engine='python')
            self.imported_values=texti['Value'].to_numpy()
            self.imported_min=texti['min'].to_numpy()
            self.imported_max=texti['max'].to_numpy()
            self.entryGamma.delete(0, END)
            self.entryGamma.insert(0,str(self.imported_values[0]))
            i=0
            for F in (self.entryGamma, self.entryAlpha, self.entryKu, self.entryKs, self.entryMs):
                F.delete(0, END)
                F.insert(0,str(self.imported_values[i]))
                i+=1
            i=0
            for F in (self.entryGaMin, self.entryAlMin, self.entryKuMin, self.entryKsMin, self.entryMsMin):
                F.delete(0, END)
                F.insert(0,str(self.imported_min[i]))
                i+=1
            i=0
            for F in (self.entryGaMax, self.entryAlMax, self.entryKuMax, self.entryKsMax, self.entryMsMax):
                F.delete(0, END)
                F.insert(0,str(self.imported_max[i]))
                i+=1
                
    def save_fit(self):
        filename = tk.filedialog.asksaveasfilename(defaultextension="*.txt")
        skjal=open(filename,'w')
        skjal.write('Variable\tValue\tmin\tmax\n')
        skjal.write(f'Gamma\t{self.entryGamma.get()}\t{self.entryGaMin.get()}\t{self.entryGaMax.get()}\n')
        skjal.write(f'Alpha\t{self.entryAlpha.get()}\t{self.entryAlMin.get()}\t{self.entryAlMax.get()}\n')
        skjal.write(f'Ku\t{self.entryKu.get()}\t{self.entryKuMin.get()}\t{self.entryKuMax.get()}\n')
        skjal.write(f'Ks\t{self.entryKs.get()}\t{self.entryKsMin.get()}\t{self.entryKsMax.get()}\n')
        skjal.write(f'Ms\t{self.entryMs.get()}\t{self.entryMsMin.get()}\t{self.entryMsMax.get()}\n')
        skjal.close()


    def fitchiframe(self):
        if self.fitchivar.get()==1:
            self.rowconfigure(20, weight=5)
            self.custframe=tk.Frame(self)
            self.custframe.grid(row=20, column=15, columnspan=3, rowspan=11, sticky='nsew')

            tk.Button(self.custframe, text='Save fit', command=self.save_fit).grid(row=0, column=1)
            tk.Button(self.custframe, text='Import fit', command=self.import_fit,width=6).grid(row=0,column=0) 
            tk.Button(self.custframe, text="Fit chi", command=self.fit_chi, width=6).grid(row=1, column=1)
            tk.Label(self.custframe,text='Min').grid(row=1,column=2)
            tk.Label(self.custframe,text='Max').grid(row=1,column=3)
            tk.Label(self.custframe,text="\u03B3").grid(row=2,column=0)
            self.entryGamma=tk.Entry(self.custframe,width=10)
            self.entryGamma.insert(0,'0')
            self.entryGamma.grid(row=2, column=1)
            
            self.entryGaMin=tk.Entry(self.custframe,width=10)
            self.entryGaMin.insert(0,'0')
            self.entryGaMin.grid(row=2,column=2)
            self.entryGaMax=tk.Entry(self.custframe,width=10)
            self.entryGaMax.insert(0,'0')
            self.entryGaMax.grid(row=2,column=3)
            
            tk.Label(self.custframe,text="\u03B1").grid(row=3,column=0)
            self.entryAlpha=tk.Entry(self.custframe,width=10)
            self.entryAlpha.insert(0, '0')
            self.entryAlpha.grid(row=3,column=1)

            self.entryAlMin=tk.Entry(self.custframe,width=10)
            self.entryAlMin.insert(0,'0')
            self.entryAlMin.grid(row=3,column=2)
            self.entryAlMax=tk.Entry(self.custframe,width=10)
            self.entryAlMax.insert(0,'0')
            self.entryAlMax.grid(row=3,column=3)
            
            tk.Label(self.custframe,text="K\u0075").grid(row=4,column=0)
            self.entryKu=tk.Entry(self.custframe,width=10)
            self.entryKu.insert(0,'0')
            self.entryKu.grid(row=4,column=1)

            self.entryKuMin=tk.Entry(self.custframe,width=10)
            self.entryKuMin.insert(0,'0')
            self.entryKuMin.grid(row=4,column=2)
            self.entryKuMax=tk.Entry(self.custframe,width=10)
            self.entryKuMax.insert(0,'0')
            self.entryKuMax.grid(row=4,column=3)
            
            tk.Label(self.custframe,text='K\u0073').grid(row=5,column=0)
            self.entryKs=tk.Entry(self.custframe,width=10)
            self.entryKs.insert(0,'0')
            self.entryKs.grid(row=5,column=1)

            #self.entryKsMin=tk.Entry(self.custframe,width=10)
            #self.entryKsMin.insert(0,'0')
            #self.entryKsMin.grid(row=5,column=2)
            #self.entryKsMax=tk.Entry(self.custframe,width=10)
            #self.entryKsMax.insert(0,'0')
            #self.entryKsMax.grid(row=5,column=3)

            tk.Label(self.custframe,text='K1').grid(row=6,column=0)
            self.entryK1=tk.Entry(self.custframe,width=10)
            self.entryK1.insert(0,'0')
            self.entryK1.grid(row=6,column=1)
            self.entryK1Min=tk.Entry(self.custframe,width=10)
            self.entryK1Min.insert(0,'0')
            self.entryK1Min.grid(row=6,column=2)
            self.entryK1Max=tk.Entry(self.custframe,width=10)
            self.entryK1Max.insert(0,'0')
            self.entryK1Max.grid(row=6,column=3)


            tk.Label(self.custframe,text='M\u0073').grid(row=7,column=0)
            self.entryMs=tk.Entry(self.custframe,width=10)
            self.entryMs.insert(0,'0')
            self.entryMs.grid(row=7,column=1)

            self.entryMsMin=tk.Entry(self.custframe,width=10)
            self.entryMsMin.insert(0,'0')
            self.entryMsMin.grid(row=7,column=2)
            self.entryMsMax=tk.Entry(self.custframe,width=10)
            self.entryMsMax.insert(0,'0')
            self.entryMsMax.grid(row=7,column=3)
            tk.Label(self.custframe,text='Shift').grid(row=8,column=0)
            self.entryShift=tk.Entry(self.custframe,width=10)
            self.entryShift.insert(0,'0')
            self.entryShift.grid(row=8,column=1)
            self.entryShiftMin=tk.Entry(self.custframe,width=10)
            self.entryShiftMin.insert(0,'0')
            self.entryShiftMin.grid(row=8,column=2)
            self.entryShiftMax=tk.Entry(self.custframe,width=10)
            self.entryShiftMax.insert(0,'0')
            self.entryShiftMax.grid(row=8,column=3)
            tk.Label(self.custframe,text='\u03C6'+'u').grid(row=9,column=0)
            self.entryPhu=tk.Entry(self.custframe,width=10)
            self.entryPhu.insert(0,'0')
            self.entryPhu.grid(row=9,column=1)
            self.entryPhuMin=tk.Entry(self.custframe,width=10)
            self.entryPhuMin.insert(0,'0')
            self.entryPhuMin.grid(row=9,column=2)
            self.entryPhuMax=tk.Entry(self.custframe,width=10)
            self.entryPhuMax.insert(0,'0')
            self.entryPhuMax.grid(row=9,column=3)
            tk.Button(self.custframe, text='Export report', command=self.exportPdf).grid(row=10,column=0)

            self.varLeastsq, self.varShgo=tk.IntVar(self), tk.IntVar(self)
            self.Leastsq=tk.Checkbutton(self.custframe, text="Leastsq", variable=self.varLeastsq,command=lambda: self.set_checkfit(2)).grid(row=10, column=1)
            self.Shgo=tk.Checkbutton(self.custframe, text="Shgo", variable=self.varShgo,command=lambda: self.set_checkfit(3)).grid(row=10,column=2)
            self.varLeastsq.set(1)
            tk.Button(self.custframe, text='Resize', command=self.fit_chi).grid(row=11,column=0)
            self.entryLower=tk.Entry(self.custframe,width=5)
            self.entryLower.insert(0,'0')
            self.entryLower.grid(row=11,column=1)
            self.entrySuperior=tk.Entry(self.custframe,width=5)
            self.entrySuperior.insert(0,'0')
            self.entrySuperior.grid(row=11, column=2)

            for i in np.arange(0,11):
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
        if self.titlevar.get()==1:
            self.ax.set_title(self.titleentry.get())
        if self.custvar.get()==1:
            self.legendliststr=[]
            for i in range(0,self.n):
                for n in range(0,1):
                    self.legendliststr.append(self.legendlist[i].get().split('.dat')[0].replace('_',' ').replace(' batch','')+' Re($\chi$)')
                    self.legendliststr.append(self.legendlist[i].get().split('.dat')[0].replace('_',' ').replace(' batch','')+' Im($\chi$)')

            self.ax.legend(self.legendliststr)

        self.ax.set_xlabel('$f$ [Hz]')
        self.ax.set_ylabel(selected +' [$\Omega$]')
        for item in plotlist:
            texti=pd.read_csv(item, index_col=False, comment= "#", sep='\t', engine='python')
            if selected == 'angle':
                self.ax=plt.subplot(projection='rectilinear')
                self.ax.set_xlabel('$\Theta$ [°]')
                self.ax.set_ylabel('$\omega_r  [rad/s]$')

                field=np.loadtxt(item,usecols=[0], dtype='str', skiprows=1, delimiter='\t')
                resonance=np.loadtxt(item, usecols=[2], skiprows=1, delimiter='\t')
                angle=np.array([float(i.split('_')[-1].split('G')[0]) for i in field])
                H=float(field[0].split('_')[-2].split('G')[0])
                #print(H)
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
                self.ax=plt.subplot(projection='polar')
                field=np.loadtxt(plotlist[0],usecols=[0], dtype='str', skiprows=1, delimiter='\t')
                resonance=np.loadtxt(plotlist[0], usecols=[2], skiprows=1, delimiter='\t')
                field=np.array([float(i.split('_')[-1].split('G')[0]) for i in field])
                self.ax.plot(field*np.pi/180,resonance/max(resonance),'*')
                self.ax.grid(True)
                self.ax.set_ylim(bottom=min(resonance/max(resonance)))

            elif selected=='4-fold':
                self.ax.set_xlabel('$\Theta$ [rad]')
                self.ax.set_ylabel('$\omega_r [rad/s]$')
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

            elif selected == 'ku':
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
                    Y=(H+4*np.pi*M+(2*ku/M)*np.cos(x+shift)**2+4*K_s/(d*M))*(H+2*ku*np.cos(2*(x+shift))/M)
                    resids = (Y-y)**2

                    return resids
                params = Parameters()
                if float(self.entryKu.get())!=0:
                    params.add('ku', value=float(self.entryKu.get()))
                else:
                    params.add('ku', value=4000)
                params.add('shift', value=float(self.entryShift.get()))
                if float(self.entryShiftMin.get())!=0:
                    params.add('shift', value=float(self.entryShift.get()),min=float(self.entryShiftMin.get()),max=float(self.entryShiftMax.get()))

                minner = Minimizer(fcn2min, params, fcn_args = (angle,(resonance/gamma)**2))
                result = minner.minimize()
                report_fit(result)
                
                self.ax.clear()
                self.ax.set_xlabel('$\Theta [rad]$')
                self.ax.set_ylabel('($\omega/\gamma$)^2')
                self.ax.plot(angle, (resonance/gamma)**2,'*')
                angles=np.arange(min(angle),max(angle),np.pi/500) 
                Y=(H+4*np.pi*M+(2*result.params['ku']/M)*np.cos(angles+result.params['shift'].value)**2+4*K_s/(d*M))*(H+2*result.params['ku']*np.cos(2*(angles+result.params['shift'].value))/M)
                self.ax.plot(angles, Y)
                self.entryKu.delete(0,"end")
                self.entryKu.insert(0,result.params['ku'].value)
                self.entryShift.delete(0,"end")
                self.entryShift.insert(0, result.params['shift'].value)

            elif selected == 'Cubic Kohmoto (100) + uni':
                field=np.loadtxt(plotlist[0],usecols=[0], dtype='str', skiprows=1, delimiter='\t')
                resonance=np.loadtxt(plotlist[0], usecols=[2], skiprows=1, delimiter='\t')
                field=np.array([float(i.split('_')[-1].split('G')[0]) for i in field])
                angle=field*np.pi/180
                
                M=float(self.entryMs.get())
                H=float(plotlist[0].split('_')[-2].split('G')[0])
                gamma=float(self.entryGamma.get())
                
                def fcn2min(params, phi, y):
                    K1=params['K1']
                    #K2=params['K2']
                    Ku1=params['Ku1']
                    shift=params['shift']
                    a=H+2*(K1/M)*np.cos(4*(phi+shift))+2*(Ku1/M)*np.cos(2*(phi+shift))
                    b=H+4*np.pi*M+(K1/(2*M))*(3+np.cos(4*(phi+shift)))+2*(Ku1/M)*np.cos(phi+shift)**2
                    #(K2/(2*M))*np.sin(2*(phi+shift))**2
              
                    Y=a*b
                    resids = (Y-y)**2

                    return resids
                params = Parameters()
                if float(self.entryK1.get())!=0:
                    params.add('K1', value=float(self.entryK1.get()))
                else:
                    params.add('K1', value=4000)
                params.add('shift', value=float(self.entryShift.get()))
                if float(self.entryKu.get())!=0:
                    params.add('Ku1', value=float(self.entryKu.get()))
                else:
                    params.add('Ku1',value=4000)

                if float(self.entryShiftMin.get())!=0:
                    params.add('shift', value=float(self.entryShift.get()),min=float(self.entryShiftMin.get()),max=float(self.entryShiftMax.get()))
                if float(self.entryK1Min.get())!=0:
                    params.add('K1', value=float(self.entryK1.get()), min=float(self.entryK1Min.get()), max=float(self.entryK1Max.get()))
                if float(self.entryKuMin.get())!=0:
                    params.add('Ku1', value=float(self.entryKu.get()), min=float(self.entryKuMin.get()), max=float(self.entryKuMax.get()))
                    
                minner = Minimizer(fcn2min, params, fcn_args = (angle,(resonance/gamma)**2))
                result = minner.minimize()
                report_fit(result)
                
                self.ax.clear()
                self.ax.set_xlabel('$\Theta [rad]$')
                self.ax.set_ylabel('($\omega/\gamma$)^2')
                self.ax.plot(angle, (resonance/gamma)**2,'*')
                phi=np.arange(min(angle),max(angle),np.pi/500)
                shift=result.params['shift'].value
                K1=result.params['K1'].value
                Ku1=result.params['Ku1'].value
                a=H+2*(K1/M)*np.cos(4*(phi+shift))+2*(Ku1/M)*np.cos(2*(phi+shift))
                b=H+4*np.pi*M+(K1/(2*M))*(3+np.cos(4*(phi+shift)))+2*(Ku1/M)*np.cos(phi+shift)**2
                Y=a*b
                self.ax.plot(phi, Y)
                self.entryKu.delete(0,"end")
                self.entryKu.insert(0,result.params['Ku1'].value)
                self.entryShift.delete(0,"end")
                self.entryShift.insert(0, result.params['shift'].value)
                self.entryK1.delete(0,"end")
                self.entryK1.insert(0,result.params['K1'].value)
			
            elif selected == 'Cubic Kohmoto (110)':
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
                self.ax.set_xlabel('$\Theta [rad]$')
                self.ax.set_ylabel('($\omega/\gamma$)^2')
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
                self.ax.set_xlabel('$\Theta [rad]$')
                self.ax.set_ylabel('($\omega/\gamma$)^2')
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

            elif selected == 'Ku':
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
                self.ax.set_xlabel('cos($ \Theta$ )^2')
                self.ax.set_ylabel('$\omega ^2 [rad^2/s^2]$')
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

            elif selected == 'EA':
                field=np.loadtxt(plotlist[0],usecols=[0], dtype='str', skiprows=1, delimiter='\t')
                resonance=np.loadtxt(plotlist[0], usecols=[2], skiprows=1, delimiter='\t')
                field=np.array([float(i.split('_')[-1].split('G')[0]) for i in field])
                H=field
                M=float(self.entryMs.get())
                Ku=float(self.entryKu.get())
                b=4*np.pi*M-4*Ku/M
                c=(4*np.pi*M-2*Ku/M)*(2*Ku/M)
                x=H**2+H*b+c

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

            else:
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
            self.titleentry.destroy()

    def shift(self):
        if self.shiftvar.get()==1:
            self.shiftentry=tk.Entry(self.editframe, width=5)
            self.shiftentry.grid(row=6,column=12)
        else:
            self.shiftentry.destroy()
    
    def custom(self):
        
        if self.custvar.get()==1:
            print('reyna')
            try:
                self.n=len(self.listboxopen.curselection())
            except:
                self.n=0

            self.customframe=tk.Frame(self.editframe)
            self.customframe.grid(row=7,column=12, columnspan=1,rowspan=9,sticky='nes')
            self.legendlist=[]
            for i in range(0, self.n):
                
                entr = tk.Entry(self.customframe, width=18)
                entr.grid(row=i,column=0)
                entr.insert(0,self.filelist[self.listboxopen.curselection()[i]].split("/")[-1].split('.dat')[0].replace('_',' ').replace(' batch',''))
                self.legendlist.append(entr)
                self.customframe.rowconfigure(i,weight=1)
            print(self.legendlist)
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
    import vxi11 as vx 
    inst= vx.Instrument("192.168.48.200")
    inst.write("*RST")
    inst.write("CALC2:PAR:SDEF 'Trc2', 'S11'")
    inst.write("DISP:WIND2:STAT ON; TRAC:FEED 'Trc2'")
    inst.write("DISP:WIND:STAT OFF")
    inst.write("INIT:CONT:ALL OFF")
    inst.write("FREQ:STAR 50e6; STOP 4e9")
    nave=10
    savelist=[]
    nfpoints=10
except:
    nfpoints=10
    print('Network analyser is not responding')

# Comedi setup, configuration for read and write
dev=None
try:
    import comedi
    subdevr, chanr, rngr, aref = 0, 0, 1, comedi.AREF_GROUND
    subdevw, chanw, chanw1, rngw, = 1, 0, 1, 0
    datazero, datawmax = 2048, 4095
    devname="/dev/comedi0"
    dev = comedi.comedi_open(devname)
    path = f=open('/home/at/FMR/magnari/Mælingar/calib_results.dat')
    lines = (line for line in f if not line.startswith('#'))
    FH = np.loadtxt(lines)
    path = f=open('/home/at/FMR/magnari/Mælingar/calib_results_Ls.dat')
    lines = (line for line in f if not line.startswith('#'))
    FH1 = np.loadtxt(lines)
    #dev = comedi.comedi_open("/dev/comedi0")
    ranger = comedi.comedi_get_range(dev, subdevr, chanr, rngr)
except:
    print('Magnet not responding')
if __name__=='__main__':
    app = App()
    #app.tk.call('tk_getOpenFile','-foobarbaz')
    #app.tk.call('set','::tk::dialog::file:showHiddenBtn','0')
    #app.tk.call('set','::tk::dialog::file::showHiddenVar','0')
    app.mainloop()
