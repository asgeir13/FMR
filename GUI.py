import time
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
from tkinter.constants import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import pyvisa
import pandas as pd
import datetime
from scipy import signal, optimize
import math
from astropy import modeling
from lmfit.models import GaussianModel, LorentzianModel
import cmath
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
        for F in (StartPage, Calibrate, Batch, Viewer2):

            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row = 0, column = 0, sticky="nsew")

        self.show_frame(Viewer2)
        #raises the page to the top with tkraise()
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
        

    #this is the main page
class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
       
        self.buttonframe=tk.Frame(self)
        self.buttonframe.grid(row=0,column=2,rowspan=2, columnspan=2,sticky='wn')
        tk.Button(self.buttonframe, text="Measure", command=lambda: controller.show_frame(StartPage), width=8, height=1).grid(row=0,column=0,padx=5)
        tk.Button(self.buttonframe, text="Viewer", command=lambda: controller.show_frame(Viewer2), width=8, height=1).grid(row=0,column=1)
        tk.Button(self.buttonframe, text="Batch", command=lambda: controller.show_frame(Batch), width=8, height=1).grid(row=1, column=0, sticky='n', padx=5)
        tk.Button(self.buttonframe, text="Calibrate", command=lambda: controller.show_frame(Calibrate), width=8, height=1).grid(row=1,column=1, sticky='n')
        self.buttonframe.columnconfigure(0,weight=1)
        self.buttonframe.columnconfigure(1,weight=1)
        tk.Button(self, text="Exit", command=self._quit).grid(row=0, column=10,sticky='ne')

        self.fig = plt.figure(constrained_layout=False, figsize=[10,9])
        gs1 = self.fig.add_gridspec(nrows=1, ncols=2, left=0.1, right=0.95, wspace=0.3)
        self.ax = self.fig.add_subplot(gs1[0,0])
        self.ax1 = self.fig.add_subplot(gs1[0,1])
        self.ax.set_xlabel('$f$ [Hz]')
        self.ax1.set_xlabel('$f$ [Hz]')
        self.ax.set_ylabel('S11 resistance [$\Omega$]')
        self.ax1.set_ylabel('S11 reactance [$\Omega$]')
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().grid(row=0, column=0, rowspan=100,columnspan=2,sticky='nswe')
        self.canvas.draw_idle()
        self.toolbarframe=tk.Frame(self)
        self.toolbarframe.grid(row=101, column=0, sticky='nwe')
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.toolbarframe)
        self.toolbar.grid(row=102, column=0, sticky='nwe')
        
        self.scanframe=tk.Frame(self)
        self.scanframe.grid(row=2,column=4,rowspan=7,columnspan=6,sticky='ne')
        tk.Button(self.scanframe, text="Scan", command=self.takecal).grid(row=4, column=0, sticky='e')
        tk.Button(self.scanframe, text="Save", command=self.file_save).grid(row=4, column=1)
        
        tk.Button(self.scanframe, text="Stop", command=self.stop_run).grid(row=4, column=2)
        tk.Button(self.scanframe, text="Calibrate IF", command=self.cal).grid(row=5, column=1,columnspan=2)
        tk.Label(self.scanframe, text="Set magnetic field").grid(row=0, column=0)
        tk.Label(self.scanframe, text="Parallel").grid(row=1,column=0)
        
        self.entrypar = tk.Entry(self.scanframe,width=5)
        self.entrypar.insert(0, "0")
        self.entrypar.grid(row=1, column=1)
        tk.Label(self.scanframe, text="G ").grid(row=1, column=2, sticky='w')

        tk.Label(self.scanframe, text="Perpendicular").grid(row=2,column=0)
        self.entryper = tk.Entry(self.scanframe,width=5)
        self.entryper.insert(0, "0")
        self.entryper.grid(row=2, column=1)
        tk.Label(self.scanframe, text="G ").grid(row=2, column=2,sticky='w')
        
        tk.Label(self.scanframe, text="Magnitude").grid(row=1, column=3)
        self.entrymag = tk.Entry(self.scanframe, width=5)
        self.entrymag.insert(0, "0")
        self.entrymag.grid(row=1, column=4, sticky='e')
        tk.Label(self.scanframe, text="G").grid(row=1, column=5, sticky='w')
        tk.Label(self.scanframe, text="Angle").grid(row=2, column=3)
        self.entryang = tk.Entry(self.scanframe, width=5)
        self.entryang.insert(0, "0")
        self.entryang.grid(row=2, column=4, sticky='e')
        tk.Label(self.scanframe, text="°").grid(row=2, column=5, sticky='w')

        tk.Button(self.scanframe, text="Reset", command=self.zerofield).grid(row=3, column=2)
        tk.Button(self.scanframe, text="Set", command=self.writevolt).grid(row=3, column=1)
        for i in np.arange(0,9):
            #self.rowconfigure(i, weight=1)
            self.columnconfigure(i,weight=1)

        for i in range(0,5):
            self.scanframe.rowconfigure(i,weight=1)

    def _quit(self):
        app.quit()
        app.destroy()
    
    def stop_run(self):
        self.run=False

    def cal(self):
       inst.write("HCT")

        #saves all the arrays, filedialog.asksaveasfile creates pop up save window
    def file_save(self):
        f = tk.filedialog.asksaveasfile(mode="w", defaultextension="*.txt")
        intro="#FMR data, this file includes calibration measurements, correction factor and corrected S11\n"
        intro1="freq\tS11a\tS11m\tS11o\tS11l\tS11s\tZa\tEdf\tErf\tEsf\n"
        dataout=np.column_stack((self.freq, self.S11a, self.S11m, S11o, S11l, S11s, self.Za, Edf, Erf, Esf))
        #write the two headers and then writing the array dataout with a double for-loop
        f.write(intro)
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
        print(f'1 of {nave+1} scans complete')
        for n in range(nave):  #averaging
            if self.run==False:
                break
            
            if (n % 2)==0:
                colour='b'
            else:
                colour='g'

            real_p, imag_p, self.freq=self.measure()
            self.S11m=(self.S11m*(n+1)+real_p+1j*imag_p)/(n+2) #averaging with each iteration
            self.docal()
            self.ax.clear()
            self.ax1.clear()
            self.ax.set_xlabel('$f$ [Hz]')
            self.ax1.set_xlabel('$f$ [Hz]')
            self.ax.set_ylabel('$Z_a$ resistance [$\Omega$]')
            self.ax1.set_ylabel('$Z_a$ reactance [$\Omega$]')
            self.ax.plot(self.freq, self.Za.real, colour)
            self.ax1.plot(self.freq, self.Za.imag, colour)
            self.canvas.draw_idle() #draw_idle is a gentle way to draw, it doesn't interupt the GUI
            self.canvas.flush_events()

            print(f'{n+2} of {nave+1} scans complete')
        print('Measurement complete')

        #receiving measurements from the network analyzer
    def measure(self):
        inst.write("TRS;WFS")   #TRS triggers a scan and WFS is wait for sweep
        inst.write('*OPC?')     #*OPC? askes if WFS is finished, thus avoiding reading the old buffer
        c=True
        while c:    #waiting for sweep
            val=0
            try:
                val=inst.read()
                c=False
            except:
                time.sleep(0.005)      
        
        inst.write("OFV") #requesting the frequency values
        freq=inst.read("\n")
        freq=freq.rsplit(", ")
        freq1=freq[0].rsplit(" ")
        freq1.extend(freq[1:])
        freq=[float(n) for n in freq1[1:]]

        inst.write("OFD") #requesting the S11 measurements, this returns the real and imag part
        valu=inst.read("\n")
        valu=valu.rsplit(",")
        valu1=valu[0].rsplit(" ")
        if len(valu1)==1:
            valu1=valu[0].rsplit("-")
            valu1[1]='-'+valu1[1]
            if len(valu1)==3:
                valu1[1]=valu1[1]+'-'+valu1[2]
            
        valu1=[valu1[1]]
        valu1.extend(valu[1:])
        valu=[float(n) for n in valu1]
        real=imag=np.arange(len(freq),dtype=np.float64)

        real=np.array(valu[0:-1:2]) #the complex values are given in pairs
        imag=valu[1:-1:2]
        imag.append(valu[-1])
        imag=np.array(imag)
        return real, imag, freq

        #set the magnetic field. FH are values read from a calibration file, which can be updated 
    def writevolt(self):
        dev = comedi.comedi_open("/dev/comedi0")

        val = self.entrypar.get()
        val1 = self.entryper.get()
        if int(val)==0 and int(val1)==0:
            mag = int(self.entrymag.get())
            ang = int(self.entryang.get())
            val, val1=mag*np.cos(ang*np.pi/180), mag*np.sin(ang*np.pi/180)
            print('mag/ang')
              
        val, val1 = float(val)*FH1[0]+FH1[1], float(val1)*FH[0]+FH[1]
        val, val1 = int(np.around(val)), int(np.around(val1))
        if val < 0 and val > 4095 and val1<0 and val1 > 4095:
            val, val1 = datazero, datazero
            print('Input value not available')
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
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().grid(row=0, column=0, rowspan=100, columnspan=10, sticky='nswe')
        self.canvas.draw_idle()
        self.toolbarframe=tk.Frame(self)
        self.toolbarframe.grid(row=101, column=0, columnspan=10, sticky='nwe')
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.toolbarframe)
        self.toolbar.grid(row=102, column=0, columnspan=10, sticky='nwe')
        
        self.buttonframe=tk.Frame(self)
        self.buttonframe.grid(row=0,column=11, columnspan=2,rowspan=2,sticky='wn')
        tk.Button(self.buttonframe, text="Measure", command=lambda: controller.show_frame(StartPage), width=8, height=1).grid(row=0,column=0,padx=5)
        tk.Button(self.buttonframe, text="Viewer", command=lambda: controller.show_frame(Viewer2), width=8, height=1).grid(row=0,column=1)
        tk.Button(self.buttonframe, text="Batch", command=lambda: controller.show_frame(Batch), width=8, height=1).grid(row=1, column=0, sticky='n', padx=5)
        tk.Button(self.buttonframe, text="Calibrate", command=lambda: controller.show_frame(Calibrate), width=8, height=1).grid(row=1,column=1, sticky='n')
        self.buttonframe.columnconfigure(0,weight=1)
        self.buttonframe.columnconfigure(1,weight=1)
        tk.Button(self, text="Exit", command=self._quit).grid(row=0, column=18, sticky='e')

        tk.Button(self, text="Scan", command=self.takecal).grid(row=2, column=13)
        self.listbox=tk.Listbox(self, height=2, width=5)
        self.listbox.grid(row=2,column=14)
        elements=['Open', 'Load', 'Short']
        for i, ele in enumerate(elements):
            self.listbox.insert(i, ele)

        tk.Button(self, text="save", command=self.save).grid(row=2,column=15, columnspan=2)
        
        tk.Label(self, text="Set magnetic field",relief='ridge').grid(row=3, column=13)
        
        tk.Label(self, text="Parallel").grid(row=4,column=13)
        self.entrypar = tk.Entry(self,width=5)
        self.entrypar.insert(0, "0")
        self.entrypar.grid(row=4, column=14)
        tk.Label(self, text="G").grid(row=4, column=15,sticky='w')

        tk.Label(self, text="Perpendicular").grid(row=5,column=13)
        self.entryper = tk.Entry(self,width=5)
        self.entryper.insert(0, "0")
        self.entryper.grid(row=5, column=14)
        tk.Label(self, text="G").grid(row=5, column=15,sticky='w')

        tk.Label(self, text="Magnitude").grid(row=4, column=16)
        self.entrymag = tk.Entry(self, width=5)
        self.entrymag.insert(0, "0")
        self.entrymag.grid(row=4, column=17, sticky='e')
        tk.Label(self, text="G").grid(row=4, column=18, sticky='w')
        tk.Label(self, text="Angle").grid(row=5, column=16)
        self.entryang = tk.Entry(self, width=5)
        self.entryang.insert(0, "0")
        self.entryang.grid(row=5, column=17, sticky='e')
        tk.Label(self, text="°").grid(row=5, column=18, sticky='w')

        tk.Button(self, text="Reset", command=self.zerofield).grid(row=7, column=17)
        tk.Button(self, text="Set", command=self.writevolt, width=2).grid(row=7, column=16, sticky='e')
        
        self.sweepframe=tk.Frame(self)
        self.sweepframe.grid(row=9,column=13,columnspan=4,rowspan=13)
        tk.Label(self.sweepframe, text="Sweep setup", relief='ridge').grid(row=0, column=0)
        

        tk.Label(self.sweepframe, text="Start").grid(row=1, column=0)
        self.startentry=tk.Entry(self.sweepframe, width=5)
        self.startentry.insert(0, "40")
        self.startentry.grid(row=1, column=1)
        tk.Label(self.sweepframe, text="MHz").grid(row=1, column=2)

        tk.Label(self.sweepframe, text="Stop").grid(row=2, column=0)
        self.stopentry=tk.Entry(self.sweepframe, width=5)
        self.stopentry.insert(0, "10000")
        self.stopentry.grid(row=2, column=1)
        tk.Label(self.sweepframe, text="MHz").grid(row=2, column=2)

        tk.Label(self.sweepframe, text="Nr. of meas.").grid(row=3, column=0)
        self.numberentry=tk.Entry(self.sweepframe, width=5)
        self.numberentry.insert(0, "10")
        self.numberentry.grid(row=3, column=1)

        tk.Label(self.sweepframe, text="Data points").grid(row=4,column=0)
        self.pointsbox=tk.Entry(self.sweepframe, width=6)
        self.pointsbox.insert(0, "401")
        self.pointsbox.grid(row=4, column=1)
        self.pointlist=["51", "101", "201", "401", "801", "1601"]
        tk.Button(self.sweepframe, text="+", command=lambda: self._up(0)).grid(row=4, column=3)
        tk.Button(self.sweepframe, text="-", command=lambda: self._down(0)).grid(row=4,column=2)

        tk.Label(self.sweepframe, text="IF BW").grid(row=5, column=0)
        self.IF_list=["10 Hz", "100 Hz", "1 kHz", "10 kHz"]
        self.IF_BW=tk.Entry(self.sweepframe,width=6)
        self.IF_BW.insert(0,"1 kHz")
        self.IF_BW.grid(row=5, column=1)
        tk.Button(self.sweepframe, text="+", command=lambda: self._up(1)).grid(row=5, column=3)
        tk.Button(self.sweepframe, text="-", command=lambda: self._down(1)).grid(row=5,column=2)
        tk.Button(self, text="Set values", command=self.set_values).grid(row=11, column=16, columnspan=3)
        tk.Button(self, text="Calibrate IF", command=self.cal).grid(row=10, column=16, columnspan=3)
        
        for i in range(0,5):

            self.sweepframe.columnconfigure(i, weight=1)
            #self.sweepframe.rowconfigure(i, weight=1)
        
        for i in np.arange(0,102):
            self.rowconfigure(i, weight=1)

        for i in range(0,18):
            self.columnconfigure(i,weight=1)
    
    def _up(self,dex):
        if dex==1:
            if self.IF_BW.get()=="10 kHz":
                print("At max")
            else:
                index=self.IF_list.index(self.IF_BW.get())
                self.IF_BW.delete(0, END)
                self.IF_BW.insert(0, self.IF_list[index+1])
        elif dex==0:
            if self.pointsbox.get()=="1601":
                print("At max")
            else:
                index=self.pointlist.index(self.pointsbox.get())
                self.pointsbox.delete(0, END)
                self.pointsbox.insert(0, self.pointlist[index+1])

    def _down(self,dex):
        if dex==1:
            
            if self.IF_BW.get()=="10 Hz":
                print("At min")
            else:
                index= self.IF_list.index(self.IF_BW.get())
                self.IF_BW.delete(0, END)
                self.IF_BW.insert(0, self.IF_list[index-1])
        elif dex==0:
            if self.pointsbox.get()=="51":
                print("At min")
            else:
                index=self.pointlist.index(self.pointsbox.get())
                self.pointsbox.delete(0, END)
                self.pointsbox.insert(0, self.pointlist[index-1])
    
        #save each measurement to it's corresponding variable
    def save(self):
        global S11o, S11l, S11s
        number=self.listbox.curselection()[0]
        if number == 0:
            if "S11o" in savelist:
                print('Replacing prior calibration')
                S11o=self.S11m
            else:
                S11o=self.S11m
                savelist.append("S11o")
                print("S11o has been saved")
                print(savelist)
        elif number == 1:
            if 'S11l' in savelist:
                print('Replacing prior calibration')
                S11l=self.S11m
            else:
                S11l=self.S11m
                savelist.append("S11l")
                print(savelist)
                print("S11l has been saved")
        elif number == 2:
            if 'S11s' in savelist:
                print('Replacing prior calibration')
                S11s=self.S11m
            else:
                S11s=self.S11m
                savelist.append("S11s")
                print(savelist)
                print("S11s has been saved")
        elif number == 3:
            if "S11o" not in savelist:
                print("Perform calibration for OPEN")
            elif "S11l" not in savelist:
                print("Perform calibration for LOAD")
            elif "S11s" not in savelist:
                print("Perform calibration for SHORT")
            else:
                print("S11m has been saved")
        else:
            print("Write in the entry which calibration took place!")

    def _quit(self):
        app.quit()
        app.destroy()

    def set_values(self):
        global nave, nfpoints
        start=self.startentry.get()
        stop=self.stopentry.get()
        start="SRT "+start+" MHz"
        stop="STP "+stop+" MHz"
        inst.write(start)
        inst.write(stop)
        #set IF_BW value
        inst.write("IF"+str(int(self.IF_list.index(self.IF_BW.get())+1)))
        #number of data points set, 
        inst.write("NP"+self.pointsbox.get())
        nfpoints=int(self.pointsbox.get())

        nave=int(self.numberentry.get())-1

        #set the magnetic field. FH are values read from a calibration file, which can be updated 
    def writevolt(self):
        dev = comedi.comedi_open("/dev/comedi0")

        val = self.entrypar.get()
        val1 = self.entryper.get()
        if int(val)==0 and int(val1)==0:
            mag = int(self.entrymag.get())
            ang = int(self.entryang.get())
            val, val1=mag*np.cos(ang*np.pi/180), mag*np.sin(ang*np.pi/180)
            print('mag/ang')

        val, val1 = float(val)*FH1[0]+FH1[1], float(val1)*FH[0]+FH[1]
        val, val1 = int(np.around(val)), int(np.around(val1))
        if val < 0 and val > 4095 and val1<0 and val1 > 4095:
            val, val1 = datazero, datazero
            print('Input value not available')
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
        comedi.comedi_close(dev)

    def cal(self):
       inst.write("HCT") #trigger a IF calibration, automatic calibration is turned off 

        #receiving measurements from the network analyzer
    def measure(self):
        inst.write("TRS;WFS")
        inst.write('*OPC?')
        c=True
        while c:
            val=0
            try:
                val=inst.read()
                c=False
            except:
                time.sleep(0.01)
        inst.write("OFV") #requesting the frequency values
        freq=inst.read("\n")
        freq=freq.rsplit(", ")
        freq1=freq[0].rsplit(" ")
        freq1.extend(freq[1:])
        freq=[float(n) for n in freq1[1:]]
        
        inst.write("OFD") #requesting the S11 measurements, this returns the real and imag part
        valu=inst.read("\n")
        valu=valu.rsplit(",")
        valu1=valu[0].rsplit(" ")
        if len(valu1)==1:
            valu1=valu[0].rsplit("-")
            valu1[1]='-'+valu1[1]
            if len(valu1)==3:
                valu1[1]=valu1[1]+'-'+valu1[2]
            
        valu1=[valu1[1]]
        valu1.extend(valu[1:])
        valu=[float(n) for n in valu1]
        real=imag=np.arange(len(freq),dtype=np.float64)

        real=np.array(valu[0:-1:2]) #the complex values are given in pairs
        imag=valu[1:-1:2]
        imag.append(valu[-1])
        imag=np.array(imag)
        return real, imag, freq

        #this function measures multiple times by calling the measure funtion, it is called nave times
        #which is the number of averages
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
        print(f'1 of {nave+1} scans complete')
        for n in range(nave):
            if (n % 2)==0:
                colour='c'
            else:
                colour='g'
            
            real_p, imag_p, self.freq=self.measure()
            self.S11m=(self.S11m*(n+1)+real_p+1j*imag_p)/(n+2) #averaging with each iteration
            self.ax.clear()
            self.ax1.clear()
            self.ax.set_xlabel('$f$ [Hz]')
            self.ax1.set_xlabel('$f$ [Hz]')
            self.ax.set_ylabel('S11 resistance [$\Omega$]')
            self.ax1.set_ylabel('S11 reactance [$\Omega$]')
            self.ax.plot(self.freq, self.S11m.real, colour)
            self.ax1.plot(self.freq, self.S11m.imag, colour)
            self.canvas.draw_idle() #draw_idle is a gentle way to draw, it doesn't interupt the GUI
            self.canvas.flush_events()
            print(f'{n+2} of {nave+1} scans complete')
        print('Measurement complete')   


