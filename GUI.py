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

        #x, y = self.winfo_screenwidth(), self.winfo_screenheight()
        #self.geometry("%dx%d+%d+%d" % (800,450,x/2-800/2,y/2-450/2))

        self.frames = {}
        #for-loop to place each page in the container or parent page
        for F in (StartPage, Calibrate, Batch, Viewer, Viewer2):

            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row = 0, column = 0, sticky="nsew")

        self.show_frame(Calibrate)
        #raises the page to the top with tkraise()
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    #this is the main page
class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
       
        tk.Button(self, text="Measure", command=lambda: controller.show_frame(StartPage), width=8, height=1).grid(row=0,column=11,padx=5)
        tk.Button(self, text="Viewer", command=lambda: controller.show_frame(Viewer), width=8, height=1).grid(row=0,column=12)
        tk.Button(self, text="Batch", command=lambda: controller.show_frame(Batch), width=8, height=1).grid(row=1, column=11, sticky='n', padx=5)
        tk.Button(self, text="Calibrate", command=lambda: controller.show_frame(Calibrate), width=8, height=1).grid(row=1,column=12, sticky='n')
        tk.Button(self, text="Exit", command=self._quit).grid(row=0, column=17)

        tk.Button(self, text="Scan", command=self.takecal).grid(row=2, column=13, sticky='e')
        tk.Button(self, text="Save", command=self.file_save).grid(row=2, column=14, pady=5)
        self.fig = plt.figure(constrained_layout=False, figsize=[10,9])
        tk.Button(self, text="Stop", command=self.stop_run).grid(row=2, column=15)
        gs1 = self.fig.add_gridspec(nrows=1, ncols=2, left=0.1, right=0.95, wspace=0.3)
        self.ax = self.fig.add_subplot(gs1[0,0])
        self.ax1 = self.fig.add_subplot(gs1[0,1])
        self.ax.set_xlabel('$f$ [Hz]')
        self.ax1.set_xlabel('$f$ [Hz]')
        self.ax.set_ylabel('S11 resistance [$\Omega$]')
        self.ax1.set_ylabel('S11 reactance [$\Omega$]')
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().grid(row=0, column=0, rowspan=100, columnspan=10)
        self.canvas.draw_idle()
        self.toolbarframe=tk.Frame(self)
        self.toolbarframe.grid(row=101, column=0, columnspan=10, sticky='nwe')
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.toolbarframe)
        self.toolbar.grid(row=102, column=0, columnspan=10, sticky='nwe')
        
        tk.Label(self, text="Set magnetic field").grid(row=3, column=13)
        tk.Label(self, text="Parallel").grid(row=4,column=13)
        self.entrypar = tk.Entry(self,width=5)
        self.entrypar.insert(0, "0")
        self.entrypar.grid(row=4, column=14)
        tk.Label(self, text="G ").grid(row=4, column=15, sticky='w')

        tk.Label(self, text="Perpendicular").grid(row=5,column=13)
        self.entryper = tk.Entry(self,width=5)
        self.entryper.insert(0, "0")
        self.entryper.grid(row=5, column=14)
        tk.Label(self, text="G ").grid(row=5, column=15,sticky='w')
        
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

        tk.Button(self, text="Reset", command=self.zerofield).grid(row=6, column=17)
        tk.Button(self, text="Set", command=self.writevolt, width=1).grid(row=6, column=16, sticky='e')
    
    def _quit(self):
        app.quit()
        app.destroy()
    
    def stop_run(self):
        self.run=False

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
        valu1.extend(valu[1:])
        valu=[float(n) for n in valu1[1:]]
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
        self.canvas.get_tk_widget().grid(row=0, column=0, rowspan=100, columnspan=10)
        self.canvas.draw_idle()
        self.toolbarframe=tk.Frame(self)
        self.toolbarframe.grid(row=101, column=0, columnspan=10, sticky='nwe')
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.toolbarframe)
        self.toolbar.grid(row=102, column=0, columnspan=10, sticky='nwe')
        tk.Button(self, text="Measure", command=lambda: controller.show_frame(StartPage), width=8, height=1).grid(row=0,column=11,padx=5)
        tk.Button(self, text="Viewer", command=lambda: controller.show_frame(Viewer), width=8, height=1).grid(row=0,column=12)
        tk.Button(self, text="Batch", command=lambda: controller.show_frame(Batch), width=8, height=1).grid(row=1, column=11, sticky='n', padx=5)
        tk.Button(self, text="Calibrate", command=lambda: controller.show_frame(Calibrate), width=8, height=1).grid(row=1,column=12, sticky='n')
        tk.Button(self, text="Exit", command=self._quit).grid(row=0, column=17, sticky='e')

        tk.Button(self, text="Scan", command=self.takecal).grid(row=2, column=13)
        self.listbox=tk.Listbox(self, height=2, width=5)
        self.listbox.grid(row=2,column=14)
        elements=['Open', 'Load', 'Short']
        for i, ele in enumerate(elements):
            self.listbox.insert(i, ele)

        tk.Button(self, text="save", command=self.save).grid(row=2,column=15, columnspan=2)
        
        tk.Label(self, text="Set magnetic field").grid(row=3, column=13)
        
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

        tk.Label(self, text="Sweep setup").grid(row=9, column=13)

        tk.Label(self, text="Start").grid(row=10, column=13)
        self.startentry=tk.Entry(self, width=5)
        self.startentry.insert(0, "40")
        self.startentry.grid(row=10, column=14)
        tk.Label(self, text="MHz").grid(row=9, column=15)

        tk.Label(self, text="Stop").grid(row=11, column=13)
        self.stopentry=tk.Entry(self, width=5)
        self.stopentry.insert(0, "10000")
        self.stopentry.grid(row=11, column=14)
        tk.Label(self, text="MHz").grid(row=11, column=15)

        tk.Label(self, text="Nr. of meas.").grid(row=13, column=13)
        self.numberentry=tk.Entry(self, width=5)
        self.numberentry.insert(0, "10")
        self.numberentry.grid(row=13, column=14)

        tk.Label(self, text="Data points").grid(row=14,column=13)
        self.pointsbox=tk.Entry(self, width=6)
        self.pointsbox.insert(0, "401")
        self.pointsbox.grid(row=14, column=14)
        self.pointlist=["51", "101", "201", "401", "801", "1601"]
        tk.Button(self, text="+", command=lambda: self._up(0), width=1, height=1).grid(row=14, column=15)
        tk.Button(self, text="-", command=lambda: self._down(0), width=1, height=1).grid(row=14,column=16)

        tk.Label(self, text="IF BW").grid(row=15, column=13)
        self.IF_list=["10 Hz", "100 Hz", "1 kHz", "10 kHz"]
        self.IF_BW=tk.Entry(self,width=6)
        self.IF_BW.insert(0,"1 kHz")
        self.IF_BW.grid(row=15, column=14)
        tk.Button(self, text="+", command=lambda: self._up(1), width=1, height=1).grid(row=15, column=15)
        tk.Button(self, text="-", command=lambda: self._down(1), width=1, height=1).grid(row=15,column=16)
        tk.Button(self, text="Set values", command=self.set_values).grid(row=9, column=16, columnspan=3)
        tk.Button(self, text="Calibrate IF", command=self.cal).grid(row=10, column=16, columnspan=3)
    
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
        valu1.extend(valu[1:])
        valu=[float(n) for n in valu1[1:]]
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
        tk.Button(self, text="Measure", command=lambda: controller.show_frame(StartPage), width=8, height=1).grid(row=0,column=11,padx=5)
        tk.Button(self, text="Viewer", command=lambda: controller.show_frame(Viewer), width=8, height=1).grid(row=0,column=12)
        tk.Button(self, text="Batch", command=lambda: controller.show_frame(Batch), width=8, height=1).grid(row=1, column=11, sticky='n', padx=5)
        tk.Button(self, text="Calibrate", command=lambda: controller.show_frame(Calibrate), width=8, height=1).grid(row=1,column=12, sticky='n')
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
        self.canvas.get_tk_widget().grid(row=0, column=0, rowspan=100, columnspan=10)
        self.canvas.draw_idle()
        self.toolbarframe=tk.Frame(self)
        self.toolbarframe.grid(row=101, column=0, columnspan=10, sticky='nwe')
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.toolbarframe)
        self.toolbar.grid(row=102, column=0, columnspan=10, sticky='nwe')

        tk.Label(self, text="Sweep magnetic field").grid(row=3,column=13)
        tk.Label(self, text="Parallel").grid(row=4, column=14, columnspan=2)
        tk.Label(self, text="Angular").grid(row=4, column=16, columnspan=2, sticky='e')
        tk.Label(self, text="Magnitude").grid(row=5, column=16)
        self.mag = tk.Entry(self, width=5)
        self.mag.insert(0, "0")
        self.mag.grid(row=5, column=17)
        tk.Label(self, text="G").grid(row=5, column=18, sticky='w')

        tk.Label(self, text="Start").grid(row=6, column=13, sticky='e')
        self.start = tk.Entry(self,width=5)
        self.start.insert(0, "0")
        self.start.grid(row=6, column=14)
        tk.Label(self, text="G").grid(row=6, column=15,sticky='w')
        tk.Label(self, text="Stop").grid(row=7, column=13, sticky='e')
        self.stop = tk.Entry(self,width=5)
        self.stop.insert(0, "0")
        self.stop.grid(row=7, column=14)
        tk.Label(self, text="G").grid(row=7, column=15,sticky='w')
        tk.Label(self,text="Step").grid(row=8,column=13, sticky='e')
        self.step = tk.Entry(self, width=5)
        self.step.insert(0,"0")
        self.step.grid(row=8, column=14)
        tk.Label(self,text="G").grid(row=8, column=15, sticky='w')
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
        tk.Button(self, text="Clear", command=self.clear).grid(row=9, column=15, columnspan=2, sticky='e')
        tk.Button(self, text="write", command=self.write).grid(row=10, column=15)

    def write(self):
        self.val=self.values[0,4]
        print(self.angles[self.values[0,:]==self.val]*180/np.pi)

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
        valu1=valu[0].rsplit(" ")
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
        intro=f'''#FMR data from {datetime.datetime.now()}, this file includes calibration measurements, correction factor and corrected S11
freq\tS11o\tS11l\tS11s\tEdf\tErf\tEsf\tS11a\tZa\tS11m'''
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

        
      #Viewer to analyze data
