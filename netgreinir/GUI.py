import comedi
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





#App class makes the frames and allows easy switching between them
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
        for F in (StartPage, Calibrate, Batch, Viewer):

            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row = 0, column = 0, sticky="nsew")

        self.show_frame(StartPage)
    #raises the page to the top with tkraise()
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


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

        tk.Button(self, text="Reset", command=lambda: self.zerofield("par")).grid(row=4, column=17)
        tk.Button(self, text="Set", command=lambda: self.writevolt("par"), width=1).grid(row=4, column=16, sticky='e')

        tk.Label(self, text="Perpendicular").grid(row=5,column=13)
        self.entryper = tk.Entry(self,width=5)
        self.entryper.insert(0, "0")
        self.entryper.grid(row=5, column=14)
        tk.Label(self, text="G ").grid(row=5, column=15,sticky='w')

        tk.Button(self, text="Reset", command=lambda: self.zerofield("per")).grid(row=5, column=17)
        tk.Button(self, text="Set", command=lambda: self.writevolt("per"), width=1).grid(row=5, column=16, sticky='e')
        
    def _quit(self):
        app.quit()
        app.destroy()
    
    def stop_run(self):
        self.run=False

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
        self.run=True
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
        self.ax.plot(self.freq, self.Za.real)
        self.ax1.plot(self.freq, self.Za.imag)
        self.canvas.draw_idle()
        self.canvas.flush_events()
        for n in range(nave):
            if self.run==False:
                break
            
            real_p, imag_p, self.freq=self.measure()
            self.S11m=(self.S11m*(n+1)+real_p+1j*imag_p)/(n+2) #averaging with each iteration
            self.docal()
            self.ax.clear()
            self.ax1.clear()
            self.ax.set_xlabel('$f$ [Hz]')
            self.ax1.set_xlabel('$f$ [Hz]')
            self.ax.set_ylabel('$Z_a$ resistance [$\Omega$]')
            self.ax1.set_ylabel('$Z_a$ reactance [$\Omega$]')
            self.ax.plot(self.freq, self.Za.real)
            self.ax1.plot(self.freq, self.Za.imag)
            self.canvas.draw_idle() #draw_idle is a gentle way to draw, it doesn't interupt the GUI
            self.canvas.flush_events()
        print('Measurement complete')


        #saves all the arrays, only applicable after running the docal function
    def file_save(self):
        f = tk.filedialog.asksaveasfile(mode="w", defaultextension="*.txt")
        intro="#FMR data, this file includes calibration measurements, correction factor and corrected S11\n"
        intro1="freq\tS11a\tS11m\tS11o\tS11l\tS11s\tZa\tEdf\tErf\tEsf\n"
        dataout=np.column_stack((self.freq, self.S11a, self.S11m, S11o, S11l, S11s, self.Za, self.Edf, self.Erf, self.Esf))
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
        fre_val=inst.read("\n")
        fre_val=fre_val.rsplit(", ")
        new_fre_val=fre_val[0].rsplit(" ")
        new_fre_val.extend(fre_val[1:])
        new_fre_val=[float(n) for n in new_fre_val[1:]]

        inst.write("OFD") #requesting the S11 measurements, this returns the real and imag part
        valu=inst.read("\n")
        valu=valu.rsplit(",")
        new_valu=valu[0].rsplit(" ")
        new_valu.extend(valu[1:])
        new_valu=[float(n) for n in new_valu[1:]]
        real_part=imag_part=np.arange(len(new_fre_val),dtype=np.float64)

        real_part=np.array(new_valu[0:-1:2]) #the complex values are given in pairs
        imag_part=new_valu[1:-1:2]
        imag_part.append(new_valu[-1])
        imag_part=np.array(imag_part)
        return real_part, imag_part, new_fre_val

        #this function measures multiple times by calling the measure funtion, it is called nave times
        #which is the number of averages
    #set the magnetic field. FH are values read from a calibration file, which can be updated 
    def writevolt(self, direction):
        dev = comedi.comedi_open("/dev/comedi0")
        if direction=="par":
            val = self.entrypar.get()
            val = float(val)*FH1[0]+FH1[1]
            chan=chanw
        elif direction=="per":
            val = self.entryper.get()
            val = float(val)*FH[0]+FH[1]
            chan=chanw1

        val = int(np.around(val))
        if val < 0 and val > 4095:
            val = datazero
            print('Input value not available')
        retvalw = comedi.comedi_data_write(dev, subdevw, chan, rngw, aref, val)
        comedi.comedi_close(dev)
        print(f"Value set to: {val}")
    
    #reset the magnet
    def zerofield(self, direction):
        if direction=="per":
            self.entryper.delete(0, END)
            self.entryper.insert(0, "0")
            chan=chanw1
        elif direction=="par":
            self.entrypar.delete(0, END)
            self.entrypar.insert(0, "0")
            chan=chanw
            
        dev = comedi.comedi_open("/dev/comedi0")
        retval = comedi.comedi_data_write(dev, subdevw, chan, rngw, aref, datazero)
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

        tk.Button(self, text="Reset", command=lambda: self.zerofield("par")).grid(row=4, column=17)
        tk.Button(self, text="Set", command=lambda: self.writevolt("par"), width=2).grid(row=4, column=16, sticky='e')

        tk.Label(self, text="Perpendicular").grid(row=5,column=13)
        self.entryper = tk.Entry(self,width=5)
        self.entryper.insert(0, "0")
        self.entryper.grid(row=5, column=14)
        tk.Label(self, text="G").grid(row=5, column=15,sticky='w')

        tk.Button(self, text="Reset", command=lambda: self.zerofield("per")).grid(row=5, column=17)
        tk.Button(self, text="Set", command=lambda: self.writevolt("per"), width=2).grid(row=5, column=16,sticky='e')

        tk.Label(self, text="Sweep setup").grid(row=7, column=13)

        tk.Label(self, text="Start").grid(row=8, column=13)
        self.startentry=tk.Entry(self, width=5)
        self.startentry.insert(0, "40")
        self.startentry.grid(row=8, column=14)
        tk.Label(self, text="MHz").grid(row=8, column=15)

        tk.Label(self, text="Stop").grid(row=9, column=13)
        self.stopentry=tk.Entry(self, width=5)
        self.stopentry.insert(0, "10000")
        self.stopentry.grid(row=9, column=14)
        tk.Label(self, text="MHz").grid(row=9, column=15)

        tk.Label(self, text="Nr. of meas.").grid(row=11, column=13)
        self.numberentry=tk.Entry(self, width=5)
        self.numberentry.insert(0, "10")
        self.numberentry.grid(row=11, column=14)

        tk.Label(self, text="Data points").grid(row=12,column=13)
        self.pointsbox=tk.Entry(self, width=6)
        self.pointsbox.insert(0, "401")
        self.pointsbox.grid(row=12, column=14)
        self.pointlist=["51", "101", "201", "401", "801", "1601"]
        tk.Button(self, text="+", command=lambda: self._up(0), width=1, height=1).grid(row=12, column=15)
        tk.Button(self, text="-", command=lambda: self._down(0), width=1, height=1).grid(row=12,column=16)

        tk.Label(self, text="IF BW").grid(row=13, column=13)
        self.IF_list=["10 Hz", "100 Hz", "1 kHz", "10 kHz"]
        self.IF_BW=tk.Entry(self,width=6)
        self.IF_BW.insert(0,"1 kHz")
        self.IF_BW.grid(row=13, column=14)
        tk.Button(self, text="+", command=lambda: self._up(1), width=1, height=1).grid(row=13, column=15)
        tk.Button(self, text="-", command=lambda: self._down(1), width=1, height=1).grid(row=13,column=16)
        tk.Button(self, text="Set values", command=self.set_values).grid(row=8, column=16, columnspan=3)
    
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
       
        inst.write("IF"+str(int(self.IF_list.index(self.IF_BW.get())+1)))

        inst.write("NP"+self.pointsbox.get())

        nave=int(self.numberentry.get())-1
        print(nave)

 #set the magnetic field. FH are values read from a calibration file, which can be updated 
    def writevolt(self, direction):
        dev = comedi.comedi_open("/dev/comedi0")
        if direction=="par":
            val = self.entrypar.get()
            val = float(val)*FH1[0]+FH1[1]
            chan=chanw
        elif direction=="per":
            val = self.entryper.get()
            val = float(val)*FH[0]+FH[1]
            chan=chanw1

        val = int(np.around(val))
        if val < 0 and val > 4095:
            val = datazero
            print('Input value not available')
        retvalw = comedi.comedi_data_write(dev, subdevw, chan, rngw, aref, val)
        comedi.comedi_close(dev)
        print(f"Value set to: {val}")
    
    #reset the magnet
    def zerofield(self, direction):
        if direction=="per":
            self.entryper.delete(0, END)
            self.entryper.insert(0, "0")
            chan=chanw1
        elif direction=="par":
            self.entrypar.delete(0, END)
            self.entrypar.insert(0, "0")
            chan=chanw
            
        dev = comedi.comedi_open("/dev/comedi0")
        retval = comedi.comedi_data_write(dev, subdevw, chan, rngw, aref, datazero)
        print(f'Resetting DAQs to zero: {retval}')
        comedi.comedi_close(dev)
  
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
        fre_val=inst.read("\n")
        fre_val=fre_val.rsplit(", ")
        new_fre_val=fre_val[0].rsplit(" ")
        new_fre_val.extend(fre_val[1:])
        new_fre_val=[float(n) for n in new_fre_val[1:]]

        inst.write("OFD") #requesting the S11 measurements, this returns the real and imag part
        valu=inst.read("\n")
        valu=valu.rsplit(",")
        new_valu=valu[0].rsplit("-")
        if len(new_valu)==3:
            new_valu[2]='-'+new_valu[1]+'-'+new_valu[2]
            print(new_valu)
            new_valu.extend(valu[1:])
            new_valu=[float(n) for n in new_valu[2:]]
            print(new_valu)
        else:
            new_valu=valu[0].rsplit(" ")
            new_valu.extend(valu[1:])
            new_valu=[float(n) for n in new_valu[1:]]
            print(new_valu)
        real_part=imag_part=np.arange(len(new_fre_val),dtype=np.float64)

        real_part=np.array(new_valu[0:-1:2]) #the complex values are given in pairs
        imag_part=new_valu[1:-1:2]
        imag_part.append(new_valu[-1])
        #real_part=np.array(new_valu[0:401])
        #imag_part=np.array(new_valu[401:802])
        imag_part=np.array(imag_part)
        return real_part, imag_part, new_fre_val

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
        for n in range(nave):
            real_p, imag_p, self.freq=self.measure()
            self.S11m=(self.S11m*(n+1)+real_p+1j*imag_p)/(n+2) #averaging with each iteration
            self.ax.clear()
            self.ax1.clear()
            self.ax.set_xlabel('$f$ [Hz]')
            self.ax1.set_xlabel('$f$ [Hz]')
            self.ax.set_ylabel('S11 resistance [$\Omega$]')
            self.ax1.set_ylabel('S11 reactance [$\Omega$]')
            self.ax.plot(self.freq, self.S11m.real)
            self.ax1.plot(self.freq, self.S11m.imag)
            self.canvas.draw_idle() #draw_idle is a gentle way to draw, it doesn't interupt the GUI
            self.canvas.flush_events()
        print('Measurement complete')   



