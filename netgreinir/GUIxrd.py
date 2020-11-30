import os, sys, platform
import Tkinter as tk
import ttk
from tkFileDialog import askopenfilenames
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg, NavigationToolbar2Tk
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

#import matplotlib.animation as animation
from matplotlib import style
style.use("seaborn-muted")
import xrdTools as xt
import numpy as np

# Stuff to fix pyinstaller
import periodic
#from periodic import _dtype_ctypes
import sqlalchemy
import sqlite3

# build using
# python oldsetup.py py2app --packages sqlalchemy,periodic,periodictable,sqlite3

dpi=100
fileList=[] # Preallocate a list, so its always a list

f,_,_ = xt.view(fileList,draw=True)

#legend=""
#scale="log"
#shift=1
icon = "favicon_16x16.ico"
myos = platform.system()
if myos == "Windows":
    osdir = os.environ['HOMEPATH']
else: 
    osdir = os.environ['HOME']
settings = {
        "scale": "linear",
        "shift": float(0),
        "legend": "on",
        "customLegend": "",
        }

def _quit():
    app.quit()     # stops mainloop
    app.destroy()  # this is necessary on Windows to prevent
                    # Fatal Python Error: PyEval_RestoreThread: NULL tstate

def OpenFile(listbox):
    global fileList, osdir
    newList = askopenfilenames(initialdir=osdir,title="Select file")
    fileList.extend(list(newList)) # Extend adds elements at the end of list
    listbox.delete(0,listbox.size())
    for i in range(len(fileList)):
        listbox.insert(i, fileList[i].split('/')[-1])

def refresh_list(listbox):
    global fileList
    item=""
    for i in fileList:
        item=i.split('/')
        listbox.insert(tk.END, item[-1])

def listbox_delete(listbox):
    global fileList
    END = listbox.size()
    removeList = get_selection(listbox)
    fileList = [item for item in fileList if item not in removeList] # List comprehension
    listbox.delete(0, END)
    for i in range(len(fileList)):
        listbox.insert(i, fileList[i].split('/')[-1])

def get_selection(listbox):
    # Returns a list of indexes which are selected in the listbox
    selection = []
    for i in range(listbox.size()):
        if listbox.select_includes(i) == True:
            selection.append(i)
    newFileList = [fileList[i] for i in range(len(fileList)) if i in selection]
    print newFileList
    return newFileList

def Plotting(canvas, figure, listbox):
    global fileList, settings
    figWidth = 900
    scale = settings["scale"]
    shift = settings["shift"]
    legend = settings["legend"]
    customLegend = settings["customLegend"]
    
    selection = get_selection(listbox)
    if len(selection) > 0: # Plot things highlighted in listbox
        plotList = selection
    else: # Plot all files in listbox
        plotList = fileList
    length=len(plotList)
    try:
        global a
        a.clear()
        f,a,props = xt.view(plotList, figWidth=figWidth, fig=figure, ax=a, scale=scale, shift=shift, draw=True, legend=legend, customLegend=customLegend)
    except:
        f,a,props = xt.view(plotList, figWidth=figWidth,fig=figure, scale=scale, shift=shift, draw=True, legend=legend, customLegend=customLegend)
    canvas.draw()

def popup_bonus(parent, canvas):
    global settings
    parent.update()
    win = tk.Toplevel()
    win.wm_title("Graph Settings")
    x1,y1 = parent.winfo_width(), parent.winfo_height()  # Top right corner of parent window
    x,y = parent.winfo_rootx(), parent.winfo_rooty()
    w,h = 220,350
    win.geometry('%dx%d+%d+%d' % (w, h, x+x1, y-22.))

    # Create text items
    i = 0
    for item in ['shift','scale','legend','custom legend']:# settings.keys():
        l = tk.Label(win, text=item.capitalize())
        l.grid(row=i, column=0,sticky='e')
        i+=1
    
    # Create entry boxes
    shiftBox=tk.Entry(win, width=10)
    shiftBox.insert(0, '0')
    shiftBox.grid(row=0, column=1, columnspan=2,sticky='w') 

    
    scaleValue = tk.StringVar(None, 'linear')
    scaleRadOn = ttk.Radiobutton(win, text='Linear',variable=scaleValue, value='linear')
    scaleRadOff = ttk.Radiobutton(win, text='Log',variable=scaleValue, value='log')
    scaleRadOn.grid(row=1, column=1,sticky='w')
    scaleRadOff.grid(row=1, column=2,sticky='w')

    legendValue = tk.StringVar(None,'on')
    legRadOn = ttk.Radiobutton(win, text='On',variable=legendValue, value='on')
    legRadOn.grid(row=2, column=1,sticky='w')
    legRadOff = ttk.Radiobutton(win, text='Off',variable=legendValue, value='off')
    legRadOff.grid(row=2, column=2,sticky='w')

    def updateSettings():
        settings["shift"] = float(shiftBox.get())
        settings["legend"] = legendValue.get()
        settings["scale"]  = scaleValue.get()
        print(customLegend.get())
        if customLegend.get() == True:
            settings["customLegend"] = [ legend.get() for legend in legBoxes ]
        else:
            settings["customLegend"] = None
    
    legBoxes = []
    customLegend = tk.BooleanVar(0,False)
    btn=tk.Checkbutton(win, variable=customLegend,command=lambda: enableCustomLegend(legBoxes))
    btn.grid(row=3,column=1,sticky='w')

    def enableCustomLegend(legBoxes):
        if customLegend.get() == True:
            try:
                n = len(selection)
            except:
                n = len(fileList)
                
            for i in range(0,n):
                l = ttk.Label(win, text="Scan %i entry" % (i,))
                l.grid(row=4+i, column=0, sticky='w')
                entr = ttk.Entry(win, width=10)
                entr.grid(row=4+i, column=1, columnspan=2, sticky='w')
                legBoxes.append(entr)
        
    applyButton = ttk.Button(win, text="Apply", command=lambda: [updateSettings(), replot(canvas,f,listbox)] ) 
    applyButton.grid(row=100, column=0, sticky='s')
    if myos != "Darwin":
        app.iconbitmap(icon)