class Viewer(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        tk.Button(self, text="Measure", command=lambda: controller.show_frame(StartPage), width=8, height=1).grid(row=0,column=11,padx=5)
        tk.Button(self, text="Viewer", command=lambda: controller.show_frame(Viewer), width=8, height=1).grid(row=0,column=12)
        tk.Button(self, text="Batch", command=lambda: controller.show_frame(Batch), width=8, height=1).grid(row=1, column=11, sticky='n', padx=5)
        tk.Button(self, text="Calibrate", command=lambda: controller.show_frame(Calibrate), width=8, height=1).grid(row=1,column=12, sticky='n')
        tk.Button(self, text="Exit", command=self._quit).grid(row=0, column=17, sticky='e')
        tk.Button(self, text="Single", command=lambda: controller.show_frame(Viewer2), width=8, height=1).grid(row=2, column=11, sticky='n')
        tk.Button(self, text="Pair", command=lambda: controller.show_frame(Viewer), width=8, height=1).grid(row=2, column=12, sticky='n')

        tk.Label(self, text="Plotter", relief='ridge').grid(row=3, column=13)
        tk.Button(self, text="Open", command=self.file_open).grid(row=4, column=14, pady=10, padx=5)
        tk.Button(self, text="Plot", command=self.plot).grid(row=6, column=13)
        
        tk.Label(self, text="Select array to plot: ").grid(row=5, column=13)
        self.listbox=tk.Listbox(self, width=8, height=1)
        self.listbox.grid(row=5, column=14, sticky='w')
        self.elements=["Za", "S11a", "S11m", "S11o", "S11l", "S11s", "Edf", "Erf", "Esf"]
        
        for i, ele in enumerate(self.elements):
            self.listbox.insert(i, ele)
        
        self.listboxopen=tk.Listbox(self, selectmode=tk.EXTENDED, height=5)
        self.listboxopen.grid(row=6, column=14, columnspan=2)
        tk.Button(self, text="Remove", command=self.listbox_delete).grid(row=4, column=15)
        self.filelist=[]
        
      #  tk.Label(self, text="Analysis", relief='ridge').grid(row=7, column=13)
      #  tk.Button(self, text="Peak", command=self.peak_finder).grid(row=8, column=14)
      #  tk.Button(self, text="+", command=lambda: self.jump_right(0)).grid(row=8, column=17, sticky='e')
      #  tk.Button(self, text="-", command=lambda: self.jump_left(0)).grid(row=8, column=18, sticky='w')
      #  tk.Button(self, text="+", command=lambda: self.jump_right(1)).grid(row=9, column=17, sticky='e')
      #  tk.Button(self, text="-", command=lambda: self.jump_left(1)).grid(row=9, column=18, sticky='w')
      #  #tk.Button(self, text='Save', command=self.saveit).grid(row=10, column=17)
      #  tk.Label(self, text="Order").grid(row=8, column=15)
      #  self.entryorder=tk.Entry(self, width=5)
      #  self.entryorder.insert(0,"20")
      #  self.entryorder.grid(row=8, column=16)
        tk.Button(self, text="Chi", command=self.chi).grid(row=13, column=14)
       
        self.circvar=tk.IntVar()
        self.squarevar=tk.IntVar()
        self.circ=tk.Checkbutton(self, text="Circular", variable=self.circvar)
        self.circ.grid(row=11, column=17)
        self.square=tk.Checkbutton(self, text="Square", variable=self.squarevar)
        self.square.grid(row=12, column=17)
        tk.Label(self, text="Sample", relief='ridge').grid(row=10, column=13)
        tk.Label(self, text="Width").grid(row=11, column=14)
        tk.Label(self, text="Thickness").grid(row=12, column=14)
        tk.Label(self, text="mm").grid(row=11, column=16, sticky='w')
        tk.Label(self, text="nm").grid(row=12, column=16, sticky='w')

        self.entrywidth = tk.Entry(self,width=5)
        self.entrywidth.insert(0, "4")
        self.entrywidth.grid(row=11, column=15)
        self.entrythick = tk.Entry(self,width=5)
        self.entrythick.insert(0, "50")
        self.entrythick.grid(row=12, column=15)

        self.fig = plt.figure(figsize=[10,9])
        gs1 = self.fig.add_gridspec(nrows=1, ncols=2, left=0.1, right=0.95, wspace=0.3)
        self.ax = self.fig.add_subplot(gs1[0,0])
        self.ax1 = self.fig.add_subplot(gs1[0,1])
        self.ax.set_xlabel('$f$ [Hz]')
        self.ax1.set_xlabel('$f$ [Hz]')
        self.ax.set_ylabel('S11 resistance [$\Omega$]')
        self.ax1.set_ylabel('S11 reactance [$\Omega$]')
        
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().grid(row=0, column=0, rowspan=100, columnspan=10, sticky='n')
        self.toolbarframe=tk.Frame(self)
        self.toolbarframe.grid(row=101, column=0, columnspan=10, sticky='nwe')
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.toolbarframe)
        self.toolbar.grid(row=102, column=0, columnspan=10, sticky='nwe')

   # def peak_finder(self):
   #     texti=pd.read_csv(self.filelist[0], index_col=False, comment= "#", sep='\t', engine='python')
   #     try:
   #         selected=self.elements[self.listbox.curselection()[0]]
   #     except:
   #         selected='Za'

   #     self.plot() 
   #     frequency=texti["freq"].to_numpy(dtype=np.complex).real
   #     real=texti[selected].to_numpy(dtype=np.complex).real
   #     imag=texti[selected].to_numpy(dtype=np.complex).imag
   #     entryorder=int(self.entryorder.get())
   #     self.peaks_real, self.peaks_imag = signal.argrelextrema(real,np.greater,order=entryorder), signal.argrelextrema(imag,np.greater,order=entryorder)
   #     self.minima_real, self.minima_imag = signal.argrelextrema(real,np.less,order=entryorder), signal.argrelextrema(imag,np.less,order=entryorder)

   #     self.ax.plot(frequency[self.peaks_real],real[self.peaks_real], 'o', frequency[self.minima_real],real[self.minima_real], 'o')
   #     self.ax.plot(frequency[self.peaks_imag],imag[self.peaks_imag], 'o', frequency[self.minima_imag],imag[self.minima_imag], 'o')
   #     
   #     self.canvas.draw()

   #def jump_right(self,dex):
        #self.ax.clear()
        #self.peak_finder()
        #if dex==1:
        #    self.indexmin=self.indexmin+1
        #elif dex==0:
        #    self.indexmax=self.indexmax+1
        #self.ax.plot(self.freq[self.peaks_real[0,self.indexmax]],self.real[self.peaks_real[0,self.indexmax]], 'x')
        #self.ax.plot(self.freq[self.minima_imag[0,self.indexmin]],self.imag[self.minima_imag[0,self.indexmin]], 'x')
        #self.canvas.draw()
  
   # def jump_left(self,dex):
        #self.ax.clear()
        #self.peak_finder()
        #if dex==1:
        #    self.indexmin=self.indexmin-1
        #elif dex==0:
        #    self.indexmax=self.indexmax-1
        #self.ax.plot(self.freq[self.peaks_real[0,self.indexmax]],self.real[self.peaks_real[0,self.indexmax]], 'x')
        #self.ax.plot(self.freq[self.minima_imag[0,self.indexmin]],self.imag[self.minima_imag[0,self.indexmin]], 'x')
        #self.canvas.draw()

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
    def reArrangeListbox(self):
        items=list(self.listboxopen.curselection())
        if not items:
            print("Nothing")
            return
        if self.direction == "up":
            for pos in items:
                if pos == 0:
                    continue
                text=self.listboxopen.get(pos)
                fileName = self.filelist[pos]
                self.filelist.pop(pos)
                self.listbox.delete(pos)
                self.filelist.insert(pos-1, fileName)
                self.listbox.insert(pos-1, text)
            self.listboxopen.selection_clear(0,self.listboxopen.size())
            self.listboxopen.selection_set(tuple([i-1 for i in items]))

        if self.direction == "dn":
            for pos in items:
                if pos ==self.listboxopen.size():
                    continue
                text=self.listboxopen.get(pos)
                fileName = self.filelist[pos]
                self.listbox.delete(pos)
                self.filelist.pop(pos)
                self.filelist.insert(pos+1, fileName)
                self.listbox.insert(pos+1, text)
            self.listboxopen.selection_clear(0,self.listboxopen.size())
            self.listboxopen.selection_set(tuple([i+1 for i in items]))
        else:
            return

    def plot(self):
        try:
            selected=self.elements[self.listbox.curselection()[0]]
        except:
            selected='Za'

        selection=self.listboxopen.curselection()
        if len(selection) > 0:
            plotlist = [item for n, item in self.filelist if n in selection]
        else:
            plotlist = self.filelist

        self.ax.clear()
        self.ax1.clear()
        self.ax.set_xlabel('$f$ [Hz]')
        self.ax.set_ylabel('Re('+selected+') [$\Omega$]')
        self.ax1.set_xlabel('$f$ [Hz]')
        self.ax1.set_ylabel('Im('+selected +') [$\Omega$]')
        for item in plotlist:
            texti=pd.read_csv(item, index_col=False, comment= "#", sep='\t', engine='python')
            x=texti['freq'].to_numpy(dtype=np.complex).real
            y=texti[selected].to_numpy(dtype=np.complex).real
            y1=texti[selected].to_numpy(dtype=np.complex).imag

            self.ax.plot(x,y)
            self.ax1.plot(x,y1)

        
        legend=[item.split('/')[-1] for item in plotlist]
        self.ax.legend(legend)
        self.canvas.draw()


    def chi(self):
        self.chi = np.zeros(nfpoints, dtype=np.complex128)

        string=self.filelist[0].rsplit('_')
        string.pop(-1)
        string.append('-0.0G.dat')
        nstring='_'
        nstring=nstring.join(string)
        filezero=pd.read_csv(nstring, index_col=False, comment='#', sep='\t', engine='python')
        Zzero=filezero['Za'].to_numpy(dtype=np.complex)

        #parameters to calc chi, susceptibility of film
        wid=float(self.entrywidth.get())*1e-3
        if int(self.circvar.get())==1 and int(self.squarevar.get())==0:
            A=np.pi*(wid/2)**2
            print('circ')
        elif int(self.squarevar.get())==1 and int(self.circvar.get())==0:
            A=wid**2
            print('square')
        else:
            print('Choose shape of sample')

        mu=np.pi*4e-7
        t=float(self.entrythick.get())*1e-9
        V=t*A
        W=16e-6
        
        selection=self.listboxopen.curselection()
        if len(selection) > 0:
            plotlist = [item for n, item in self.filelist if n in selection]
        else:
            plotlist = self.filelist

        self.ax.clear()
        self.ax1.clear()
        self.ax.set_xlabel('$f$ [Hz]')
        self.ax.set_ylabel('Re($\chi$)')
        self.ax1.set_xlabel('$f$ [Hz]')
        self.ax1.set_ylabel('Im($\chi$)')

        for item in plotlist:
            texti=pd.read_csv(item, index_col=False, comment= "#", sep='\t', engine='python')
            freq=texti['freq'].to_numpy(dtype=np.complex).real
            real=texti['Za'].to_numpy(dtype=np.complex).real
            imag=texti['Za'].to_numpy(dtype=np.complex).imag
            real=real-Zzero.real
            imag=imag-Zzero.imag
            chi=imag*W/(1*mu*V*self.freq*2*np.pi)
            chii=real*W/(1*mu*V*self.freq*2*np.pi)
            self.chi=chi+1j*chii
            self.ax.plot(freq,self.chi.real)
            self.ax1.plot(freq,self.chi.imag)
        
        legend=[item.split('/')[-1].split('.')[0]+'G' for item in plotlist]
        self.ax.legend(legend)
        self.ax1.legend(legend)
        self.canvas.draw()