class Batch(tk.Frame):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)
        tk.Button(self, text="Measure", command=lambda: controller.show_frame(StartPage), width=8, height=1).grid(row=0,column=11,padx=5)
        tk.Button(self, text="Viewer", command=lambda: controller.show_frame(Viewer), width=8, height=1).grid(row=0,column=12)
        tk.Button(self, text="Batch", command=lambda: controller.show_frame(Batch), width=8, height=1).grid(row=1, column=11, sticky='n', padx=5)
        tk.Button(self, text="Calibrate", command=lambda: controller.show_frame(Calibrate), width=8, height=1).grid(row=1,column=12, sticky='n')
        tk.Button(self, text="Exit", command=self._quit).grid(row=0, column=17,sticky='e')

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
        tk.Label(self, text="Start").grid(row=4, column=13)
        self.entrystart = tk.Entry(self,width=5)
        self.entrystart.insert(0, "0")
        self.entrystart.grid(row=4, column=14)
        tk.Label(self, text="G").grid(row=4, column=15,sticky='w')
        tk.Label(self, text="Stop").grid(row=5, column=13)
        self.entrystop = tk.Entry(self,width=5)
        self.entrystop.insert(0, "0")
        self.entrystop.grid(row=5, column=14)
        tk.Label(self, text="G").grid(row=5, column=15,sticky='w')
        tk.Label(self,text="Step").grid(row=6,column=13)
        self.entrystep = tk.Entry(self, width=5)
        self.entrystep.insert(0,"0")
        self.entrystep.grid(row=6, column=14)
        tk.Label(self,text="G").grid(row=6, column=15)

        tk.Button(self, text="Calc", command=self.calcvect).grid(row=7, column=13,sticky='e')
        tk.Button(self, text="Scan", command=self.batchscan).grid(row=8, column=13,sticky='e')
        tk.Button(self, text="Save", command=self.file_save).grid(row=7, column=14)
        tk.Button(self, text="Stop", command=self.stop_run).grid(row=8, column=14)
    
    def stop_run(self):
        self.run=False

    def _quit(self):
        app.quit()
        app.destroy()

    def calcvect(self):
        try:
            step = self.entrystep.get()
            self.values=np.arange(float(self.entrystart.get()), float(self.entrystop.get())+float(step), float(step))
            print(self.values)
        except:
            print('Dividing by zero')

    def batchscan(self):
        self.run=True
        
        for i, item in enumerate(self.values):
            if self.run == False:
                self.zerofield("per")
                self.zerofield("par")
                break

            self.val=self.values[i]
            self.writevolt("par")
            self.takecal()

            if i ==0:
                self.array=np.column_stack((self.S11a, self.Za, self.S11m))
            else:
                self.array=np.column_stack((self.array, self.S11a, self.Za, self.S11m))

        print('done')
        self.zerofield("per")
        self.zerofield("par")
    
 #set the magnetic field. FH are values read from a calibration file, which can be updated 
    def writevolt(self, direction):
        dev = comedi.comedi_open("/dev/comedi0")
        if direction=="par":
            val = float(self.val)*FH1[0]+FH1[1]
            chan=chanw
        elif direction=="per":
            val = float(self.val)*FH[0]+FH[1]
            chan=chanw1

        val = int(np.around(val))
        if val < 0 and val > 4095:
            val = datazero
            print('Input value not available')
        retvalw = comedi.comedi_data_write(dev, subdevw, chan, rngw, aref, val)
        comedi.comedi_close(dev)
        print(f"Value set to: {val}")
    
    #reset the magnet
    def zerofield(self, direction):
        if direction=="per":
            chan=chanw1
        elif direction=="par":
            chan=chanw
            
        dev = comedi.comedi_open("/dev/comedi0")
        retval = comedi.comedi_data_write(dev, subdevw, chan, rngw, aref, datazero)
        print(f'Resetting DAQs to zero: {retval}')
        comedi.comedi_close(dev)
       
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
        fre_val=inst.read("\n")
        fre_val=fre_val.rsplit(", ")
        new_fre_val=fre_val[0].rsplit(" ")
        new_fre_val.extend(fre_val[1:])
        new_fre_val=[float(n) for n in new_fre_val[1:]]

        inst.write("OFD") #requesting the S11 measurements, this returns the real and imag part
        valu=inst.read("\n")
        valu=valu.rsplit(",")
        new_valu=valu[0].rsplit(" ")
        new_valu.extend(valu[1:])
        new_valu=[float(n) for n in new_valu[1:]]
        print(len(new_valu))
        real_part=imag_part=np.arange(len(new_fre_val),dtype=np.float64)

        real_part=np.array(new_valu[0:-1:2]) #the complex values are given in pairs
        imag_part=new_valu[1:-1:2]
        imag_part.append(new_valu[-1])
        imag_part=np.array(imag_part)
        #real_part=np.array(new_valu[0:401])
        #imag_part=np.array(new_valu[401:802])
        return real_part, imag_part, new_fre_val

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
        self.ax.plot(self.freq, self.Za.real, label=str(self.val))
        self.ax.legend()
        self.ax1.plot(self.freq, self.Za.imag, label=str(self.val))
        self.ax1.legend()
        self.canvas.draw_idle()
        self.canvas.flush_events()
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
            self.ax.plot(self.freq, self.Za.real, label=str(self.val))
            self.ax.legend()
            self.ax1.plot(self.freq, self.Za.imag, label=str(self.val))
            self.ax1.legend()
            self.canvas.draw_idle() #draw_idle is a gentle way to draw, it doesn't interupt the GUI
            self.canvas.flush_events()
        print('Measurement complete')   

    def file_save(self):
        filename = tk.filedialog.asksaveasfilename(defaultextension="*.txt")
        intro=f'''#FMR data from {datetime.datetime.now()}, this file includes calibration measurements, correction factor and corrected S11
freq\tS11o\tS11l\tS11s\tEdf\tErf\tEsf\tS11a\tZa\tS11m'''
        #fmt=['%.5e', '%.5e %+.5ej', '%.5e %+.5ej', '%.5e %+.5ej', '%.5e %+.5ej', '%.5e %+.5ej', '%.5e %+.5ej', '%.5e %+.5ej', '%.5e %+.5ej', '%.5e %+.5ej']
        fmt='%.5e'
        dataout=np.column_stack((self.freq, S11o, S11l, S11s, Edf, Erf, Esf))
        for i, n in enumerate(self.values):
            looparray=np.column_stack((dataout, self.array[:,i*3:(i*3+3)]))
            np.savetxt(filename.rsplit('.')[0]+str(n)+'G.dat', looparray, delimiter='\t', header=intro, fmt=fmt, comments='')
        
        #Viewer to analyze data