def replot(canvas,f,listbox):
    global settings
    Plotting(canvas, f, listbox)

class Viewer(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.wm_title(self, "Grein Research XRD Viewer")
        container=tk.Frame(self, width=1.67*600, height=600, bg='white')
        container.pack(side="top", fill="both", expand = True)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)

        frame=StartPage(container, self)
        frame.grid(row=0, column=0, sticky="news")
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        frame.tkraise()
        
        # Initial window is 16/9 aspect ratio
        # with a width of 800 pixels
        x, y = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry("%dx%d+%d+%d" % (800,450,x/2-800/2,y/2-450/2))


class StartPage(tk.Frame):
    
    def __init__(self, parent,controller,*pargs):
        global listbox, settings
        
        tk.Frame.__init__(self,parent,*pargs)
    
        button1 = ttk.Button(self, text="Open", command=lambda: OpenFile(listbox))
        button1.grid(row=0, column=6, sticky='s')
        
        canvas = FigureCanvasTkAgg(f, master=self)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, columnspan=6, rowspan=3, sticky='news')
        canvas.get_tk_widget().grid_columnconfigure(0, weight=2)
        canvas.get_tk_widget().grid_rowconfigure(0, weight=2)

        def mouseClick(event):         
            print("You clicked on x:%.4f y:%.4f" % (event.xdata, event.ydata))
        
        cid = f.canvas.mpl_connect('button_press_event', mouseClick)

        toolbarFrame = tk.Frame(self)
        toolbarFrame.grid(row=3, column=0, columnspan=4,sticky='w')
        toolbar = NavigationToolbar2Tk(canvas, toolbarFrame)

        label=tk.Label(self, text="List of xrdml files:")
        label.grid(row=1, column=6, sticky='we')
        listbox=tk.Listbox(self, selectmode=tk.EXTENDED)
        listbox.grid(row=2, column=6, columnspan=2)

        button_del=ttk.Button(self, text="Delete", command=lambda listbox=listbox: listbox_delete(listbox) ) 
        button_del.grid(row=3, column=7)
        
        button2 = ttk.Button(self, text="Plot", command=lambda: Plotting(canvas,f,listbox))
        button2.grid(row=0, column=7, sticky='s')
        
        button3 = ttk.Button(self, text="Quit", command=_quit)
        button3.grid(row=6, column=7)

        button4= ttk.Button(self, text="Settings", command=lambda: popup_bonus(self,canvas))
        button4.grid(row=5, column=7)
        
app = Viewer()
print("You're running %s" % (myos,))
if myos != "Darwin":
    app.iconbitmap(icon)
app.mainloop()



## More stuff
# def onclick(event):
#        point = event.artist
#        coords = point.get_data()
#        xrdCoords = projectToXRD(coords)
#        idx = find_concentration(P, coords)
#        if idx != -1:
#            conc = c[:,idx]*100
#            print("Concentration in point (%.0f, %.0f)\nOr in XRD Projection (%.0f, %.0f):\n\t%s: %.0f\n\t%s: %.0f\n\t%s: %.0f" % (coords[0],coords[1],xrdCoords[0],xrdCoords[1],elements[0],conc[0],elements[1],conc[1],elements[2],conc[2]))
##        else: 
#           print("No data recovered")
#        # Click on image for atomic concentration
#        #print('Atomic Concentration at: X=%.2fmm and Y=%.2fmm is ' %
#        #  (event.xdata,event.ydata))

#        return

#    cid = f.canvas.mpl_connect('pick_event',onclick)