class Viewer2(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        tk.Button(self, text="Measure", command=lambda: controller.show_frame(StartPage), width=8, height=1).grid(row=0,column=11,padx=5)
        tk.Button(self, text="Viewer", command=lambda: controller.show_frame(Viewer), width=8, height=1).grid(row=0,column=12)
        tk.Button(self, text="Batch", command=lambda: controller.show_frame(Batch), width=8, height=1).grid(row=1, column=11, sticky='n', padx=5)
        tk.Button(self, text="Calibrate", command=lambda: controller.show_frame(Calibrate), width=8, height=1).grid(row=1,column=12, sticky='n')
        tk.Button(self, text="Exit", command=self._quit).grid(row=0, column=17, sticky='e')
        tk.Button(self, text="Single", command=lambda: controller.show_frame(Viewer2), width=8, height=1).grid(row=2, column=11, sticky='n')
        tk.Button(self, text="Pair", command=lambda: controller.show_frame(Viewer), width=8, height=1).grid(row=2, column=12, sticky='n')

        tk.Label(self, text="Plotter", relief='ridge').grid(row=3, column=13)
        tk.Button(self, text="Open", command=self.file_open).grid(row=4, column=14, pady=10, padx=5)
        tk.Button(self, text="Plot", command=self.plot).grid(row=6, column=13)
        
        tk.Label(self, text="Select array to plot: ").grid(row=5, column=13)
        self.listbox=tk.Listbox(self, width=8, height=1)
        self.listbox.grid(row=5, column=14, sticky='w')
        self.elements=["Za", "S11a", "S11m", "S11o", "S11l", "S11s", "Edf", "Erf", "Esf"]
        
        for i, ele in enumerate(self.elements):
            self.listbox.insert(i, ele)
        
        self.listboxopen=tk.Listbox(self, selectmode=tk.EXTENDED, height=5)
        self.listboxopen.grid(row=6, column=14, columnspan=2)
        tk.Button(self, text="Remove", command=self.listbox_delete).grid(row=4, column=15)
        self.filelist=[]
        
        tk.Label(self, text="Analysis", relief='ridge').grid(row=7, column=13)
        tk.Button(self, text="Peak", command=self.peak_finder).grid(row=8, column=14)
        tk.Button(self, text="+", command=lambda: self.jump_right(0)).grid(row=8, column=17, sticky='e')
        tk.Button(self, text="-", command=lambda: self.jump_left(0)).grid(row=8, column=18, sticky='w')
        tk.Button(self, text="+", command=lambda: self.jump_right(1)).grid(row=9, column=17, sticky='e')
        tk.Button(self, text="-", command=lambda: self.jump_left(1)).grid(row=9, column=18, sticky='w')
        tk.Button(self, text='Save', command=self.saveit).grid(row=10, column=17)
        tk.Label(self, text="Order").grid(row=8, column=15)
        self.entryorder=tk.Entry(self, width=5)
        self.entryorder.insert(0,"20")
        self.entryorder.grid(row=8, column=16)
        tk.Button(self, text="Chi", command=self.chi).grid(row=13, column=14)
       
        self.circvar=tk.IntVar()
        self.squarevar=tk.IntVar()
        self.circ=tk.Checkbutton(self, text="Circular", variable=self.circvar)
        self.circ.grid(row=11, column=17)
        self.square=tk.Checkbutton(self, text="Square", variable=self.squarevar)
        self.square.grid(row=12, column=17)
        tk.Label(self, text="Sample", relief='ridge').grid(row=10, column=13)
        tk.Label(self, text="Width").grid(row=11, column=14)
        tk.Label(self, text="Thickness").grid(row=12, column=14)
        tk.Label(self, text="mm").grid(row=11, column=16, sticky='w')
        tk.Label(self, text="nm").grid(row=12, column=16, sticky='w')

        tk.Label(self, text="FWHM", relief='ridge').grid(row=14, column=14)
        self.entrysigma=tk.Entry(self, width=5)
        self.entrysigma.insert(0,"1000")
        self.entrysigma.grid(row=15, column=14)
        tk.Button(self, text='Determine', command=self.fwhm).grid(row=15, column=15)
        tk.Label(self, text="Mean").grid(row=16,column=15)
        self.entryMean=tk.Entry(self,width=8)
        self.entryMean.insert(0, "0")
        self.entryMean.grid(row=16,column=16)
        tk.Label(self, text="Amplitude").grid(row=17,column=15)
        self.entryAmpl=tk.Entry(self,width=8)
        self.entryAmpl.insert(0, "0")
        self.entryAmpl.grid(row=17,column=16)
        tk.Label(self, text='Stddev').grid(row=18,column=15)
        self.entryStd=tk.Entry(self,width=8)
        self.entryStd.insert(0, "0")
        self.entryStd.grid(row=18,column=16)

        self.entrywidth = tk.Entry(self,width=5)
        self.entrywidth.insert(0, "4")
        self.entrywidth.grid(row=11, column=15)
        self.entrythick = tk.Entry(self,width=5)
        self.entrythick.insert(0, "50")
        self.entrythick.grid(row=12, column=15)

        self.fig = plt.figure(figsize=[10,9])
        self.ax = plt.subplot()
        self.ax.set_xlabel('$f$ [Hz]')
        self.ax.set_ylabel('S11')
        
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().grid(row=0, column=0, rowspan=100, columnspan=10, sticky='n')
        self.toolbarframe=tk.Frame(self)
        self.toolbarframe.grid(row=101, column=0, columnspan=10, sticky='nwe')
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.toolbarframe)
        self.toolbar.grid(row=102, column=0, columnspan=10, sticky='nwe')

        self.indexmax=0
        self.indexmin=0
        self.peakpos=[0,0]
        self.iterator=0

    def saveit(self):
        skjal=open('/home/at/FMR/maelingar/utgildi.txt','a')
        skjal.write()

    def fwhm(self):
        self.iterator +=1
        print(self.iterator)
        dw = int((self.peaks_imag[0,self.indexmax]-self.peaks_imag[0,self.indexmax-1])/2)
        dw1 =int((self.peaks_imag[0,self.indexmax+1]-self.peaks_imag[0,self.indexmax])/2)
        if dw>dw1:
            dw=dw1
        freq=self.freq[(self.peaks_imag[0,self.indexmax]-dw):(self.peaks_imag[0,self.indexmax]+dw)]
        imag=self.imag[(self.peaks_imag[0,self.indexmax]-dw):(self.peaks_imag[0,self.indexmax]+dw)]
        shift=min(imag)
        imag=(-1)*shift+imag
        print('selfindicator:'+str(self.indicator)) 
        topindex=self.peaks_imag[0,self.indexmax]
        fitter = modeling.fitting.LevMarLSQFitter()
        model = modeling.models.Gaussian1D(amplitude=self.imag[topindex], mean=self.freq[topindex], stddev=(freq[-1]-freq[0])/2)
        if self.iterator>=2:
            model=self.fitted_model

        self.fitted_model = fitter(model, freq, imag)
        ampl=self.fitted_model.amplitude.value
        mean=self.fitted_model.mean.value
        stddev=self.fitted_model.stddev.value
        self.entryAmpl.insert(0,ampl)
        self.entryMean.insert(0,mean)
        self.entryStd.insert(0,stddev)
        self.ax.plot(freq, self.fitted_model(freq)+shift)
        self.canvas.draw()



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

        self.ax.plot(frequency[self.peaks_real],self.real[self.peaks_real], 'o')#, frequency[self.minima_real],self.real[self.minima_real], 'o')
        self.ax.plot(frequency[self.peaks_imag],self.imag[self.peaks_imag], 'o')#, frequency[self.minima_imag],self.imag[self.minima_imag], 'o')

        self.canvas.draw()
        self.peaks_real=np.array(self.peaks_real)
        self.peaks_imag=np.array(self.peaks_imag)

    def jump_right(self,dex):
        self.ax.clear()
        self.peak_finder()
        if dex==1:
            self.indexmin=self.indexmin+1
        elif dex==0:
            self.indexmax=self.indexmax+1
        self.ax.plot(self.freq[self.peaks_imag[0,self.indexmax]],self.imag[self.peaks_imag[0,self.indexmax]], 'x')
        #self.ax.plot(self.freq[self.minima_imag[0,self.indexmin]],self.imag[self.minima_imag[0,self.indexmin]], 'x')
        self.canvas.draw()
  
    def jump_left(self,dex):
        self.ax.clear()
        self.peak_finder()
        if dex==1:
            self.indexmin=self.indexmin-1
        elif dex==0:
            self.indexmax=self.indexmax-1
        self.ax.plot(self.freq[self.peaks_imag[0,self.indexmax]],self.imag[self.peaks_imag[0,self.indexmax]], 'x')
        #self.ax.plot(self.freq[self.minima_imag[0,self.indexmin]],self.imag[self.minima_imag[0,self.indexmin]], 'x')
        self.canvas.draw()

    def fit(self):
        def make_norm_dist(x,mean,sd):
            return 1.0/(sd*np.sqrt(2*np.pi))*np.exp(-(x-mean)**2/(2*sd**2))

    def chi(self):
        self.chii = np.zeros(nfpoints, dtype=np.complex128)
        string=self.filelist[0].rsplit('_')
        string.pop(-1)
        string.append('-0.0G.dat')
        nstring='_'
        nstring=nstring.join(string)
        filezero=pd.read_csv(nstring, index_col=False, comment='#', sep='\t', engine='python')
        Zzero=filezero['Za'].to_numpy(dtype=np.complex)

        self.indicator=1
        #parameters to calc chi, susceptibility of film
        wid=float(self.entrywidth.get())*1e-3
        if int(self.circvar.get())==1 and int(self.squarevar.get())==0:
            A=np.pi*(wid/2)**2
            print('circ')
        elif int(self.squarevar.get())==1 and int(self.circvar.get())==0:
            A=wid**2
            print('square')
        else:
            print('Choose shape of sample')

        mu=np.pi*4e-7
        t=float(self.entrythick.get())*1e-9
        V=t*A
        W=16e-6

        selection=self.listboxopen.curselection()
        if len(selection) > 0:
            plotlist = [item for n, item in self.filelist if n in selection]
        else:
            plotlist = self.filelist

        self.ax.clear()
        self.ax.set_xlabel('$f$ [Hz]')
        self.ax.set_ylabel('$\chi$')

        for item in plotlist:
            texti=pd.read_csv(item, index_col=False, comment= "#", sep='\t', engine='python')
            self.freq=texti['freq'].to_numpy(dtype=np.complex).real
            real=texti['Za'].to_numpy(dtype=np.complex).real
            imag=texti['Za'].to_numpy(dtype=np.complex).imag
            #real=real-Zzero.real
            #imag=imag-Zzero.imag
            chi=imag*W/(1*mu*V*self.freq*2*np.pi)
            chii=real*W/(1*mu*V*self.freq*2*np.pi)
            self.chii=chi+1j*chii
            re='Re($\chi$) '+item.split('/')[-1].split('.')[0]+'G'
            im='Im($\chi$) '+item.split('/')[-1].split('.')[0]+'G'
            self.ax.plot(self.freq,self.chii.real,label=re)
            self.ax.plot(self.freq,self.chii.imag,label=im)
        self.ax.legend()#legend)
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
    def reArrangeListbox(self):
        items=list(self.listboxopen.curselection())
        if not items:
            print("Nothing")
            return
        if self.direction == "up":
            for pos in items:
                if pos == 0:
                    continue
                text=self.listboxopen.get(pos)
                fileName = self.filelist[pos]
                self.filelist.pop(pos)
                self.listbox.delete(pos)
                self.filelist.insert(pos-1, fileName)
                self.listbox.insert(pos-1, text)
            self.listboxopen.selection_clear(0,self.listboxopen.size())
            self.listboxopen.selection_set(tuple([i-1 for i in items]))

        if self.direction == "dn":
            for pos in items:
                if pos ==self.listboxopen.size():
                    continue
                text=self.listboxopen.get(pos)
                fileName = self.filelist[pos]
                self.listbox.delete(pos)
                self.filelist.pop(pos)
                self.filelist.insert(pos+1, fileName)
                self.listbox.insert(pos+1, text)
            self.listboxopen.selection_clear(0,self.listboxopen.size())
            self.listboxopen.selection_set(tuple([i+1 for i in items]))
        else:
            return

    def plot(self):
        try:
            selected=self.elements[self.listbox.curselection()[0]]
        except:
            selected='Za'

        selection=self.listboxopen.curselection()
        if len(selection) > 0:
            plotlist = [item for n, item in self.filelist if n in selection]
        else:
            plotlist = self.filelist
        self.indicator=0
        self.ax.clear()
        self.ax.set_xlabel('$f$ [Hz]')
        self.ax.set_ylabel(selected +' [$\Omega$]')
        for item in plotlist:
            texti=pd.read_csv(item, index_col=False, comment= "#", sep='\t', engine='python')
            x=texti['freq'].to_numpy(dtype=np.complex).real
            y=texti[selected].to_numpy(dtype=np.complex).real
            y1=texti[selected].to_numpy(dtype=np.complex).imag

            #custom_lines = [plt.Line2D([0], [0]), plt.Line2D([0], [0])]
            self.ax.plot(x,y,x,y1)
            #self.ax.legend(["Re "+selected, "Im "+selected])
        legend=[item.split('/')[-1] for item in plotlist]
        self.ax.legend(legend)
        self.canvas.draw()
        

#use try here so the GUI can be used outside the experimental setup
#this sets up the connection to the network analyzer and the magnet
try:
    rm = pyvisa.ResourceManager('@py')
    inst = rm.open_resource('GPIB0::6::INSTR')
    inst.write("S11")
    inst.write("HC0") #turn of automatic IF calibration
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
    print('Network analyser is not responding')

# Comedi setup, configuration for read and write
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


if dev is None:
    errno = comedi.comedi_errno()
    print('Error (%d) %s',errno, comedi.comedi_strerror(errno))


comedi.comedi_close(dev)
app = App()
app.mainloop()
