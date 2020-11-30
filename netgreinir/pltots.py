import time
import matplotlib.pyplot as plt
import numpy as np
plt.ion()
start="0.00"
stop="100.00"
print(start, stop)
start=float(start)
stop=float(stop)
print(start, stop)

vector=np.linspace(start, stop)
print(vector)


fig, ax = plt.subplots()
th = np.linspace(0, 2*np.pi, 512)
ax.set_ylim(-1.5, 1.5)

ln, = ax.plot(th, np.sin(th))

def slow_loop(N, ln):
    for j in range(N):
        time.sleep(.1)  # to simulate some work
        if j % 10:
            ln.set_ydata(np.sin(((j // 10) % 5 * th)))
            ln.figure.canvas.draw_idle()

        ln.figure.canvas.flush_events()

slow_loop(80, ln)