class Batch(tk.Frame):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)
        self.buttonframe=tk.Frame(self)
        self.buttonframe.grid(row=0,column=11, columnspan=2,rowspan=2,sticky='wn')
        tk.Button(self.buttonframe, text="Measure", command=lambda: controller.show_frame(StartPage), width=8, height=1).grid(row=0,column=0,padx=5)
        tk.Button(self.buttonframe, text="Viewer", command=lambda: controller.show_frame(Viewer2), width=8, height=1).grid(row=0,column=1)
        tk.Button(self.buttonframe, text="Batch", command=lambda: controller.show_frame(Batch), width=8, height=1).grid(row=1, column=0, sticky='n', padx=5)
        tk.Button(self.buttonframe, text="Calibrate", command=lambda: controller.show_frame(Calibrate), width=8, height=1).grid(row=1,column=1, sticky='n')
        self.buttonframe.columnconfigure(0,weight=1)
        self.buttonframe.columnconfigure(1,weight=1)
        tk.Button(self, text="Exit", command=self._quit).grid(row=0, column=18,sticky='e')

        self.fig = plt.figure(constrained_layout=False, figsize=[10,9])
        gs1 = self.fig.add_gridspec(nrows=1, ncols=2, left=0.1, right=0.95, wspace=0.3)
        self.ax = self.fig.add_subplot(gs1[0,0])
        self.ax1 = self.fig.add_subplot(gs1[0,1])
        self.ax.set_xlabel('$f$ [Hz]')
        self.ax1.set_xlabel('$f$ [Hz]')
        self.ax.set_ylabel('S11 resistance [$\Omega$]')
        self.ax1.set_ylabel('S11 reactance [$\Omega$]')
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().grid(row=0, column=0, rowspan=100, columnspan=10, sticky='nswe')
        self.canvas.draw_idle()
        self.toolbarframe=tk.Frame(self)
        self.toolbarframe.grid(row=101, column=0, columnspan=10, sticky='nwe')
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.toolbarframe)
        self.toolbar.grid(row=102, column=0, columnspan=10, sticky='nwe')

        #tk.Label(self, text="Sweep magnetic field").grid(row=3,column=13)
        tk.Label(self, text="Parallel",relief='ridge').grid(row=4, column=14, columnspan=2)
        tk.Label(self, text="Angular",relief='ridge').grid(row=4, column=16, columnspan=2, sticky='e')
        tk.Label(self, text="Magnitude").grid(row=5, column=16)
        self.mag = tk.Entry(self, width=5)
        self.mag.insert(0, "0")
        self.mag.grid(row=5, column=17)
        tk.Label(self, text="G").grid(row=5, column=18, sticky='w')

        tk.Label(self, text="Start").grid(row=5, column=13, sticky='e')
        self.start = tk.Entry(self,width=5)
        self.start.insert(0, "0")
        self.start.grid(row=5, column=14)
        tk.Label(self, text="G").grid(row=5, column=15,sticky='w')
        tk.Label(self, text="Stop").grid(row=6, column=13, sticky='e')
        self.stop = tk.Entry(self,width=5)
        self.stop.insert(0, "0")
        self.stop.grid(row=6, column=14)
        tk.Label(self, text="G").grid(row=6, column=15,sticky='w')
        tk.Label(self,text="Step").grid(row=7,column=13, sticky='e')
        self.step = tk.Entry(self, width=5)
        self.step.insert(0,"0")
        self.step.grid(row=7, column=14)
        tk.Label(self,text="G").grid(row=7, column=15, sticky='w')
        tk.Label(self, text="Start").grid(row=6, column=16, sticky='e')
        self.startang = tk.Entry(self, width=5)
        self.startang.insert(0, "0")
        self.startang.grid(row=6, column=17)
        tk.Label(self, text="°").grid(row=6, column=18, sticky='w')
        tk.Label(self, text="Step").grid(row=7, column=16, sticky='e')
        self.stepang = tk.Entry(self, width=5)
        self.stepang.insert(0, "0")
        self.stepang.grid(row=7, column=17)
        tk.Label(self, text="°").grid(row=7, column=18, sticky='w')
        tk.Label(self, text="Stop").grid(row=8, column=16, sticky='e')
        self.stopang = tk.Entry(self, width=5)
        self.stopang.insert(0, "0")
        self.stopang.grid(row=8, column=17)
        tk.Label(self, text="°").grid(row=8, column=18, sticky='w')

        tk.Button(self, text="Calc", command=self.calcvect).grid(row=9, column=13,sticky='e')
        tk.Button(self, text="Scan", command=self.batchscan).grid(row=10, column=13,sticky='e')
        tk.Button(self, text="Save", command=self.file_save).grid(row=9, column=14)
        tk.Button(self, text="Stop", command=self.stop_run).grid(row=10, column=14)
        tk.Button(self, text="IF calibrate", command=self.cal).grid(row=10,column=16)
        tk.Button(self, text="Clear", command=self.clear).grid(row=9, column=15, columnspan=2, sticky='e')

        for i in np.arange(0,102):
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

    def calcvect(self):
        try:
            if int(self.step.get())==0:
                step = float(self.stepang.get())
                self.angles = np.arange(float(self.startang.get())*np.pi/180, (float(self.stopang.get())+step)*np.pi/180, step*np.pi/180)
                print(self.angles)
                mag = float(self.mag.get())
                par=[int(np.around(mag*np.cos(element)*FH1[0]+FH1[1])) for n, element in enumerate(self.angles)]
                per=[int(np.around(mag*np.sin(element)*FH[0]+FH[1])) for n, element in enumerate(self.angles)]
                self.values=np.row_stack((par,per))
                self.type="ang"
            else:
                step = float(self.step.get())
                self.values=np.arange(float(self.start.get()), float(self.stop.get())+float(step), float(step))
                self.values=[int(element*FH1[0]+FH1[1]) for n, element in enumerate(self.values)]
                self.type="parallel"
        except:
            print('Dividing by zero')
    
        #set the magnetic field. FH are values read from a calibration file, which can be updated 
    def writevolt(self):
        dev = comedi.comedi_open("/dev/comedi0")
        
        if len(self.values)==2: 
            val, val1=int(self.val[0]), int(self.val[1])

            if val < 0 and val > 4095 and val1<0 and val1 > 4095:
                val, val1 = datazero, datazero
                print('Input value not available')
            retvalw = comedi.comedi_data_write(dev, subdevw, chanw, rngw, aref, val)
            retvalw1 = comedi.comedi_data_write(dev, subdevw, chanw1, rngw, aref, val1)
            comedi.comedi_close(dev)
            print(f"Value set to:")

        else:
            if self.val<0 and self.val>4095:
                self.val=datazero
                print('Input value not available')
            retvalw=comedi.comedi_data_write(dev, subdevw,chanw,rngw,aref, int(self.val))

        #reset the magnet
    def zerofield(self):
        dev = comedi.comedi_open("/dev/comedi0")
        retval = comedi.comedi_data_write(dev, subdevw, chanw, rngw, aref, datazero)
        retval = comedi.comedi_data_write(dev, subdevw, chanw1, rngw, aref, datazero)
        print(f'Resetting DAQs to zero: {retval}')
        comedi.comedi_close(dev)
 
    def batchscan(self):
        self.run=True
       
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
            self.writevolt()
            self.takecal()
            #if self.type=="ang":
            #    print("ang")

            if i ==0:
                self.array=np.column_stack((self.S11a, self.Za, self.S11m))
            else:
                self.array=np.column_stack((self.array, self.S11a, self.Za, self.S11m))

        print('done')
        self.zerofield()
      
        #receiving measurements from the network analyzer
    def measure(self):
        inst.write("TRS;WFS")
        inst.write('*OPC?')
        c=True
        while c:
            val=0
            try:
                val=inst.read()
                c=False
            except:
                time.sleep(0.01)     
        inst.write("OFV") #requesting the frequency values
        freq=inst.read("\n")
        freq=freq.rsplit(", ")
        freq1=freq[0].rsplit(" ")
        freq1.extend(freq[1:])
        freq=[float(n) for n in freq1[1:]]

        inst.write("OFD") #requesting the S11 measurements, this returns the real and imag part
        valu=inst.read("\n")
        valu=valu.rsplit(",")
        print(valu[0])
        valu1=valu[0].rsplit(" ")
        if len(valu1)==1:
            valu1=valu[0].rsplit("-")
            valu1[1]='-'+valu1[1]
            if len(valu1)==3:
                valu1[1]=valu1[1]+'-'+valu1[2]
            
        valu1=[valu1[1]]
        valu1.extend(valu[1:])
        valu=[float(n) for n in valu1[1:]]
        real=imag=np.arange(len(freq),dtype=np.float64)

        real=np.array(valu[0:-1:2]) #the complex values are given in pairs
        imag=valu[1:-1:2]
        imag.append(valu[-1])
        imag=np.array(imag)
        return real, imag, freq

    def docal(self):
        global Edf, Erf, Esf, Z0
        Edf = S11l
        Erf = 2 * (S11o - S11l) * (S11l - S11s)/(S11o - S11s)
        Esf = (S11o + S11s - 2 * S11l)/(S11o - S11s)
        Z0 = 50
        self.S11a = (self.S11m - Edf)/((self.S11m - Edf) * Esf + Erf)
        self.Za = Z0 * (1 + self.S11a)/(1 - self.S11a)

        #this function measures multiple times by calling the measure funtion, it is called nave times
        #which is the number of averages
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
        print(f'1 of {nave+1} scans complete')
        for n in range(nave):
            real_p, imag_p, self.freq=self.measure()
            self.S11m=(self.S11m*(n+1)+real_p+1j*imag_p)/(n+2) #averaging with each iteration
            self.docal()
            self.ax.clear()
            self.ax1.clear()
            self.ax.set_xlabel('$f$ [Hz]')
            self.ax1.set_xlabel('$f$ [Hz]')
            self.ax.set_ylabel('$Z_a$ resistance [$\Omega$]')
            self.ax1.set_ylabel('$Z_a$ reactance [$\Omega$]')
            self.ax.plot(self.freq, self.Za.real, label=plotlabel)
            self.ax.legend()
            self.ax1.plot(self.freq, self.Za.imag, label=plotlabel)
            self.ax1.legend()
            self.canvas.draw_idle() #draw_idle is a gentle way to draw, it doesn't interupt the GUI
            self.canvas.flush_events()
            print(f'{n+2} of {nave+1} scans complete')

        print('Measurement complete')   

    def file_save(self):
        filename = tk.filedialog.asksaveasfilename(defaultextension="*.txt")
        intro=f'''#FMR data from {datetime.datetime.now()}, this file includes calibration measurements, correction factor and corrected S11 freq\tS11o\tS11l\tS11s\tEdf\tErf\tEsf\tS11a\tZa\tS11m'''
        #fmt=['%.5e', '%.5e %+.5ej', '%.5e %+.5ej', '%.5e %+.5ej', '%.5e %+.5ej', '%.5e %+.5ej', '%.5e %+.5ej', '%.5e %+.5ej', '%.5e %+.5ej', '%.5e %+.5ej']
        fmt='%.5e'
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
        tk.Button(self.buttonframe, text="Measure", command=lambda: controller.show_frame(StartPage), width=8, height=1).grid(row=0,column=0,padx=5)
        tk.Button(self.buttonframe, text="Viewer", command=lambda: controller.show_frame(Viewer2), width=8, height=1).grid(row=0,column=1)
        tk.Button(self.buttonframe, text="Batch", command=lambda: controller.show_frame(Batch), width=8, height=1).grid(row=1, column=0, sticky='n', padx=5)
        tk.Button(self.buttonframe, text="Calibrate", command=lambda: controller.show_frame(Calibrate), width=8, height=1).grid(row=1,column=1, sticky='n')
        tk.Button(self, text="Exit", command=self._quit).grid(row=0, column=17, sticky='e')
        #tk.Button(self, text="Single", command=lambda: controller.show_frame(Viewer2), width=8, height=1).grid(row=2, column=11, sticky='n')
        #tk.Button(self, text="Pair", command=lambda: controller.show_frame(Viewer), width=8, height=1).grid(row=2, column=12, sticky='n')
        self.buttonframe.columnconfigure(0,weight=1)
        self.buttonframe.columnconfigure(1,weight=1)
        tk.Button(self, text="Open", command=self.file_open).grid(row=4, column=15, pady=10, padx=5)
        tk.Button(self, text="Plot", command=self.plot, width=3).grid(row=6, column=17,sticky='n')
        tk.Label(self, text="Plot selection").grid(row=5, column=16)
        self.listbox=tk.Listbox(self, width=8, height=1)
        self.listbox.grid(row=5, column=15)
        self.elements=["Za", "angle", "Ku", "EA", "S11a", "S11m", "S11o", "S11l", "S11s", "Edf", "Erf", "Esf"]
        
        for i, ele in enumerate(self.elements):
            self.listbox.insert(i, ele)

        self.titlevar=tk.IntVar()
        self.titlevar.set(0)
        tk.Checkbutton(self, text='Title', variable=self.titlevar, command=self.title).grid(row=5,column=11,sticky='sw')
        self.custvar=tk.IntVar()
        self.custvar.set(0)
        tk.Checkbutton(self, text='Legend', variable=self.custvar, command=self.custom).grid(row=6,column=11,sticky='nw')
        
       
        self.listboxopen=tk.Listbox(self, selectmode=tk.EXTENDED, height=6, width=24)
        self.listboxopen.grid(row=6, column=15, columnspan=2, sticky='s')
        tk.Button(self, text="Remove", command=self.listbox_delete).grid(row=4, column=16)
        self.filelist=[]
        tk.Button(self, text='up', command=lambda: self.reArrangeListbox("up")).grid(row=6, column=17)
        tk.Button(self, text='dn', command=lambda: self.reArrangeListbox("dn")).grid(row=6, column=17, sticky='s')
        
        #tk.Label(self, text="Analysis", relief='ridge').grid(row=7, column=13)
        self.chipeakframe=tk.Frame(self)
        self.chipeakframe.grid(row=8,column=15,columnspan=5)
        tk.Button(self.chipeakframe, text="Peak", command=self.peak_finder, width=3).grid(row=0, column=1,sticky='e')
        tk.Button(self.chipeakframe, text="+", command=lambda: self.jump_right(0)).grid(row=0, column=3, sticky='w')
        tk.Button(self.chipeakframe, text="-", command=lambda: self.jump_left(0)).grid(row=0, column=2, sticky='e')
        tk.Button(self, text='Save', command=self.save).grid(row=9, column=17,sticky='w')
        tk.Button(self, text='Save as', command=self.save_as).grid(row=10, column=17,sticky='w')
        tk.Label(self.chipeakframe, text="Order").grid(row=0, column=4, sticky='e')
        self.entryorder=tk.Entry(self.chipeakframe, width=5)
        self.entryorder.insert(0,"50")
        self.entryorder.grid(row=0, column=5)
        tk.Button(self.chipeakframe, text="Chi", command=self.chi, width=2).grid(row=0, column=0,sticky='w')        
       
        self.circvar=tk.IntVar()
        self.circvar.set(1)
        self.squarevar=tk.IntVar()
        self.circ=tk.Checkbutton(self, text="Circular", variable=self.circvar)
        self.square=tk.Checkbutton(self, text="Square", variable=self.squarevar)
        tk.Label(self, text="Sample", relief='ridge').grid(row=9, column=14)
        tk.Label(self, text="Width [mm]").grid(row=10, column=15,sticky='e')
        tk.Label(self, text="Thickness [nm]").grid(row=11, column=15,sticky='e')
        self.circ.grid(row=12, column=15)
        self.square.grid(row=12, column=16)

        self.entrywidth = tk.Entry(self,width=5)
        self.entrywidth.insert(0, "4")
        self.entrywidth.grid(row=10, column=16)
        self.entrythick = tk.Entry(self,width=5)
        self.entrythick.insert(0, "50")
        self.entrythick.grid(row=11, column=16)
        
        tk.Label(self, text="FWHM", relief='ridge').grid(row=14, column=14)
        tk.Button(self, text='Determine', command=lambda: self.fwhm(0)).grid(row=15, column=15)
        tk.Button(self, text='Rerun', command=lambda: self.fwhm(1)).grid(row=15,column=16)
        tk.Label(self, text='Resize').grid(row=14,column=17)
        self.entrySize=tk.Entry(self,width=8)
        self.entrySize.insert(0,'0')
        self.entrySize.grid(row=15,column=17)
        
        tk.Label(self, text='Axis limits').grid(row=18,column=15)
        self.axismin=tk.Entry(self,width=8)
        self.axismax=tk.Entry(self,width=8)
        self.axismin.insert(0,'0')
        self.axismax.insert(0,'0')
        self.axismin.grid(row=18,column=16)
        self.axismax.grid(row=18,column=17)
        tk.Label(self, text='Fit')
        self.varGauss, self.varLor=tk.IntVar(self), tk.IntVar(self)
        self.Gauss=tk.Checkbutton(self, text="Gaussian", variable=self.varGauss,command=lambda: self.set_checkfit(0)).grid(row=17,column=15)
        self.Lorentz=tk.Checkbutton(self, text="Lorentzian", variable=self.varLor,command=lambda: self.set_checkfit(1)).grid(row=17,column=16)
        self.varGauss.set(1)

        self.fitchivar=tk.IntVar(self)
        self.fitchi=tk.Checkbutton(self,text="Fit Chi", variable=self.fitchivar,command=self.fitchiframe, relief='ridge').grid(row=19,column=14)

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
            
    def set_checkcurr(self,arg):
        for i, ele in enumerate(self.checklista):
            if i!=arg:
                ele.set(0)
                
    def save_as(self):
        filename = tk.filedialog.asksaveasfilename(defaultextension="*.txt")
        skjal=open(filename,'w')
        skjal.write('Filename\tAmplitude\tMean[Hz]\tStddev[Hz]\tFWHM[Hz]\n') 
        skjal.close()

    def save(self):
        t=tk.filedialog.askopenfilename()
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
        peakwith=8e9
        indexspan=(peakwith/freqspan)*len(self.freq)
        
        
        dw=int((self.peaks_imag[0,self.indexmax]-self.peaks_imag[0,self.indexmax-1])/2)
        dw1=int((self.peaks_imag[0,self.indexmax+1]-self.peaks_imag[0,self.indexmax])/2)
        if dw>dw1:
            dw=dw1

        if self.varGauss.get() == 1:
            model=GaussianModel()
        else:
            model=LorentzianModel()

        if dex==0:
            self.freqfit=self.freq[(self.peaks_imag[0,self.indexmax]-int(round(indexspan/2))):(self.peaks_imag[0,self.indexmax]+int(round(indexspan/2)))]
            self.imagfit=self.imag[(self.peaks_imag[0,self.indexmax]-int(round(indexspan/2))):(self.peaks_imag[0,self.indexmax]+int(round(indexspan/2)))]
            #self.shift=min(self.imagfit)
            #print(self.shift)
            #self.imagfit=(-1)*self.shift+self.imagfit
            topindex=self.peaks_imag[0,self.indexmax]
            self.iteratorfwhm=0
            #self.freqfit=self.freqfit*10**-9
            #params=model.make_params(amplitude=self.imag[topindex], center=self.freq[topindex]*10**-9, sigma=(self.freqfit[-1]-self.freqfit[0])/2, gamma=1)
            params=model.make_params(amplitude=self.imag[topindex]*self.freqfit[0], center=self.freq[topindex], sigma=(self.freqfit[-1]-self.freqfit[0])/2)
        else:
            if self.entrySize.get() !='0':
                factor=float(self.entrySize.get())
            else:
                factor=7/8
                
            self.iteratorfwhm +=1    

            params=model.make_params(amplitude=self.ampl, center=self.mode, sigma=self.sigma)
            print('iterator ' + str(self.iteratorfwhm))
            self.freqfit=self.freq[(self.peaks_imag[0,self.indexmax]-int(round(indexspan*factor**self.iteratorfwhm/2))):(self.peaks_imag[0,self.indexmax]+int(round(indexspan*factor**self.iteratorfwhm/2)))]
            self.imagfit=self.imag[(self.peaks_imag[0,self.indexmax]-int(round(indexspan*factor**self.iteratorfwhm/2))):(self.peaks_imag[0,self.indexmax]+int(round(indexspan*factor**self.iteratorfwhm/2)))]
            
        

        result=model.fit(self.imagfit, params, x=self.freqfit)
        print(result.fit_report())
        self.ampl=result.params['amplitude'].value#+self.shift
        self.mode=result.params['center'].value
        self.sigma=result.params['sigma'].value
        self.variance=result.params['fwhm'].value
        self.ax.clear()
        self.peak_finder()
        self.ax.plot(self.freqfit, result.best_fit)#+self.shift)
        print(self.variance)
        self.maxima=self.freqfit[np.where(result.best_fit==max(result.best_fit))]
        if self.axismin.get() !='0':
            imagfit=self.imagfit#+self.shift
            self.ax.set_xlim(float(self.axismin.get()),float(self.axismax.get()))
            self.ax.set_ylim(min(imagfit[np.where((self.freqfit>round(float(self.axismin.get()))) & (self.freqfit<round(float(self.axismax.get()))))]),1.5*max(imagfit[np.where((self.freqfit>round(float(self.axismin.get()))) & (self.freqfit<round(float(self.axismax.get()))))]))
        self.ax.plot(self.maxima-self.variance/2,(max(result.best_fit)/2),'*',self.maxima+self.variance/2, max(result.best_fit)/2,'*')#tók self.shift
        self.ax.plot(self.maxima,max(result.best_fit),'o')#+self.shift,'o')
        self.canvas.draw()


        #laga peak_finder hægt að skoða hæðsta toppinn, þá væri gagnasöfnunin miklu hraðari

    def peak_finder(self):
        self.iterator=0
        texti=pd.read_csv(self.filelist[0], index_col=False, comment= "#", sep='\t', engine='python')
        try:
            selected=self.elements[self.listbox.curselection()[0]]
        except:
            selected='Za'
        
        entryorder=int(self.entryorder.get())

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

        self.peaks_real, self.peaks_imag = signal.argrelextrema(self.real,np.greater,order=entryorder), signal.argrelextrema(self.imag,np.greater,order=entryorder)
        self.minima_real, self.minima_imag = signal.argrelextrema(self.real,np.less,order=entryorder), signal.argrelextrema(self.imag,np.less,order=entryorder)

        #self.ax.plot(frequency[self.peaks_real],self.real[self.peaks_real], 'o')#, frequency[self.minima_real],self.real[self.minima_real], 'o')
        self.ax.plot(frequency[self.peaks_imag],self.imag[self.peaks_imag], 'o')#, frequency[self.minima_imag],self.imag[self.minima_imag], 'o')
        if self.axismin.get() !='0':
            self.ax.set_xlim(float(self.axismin.get()),float(self.axismax.get()))
            #self.ax.set_ylim(0,max(self.imagfit[np.where(self.freqfit>float(self.axismin.get()) & self.freqfit<float(self.axismax.get()))]))
            self.ax.set_ylim(min(self.imag[np.where((self.freq>round(float(self.axismin.get()))) & (self.freq<round(float(self.axismax.get()))))]),1.5*max(self.imag[np.where((self.freq>round(float(self.axismin.get()))) & (self.freq<round(float(self.axismax.get()))))]))
        self.canvas.draw()
        #self.peaks_real=np.array(self.peaks_real)
        self.peaks_imag=np.array(self.peaks_imag)

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
        self.chii = np.zeros(nfpoints, dtype=np.complex128)
        string=self.filelist[0].rsplit('_')
        string.pop(-1)
        string.append('-0.0G.dat')
        nstring='_'
        nstring=nstring.join(string)
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
        W=16e-6

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

        for item in plotlist:
            texti=pd.read_csv(item, index_col=False, comment= "#", sep='\t', engine='python')
            self.freq=texti['freq'].to_numpy(dtype=complex).real*2*np.pi
            real=texti['Za'].to_numpy(dtype=complex).real
            imag=texti['Za'].to_numpy(dtype=complex).imag
            #real=real-Zzero.real
            #imag=imag-Zzero.imag
            chi=imag*W/(1*mu*V*self.freq)
            chii=real*W/(1*mu*V*self.freq)
            self.chii=chi+1j*chii
            re='Re($\chi$) '+item.split('/')[-1].split('.')[0]
            im='Im($\chi$) '+item.split('/')[-1].split('.')[0]
            self.ax.plot(self.freq,self.chii.real,label=re)
            self.ax.plot(self.freq,self.chii.imag,label=im)
            
            if self.custvar.get()==1:
                self.legendliststr=[]
                for i in range(0,self.n):
                    for n in range(0,1):
                        self.legendliststr.append(self.legendlist[i].get()+' Re($\chi$)')
                        self.legendliststr.append(self.legendlist[i].get()+' Im($\chi$)')

                self.ax.legend(self.legendliststr)
            else:
                self.ax.legend()#legend)
        if self.axismin.get() !='0':
            self.ax.set_xlim(float(self.axismin.get()),float(self.axismax.get()))
            #print(max(chi[np.where((self.freq>round(float(self.axismin.get()))) & (self.freq<round(float(self.axismax.get()))))]))# & self.freq<round(float(self.axismax.get()))))
            self.ax.set_ylim(min(chi[np.where((self.freq>round(float(self.axismin.get()))) & (self.freq<round(float(self.axismax.get()))))]),1.5*max(chi[np.where((self.freq>round(float(self.axismin.get()))) & (self.freq<round(float(self.axismax.get()))))]))
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

        start=self.mode-self.variance
        end=(self.mode+self.variance)

        print(np.where(freq<start))
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
        K_s=float(self.entryKs.get())
        K_sMin=float(self.entryKsMin.get())
        K_sMax=float(self.entryKsMax.get())
        H=float(self.filelist[self.listboxopen.curselection()[0]].split('_')[-1].split('.')[0])
        alphavalue=float(self.entryAlpha.get())
        alphavalueMin=float(self.entryAlMin.get())
        alphavalueMax=float(self.entryAlMax.get())
        d=float(self.entrythick.get())*1e-9
        #Dx=H+(4*np.pi+2*K_u/(M**2)+4*K_s/(d*M**2))*M
        #Dy=2*H+(4*np.pi+4*K_u/(M**2)+4*K_s/(d*M**2))*M

        params=Parameters()
        if gammaMin!=gammaMax:
            params.add('gamma',value=gamma,min=gammaMin,max=gammaMax)

        if alphavalueMin!=alphavalueMax:
            params.add('alpha',value=alphavalue,min=alphavalueMin,max=alphavalueMax)
                         
        if K_sMin!=K_sMax:
            params.add('Ks',value=K_s,min=K_sMin,max=K_sMax)
            
        if MMin!=MMax:
            params.add('M',value=M,min=MMin,max=MMax)

        if K_uMin!=K_uMax:
            params.add('Ku',value=K_u,min=K_uMin,max=K_uMax)


        def fcn2min(params,x,y):
            if alphavalueMin!=alphavalueMax:
                alpha=params['alpha']

            if MMin!=MMax:
                M=params['M']

            if K_sMin!=K_sMax:
                K_s=params['Ks']

            if K_uMin!=K_uMax:
                K_u=params['Ku']

            if gammaMin!=gammaMax:
                gamma=params['gamma']
                
            chi_num=gamma**2*M*(H+(4*np.pi+2*K_u/(M**2)+4*K_s/(d*M**2))*M)+1j*x*alpha*gamma*M
            omegarpow2=gamma**2*(H+(4*np.pi+2*K_u/(M**2)+4*K_s/(d*M**2))*M)*(H+2*K_u/M)
            chi_den=omegarpow2*-x**2*(1+alpha**2)+1j*x*gamma*alpha*(2*H+(4*np.pi+4*K_u/(M**2)+4*K_s/(d*M**2))*M)
            chi=chi_num/chi_den
            resids=(y.imag-chi.imag)**2+(y.real-chi.real)**2
            return resids

        #tverhluti=self.chii-min(self.chii[np.where((self.freq>start*0.66) & (self.freq<end))].imag)
        #raunhluti=self.chii+min(self.chii[np.where((self.freq>start*0.66) & (self.freq<end))].imag)
        #chitoppur=raunhluti+1j*tverhluti
        #minner = Minimizer(fcn2min, params, fcn_args=(self.freq[np.where((self.freq>start*0.66) & (self.freq<end))],chitoppur[np.where((self.freq>start*0.66) & (self.freq<end))]))
        minner = Minimizer(fcn2min, params, fcn_args=(self.freq[np.where((self.freq>start) & (self.freq<end))], self.chii[np.where((self.freq>start) & (self.freq<end))]))
        result = minner.minimize()
        report_fit(result)
        if alphavalueMin!=alphavalueMax:
            alpha=result.params['alpha'].value
            self.entryAlpha.delete(0,"end")
            self.entryAlpha.insert(0,result.params['alpha'].value)

        if MMin!=MMax:
            M=result.params['M'].value
            self.entryMs.delete(0,"end")
            self.entryMs.insert(0,result.params['M'].value)

        if K_sMin!=K_sMax:
            K_s=result.params['Ks'].value
            self.entryKs.delete(0,"end")
            self.entryKs.insert(0,result.params['Ks'].value)

        if K_uMin!=K_uMax:
            K_u=result.params['Ku'].value
            self.entryKu.delete(0,"end")
            self.entryKu.insert(0,result.params['Ku'].value)

        if gammaMin!=gammaMax:
            gamma=result.params['gamma'].value
            self.entryGamma.delete(0,"end")
            self.entryGamma.insert(0,result.params['gamma'].value)
        
        freq=self.freq[np.where((self.freq>start) & (self.freq<end))]
        chi_num=gamma**2*M*(H+(4*np.pi+2*K_u/(M**2)+4*K_s/(d*M**2))*M)+1j*freq*alpha*gamma*M
        omegarpow2=gamma**2*(H+(4*np.pi+2*K_u/(M**2)+4*K_s/(d*M**2))*M)*(H+2*K_u/M)
        chi_den=omegarpow2-freq**2*(1+alpha**2)+1j*freq*gamma*alpha*(2*H+(4*np.pi+4*K_u/(M**2)+4*K_s/(d*M**2))*M)
        chi=chi_num/chi_den
        self.ax.clear()
        #self.ax.plot(freqlin,chiilin, '*',label='imaglin')
        self.ax.plot(self.freq, self.chii.real, label='Real Chi')  #+min(self.chii.imag[100:-1])
        self.ax.plot(self.freq, self.chii.imag, label='Imag Chi')   #-min(self.chii.imag[100:-1])
        self.ax.plot(freq,chi.real,label="re")
        self.ax.plot(freq,chi.imag,label="im")
        #self.ax.plot(omegarpow2,max(chi.imag),'*')
        self.ax.legend()
        self.canvas.draw()  
        
    def _quit(self):
        app.quit()
        app.destroy()

        #creates a list of .dat files to plot

    def file_open(self):
        t=tk.filedialog.askopenfilenames(initialdir='/home/at/FMR/netgreinir/maelingar/')
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

    def fitchiframe(self):
        if self.fitchivar.get()==1:
            self.rowconfigure(20, weight=5)
            self.custframe=tk.Frame(self)
            self.custframe.grid(row=20, column=15, columnspan=3, rowspan=9, sticky='nsew')
            
            tk.Button(self.custframe, text="Fit chi", command=self.fit_chi, width=6).grid(row=0, column=1)
            tk.Label(self.custframe,text='Min').grid(row=0,column=2)
            tk.Label(self.custframe,text='Max').grid(row=0,column=3)
            tk.Label(self.custframe,text="\u03B3").grid(row=1,column=0)
            self.entryGamma=tk.Entry(self.custframe,width=10)
            self.entryGamma.insert(0,'0')
            self.entryGamma.grid(row=1, column=1)
            
            self.entryGaMin=tk.Entry(self.custframe,width=10)
            self.entryGaMin.insert(0,'0')
            self.entryGaMin.grid(row=1,column=2)
            self.entryGaMax=tk.Entry(self.custframe,width=10)
            self.entryGaMax.insert(0,'0')
            self.entryGaMax.grid(row=1,column=3)
            
            tk.Label(self.custframe,text="\u03B1").grid(row=2,column=0)
            self.entryAlpha=tk.Entry(self.custframe,width=10)
            self.entryAlpha.insert(0, '0')
            self.entryAlpha.grid(row=2,column=1)

            self.entryAlMin=tk.Entry(self.custframe,width=10)
            self.entryAlMin.insert(0,'0')
            self.entryAlMin.grid(row=2,column=2)
            self.entryAlMax=tk.Entry(self.custframe,width=10)
            self.entryAlMax.insert(0,'0')
            self.entryAlMax.grid(row=2,column=3)
            
            tk.Label(self.custframe,text="K\u0075").grid(row=3,column=0)
            self.entryKu=tk.Entry(self.custframe,width=10)
            self.entryKu.insert(0,'0')
            self.entryKu.grid(row=3,column=1)

            self.entryKuMin=tk.Entry(self.custframe,width=10)
            self.entryKuMin.insert(0,'0')
            self.entryKuMin.grid(row=3,column=2)
            self.entryKuMax=tk.Entry(self.custframe,width=10)
            self.entryKuMax.insert(0,'0')
            self.entryKuMax.grid(row=3,column=3)
            
            tk.Label(self.custframe,text='K\u0073').grid(row=4,column=0)
            self.entryKs=tk.Entry(self.custframe,width=10)
            self.entryKs.insert(0,'0')
            self.entryKs.grid(row=4,column=1)

            self.entryKsMin=tk.Entry(self.custframe,width=10)
            self.entryKsMin.insert(0,'0')
            self.entryKsMin.grid(row=4,column=2)
            self.entryKsMax=tk.Entry(self.custframe,width=10)
            self.entryKsMax.insert(0,'0')
            self.entryKsMax.grid(row=4,column=3)

            tk.Label(self.custframe,text='M\u0073').grid(row=5,column=0)
            self.entryMs=tk.Entry(self.custframe,width=10)
            self.entryMs.insert(0,'0')
            self.entryMs.grid(row=5,column=1)

            self.entryMsMin=tk.Entry(self.custframe,width=10)
            self.entryMsMin.insert(0,'0')
            self.entryMsMin.grid(row=5,column=2)
            self.entryMsMax=tk.Entry(self.custframe,width=10)
            self.entryMsMax.insert(0,'0')
            self.entryMsMax.grid(row=5,column=3)

            for i in np.arange(0,5):
                self.custframe.rowconfigure(i, weight=1)
        else:
            self.custframe.destroy()
    
    def plot(self):
        try:
            selected=self.elements[self.listbox.curselection()[0]]
        except:
            selected='Za'

        selection=self.listboxopen.curselection()
        if len(selection) > 0:
            plotlist = [item for n, item in enumerate(self.filelist) if n in selection]
        else:
            plotlist = self.filelist

        self.indexmax=0
        self.indicator=0
        self.ax.clear()
        self.ax.set_xlabel('$f$ [Hz]')
        self.ax.set_ylabel(selected +' [$\Omega$]')
        for item in plotlist:
            texti=pd.read_csv(item, index_col=False, comment= "#", sep='\t', engine='python')
            if selected == 'angle':
                self.ax.clear()
                self.ax.set_xlabel('$\Theta$ [°]')
                self.ax.set_ylabel('$\omega_r  [rad/s]$')

                field=np.loadtxt(plotlist[0],usecols=[0], dtype='str', skiprows=1, delimiter='\t')
                resonance=np.loadtxt(plotlist[0], usecols=[2], skiprows=1, delimiter='\t')
                field=np.array([float(i.split('_')[-1].split('G')[0]) for i in field])

                self.ax.plot(field,resonance,'*')
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
                minner = Minimizer(fcn2min, params, fcn_args = (x**2,resonance**2))
                result = minner.minimize()
                report_fit(result)
                self.ax.clear()
                self.ax.set_xlabel('cos($ \Theta$ )^2')
                self.ax.set_ylabel('$\omega ^2 [rad^2/s^2]$')
                self.ax.plot(x**2, resonance**2,'*')
                self.ax.plot(x**2,result.params['a']*x**4+result.params['b']*x**2+result.params['c'],'X')

                M=float(self.entryMs.get())
                H=float(plotlist[0].split('_')[-2].split('G')[0])
                print(H)
                K_s=0
                d=float(self.entrythick.get())*1e-9
                a=result.params['a']
                b=result.params['b']
                c=result.params['c']
                r=4/(M**2)
                s=-6*H/M-16*np.pi-8*np.pi*(a+b)/c-2*(H/M)*((a+b)/c)-16*K_s/(d*M**2)-8*K_s*(a+b)/(d*c*M**2)
                t=(-H**2-4*np.pi*M*H-4*K_s*H/(d*M))*(a+b)/c
                try:
                    x=(-s+np.sqrt(s**2-4*r*t))/(2*r)
                    print(f'x er {x} erg/cm^3')
                except:
                    print('x er ekki lausn')

                try:    
                    x1=(-s-np.sqrt(s**2-4*r*t))/(2*r)
                    print(f'x1 er {x1} erg/cm^3')
                except:
                    print('x1 er ekki lausn')

                self.entryKu.delete(0,"end")
                self.entryKu.insert(0,abs(x1))

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

    def title(self):
        if self.titlevar.get()==1:
            self.titleentry=tk.Entry(self, width=18)
            self.titleentry.grid(row=5,column=12,sticky='s')
        else:
            self.titleentry.destroy()
    
    def custom(self):
        
        if self.custvar.get()==1:
            print('reyna')
            try:
                self.n=len(self.filelist)
            except:
                self.n=0

            self.customframe=tk.Frame(self)
            self.customframe.grid(row=6,column=12, columnspan=1,rowspan=5,sticky='nes')
            self.legendlist=[]
            for i in range(0, self.n):
                
                entr = tk.Entry(self.customframe, width=18)
                entr.grid(row=i,column=0)
                entr.insert(0,self.filelist[i].split("/")[-1])
                self.legendlist.append(entr)
                
            print(self.legendlist)
        else:
            self.customframe.destroy()

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
    rm = pyvisa.ResourceManager('@py')
    inst = rm.open_resource('GPIB0::6::INSTR')
    inst.write("S11")
    #inst.write("HC0") #turn of automatic IF calibration
    start="SRT 40 MHz"
    stop="10000"
    stop="STP 10000 MHz"
    inst.write(start)
    inst.write(stop)
    inst.write("FMA") #Select ASCII data transfer format
    inst.write("HLD")
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
    dev = comedi.comedi_open("/dev/comedi0")
    ranger = comedi.comedi_get_range(dev, subdevr, chanr, rngr)
except:
    print('Magnet not responding')
if __name__=='__main__':
    app = App()
    app.mainloop()