class Viewer(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        tk.Button(self, text="Measure", command=lambda: controller.show_frame(StartPage), width=8, height=1).grid(row=0,column=11,padx=5)
        tk.Button(self, text="Viewer", command=lambda: controller.show_frame(Viewer), width=8, height=1).grid(row=0,column=12)
        tk.Button(self, text="Batch", command=lambda: controller.show_frame(Batch), width=8, height=1).grid(row=1, column=11, sticky='n', padx=5)
        tk.Button(self, text="Calibrate", command=lambda: controller.show_frame(Calibrate), width=8, height=1).grid(row=1,column=12, sticky='n')
        tk.Button(self, text="Exit", command=self._quit).grid(row=0, column=17, sticky='e')

        tk.Button(self, text="open", command=self.file_open).grid(row=2, column=13, pady=10, padx=5)
        tk.Button(self, text="plot", command=self.plot).grid(row=2, column=14)

        tk.Label(self, text="Select array to plot: ").grid(row=3, column=13)
        self.listbox=tk.Listbox(self, width=8, height=3)
        self.listbox.grid(row=4, column=13)
        self.elements=["Za", "S11a", "S11m", "S11o", "S11l", "S11s", "Edf", "Erf", "Esf"]
        for i, ele in enumerate(self.elements):
            self.listbox.insert(i, ele)
        
        self.listboxopen=tk.Listbox(self, selectmode=tk.EXTENDED, height=5)
        self.listboxopen.grid(row=4, column=14)
        tk.Button(self, text="Remove", command=self.listbox_delete).grid(row=5, column=13)
        self.filelist=[]

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

    def _quit(self):
        app.quit()
        app.destroy()

        #creates a list of .dat files to plot
    def file_open(self):

        t=tk.filedialog.askopenfilenames()
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
        selected=self.elements[self.listbox.curselection()[0]]
        selection=self.listboxopen.curselection()
        if len(selection) > 0:
            plotlist = [item for n, item in self.filelist if n in selection]
        else:
            plotlist = self.filelist

        self.ax.clear()
        self.ax1.clear()
        self.ax.set_xlabel('$f$ [Hz]')
        self.ax1.set_xlabel('$f$ [Hz]')
        self.ax.set_ylabel('S11 resistance [$\Omega$]')
        self.ax1.set_ylabel('S11 reactance [$\Omega$]')
        for item in plotlist:
            texti=pd.read_csv(item, index_col=False, comment= "#", sep='\t', engine='python')
            print(texti['freq'])
            self.ax.plot(texti['freq'].to_numpy(dtype=np.complex).real, texti[selected].to_numpy(dtype=np.complex).real, label=item.split('/')[-1])
            self.ax.legend()
            self.ax1.plot(texti['freq'].to_numpy(dtype=np.complex).real, texti[selected].to_numpy(dtype=np.complex).imag, label=item.split('/')[-1])
            self.ax1.legend()
            print(item)

        self.canvas.draw()

    def chi(self):
        infstruct=[] #takes multiple measurements of the same material, but with differing thickness
        f=[] #is the frequency, assumed to be the same in each scan
        S=[] # is the S11 reflection parameter

        chi=[] #array that contains the complex susceptibility matrix(no normalization)
        cz=[] #complex uncorrected Z(impedance)

        nfiles=[] #number of files that contain scans that are read
        Z=50*(1+S)/(1-S)
        for n in np.arange(len(nfiles)):
            cz.append(Z[:,n+1]-Z[:,1])

        #parameters to calc chi, susceptibility of film
        wid=[] #width of fixture in m
        A=[] # 


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
savelist=[]

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
except:
    print('Network analyser is not responding')

# Comedi setup, configuration for read and write
try:
    subdevr, chanr, rngr, aref = 0, 0, 1, comedi.AREF_GROUND
    subdevw, chanw, chanw1, rngw, = 1, 0, 1, 0
    datazero, datawmax = 2048, 4095
    devname="/dev/comedi0"
    dev = comedi.comedi_open(devname)
    path = f=open('/home/at/suscept/magnari/Mælingar/calib_results.dat')
    lines = (line for line in f if not line.startswith('#'))
    FH = np.loadtxt(lines)
    path = f=open('/home/at/suscept/magnari/Mælingar/calib_results_Ls.dat')
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
