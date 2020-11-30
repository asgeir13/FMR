import tkinter as tk
from tkinter.constants import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)




def plot():
    fig = Figure(figsize = (5, 5), dpi = 100)
    
    y = [i**2 for i in range(101)]

    plot1 = fig.add_subplot(111)
    plot1.plot(y)

    canvas = FigureCanvasTkAgg(fig, master = tkint)
    canvas.draw()


    canvas.get_tk_widget().pack()
    toolbar = NavigationToolbar2Tk(canvas, tkint)
    toolbar.update()

    canvas.get_tk_widget().pack()

tkint = tk.Tk()


frame_a = tk.Frame()
frame_b = tk.Frame()

def handle_click():
    print("The button was clicked!")


entry=tk.Entry(master=frame_a, width=40, bg="white", fg="black")
entry.pack()
entry.insert(0,"Hello")

button = tk.Button(master=frame_b, text="Click me!", command=plot, width=25,height=5, bg="green")
button.pack()



frame_b.pack()
frame_a.pack()
tkint.mainloop()

