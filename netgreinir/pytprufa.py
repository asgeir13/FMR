import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import time




x=y=z = np.arange(0.0,5.0,1.0)

#np.savetxt('test.out', x, delimiter=',')   # X is an array
np.savetxt('test.out', (x,y,z))   # x,y,z equal sized 1D arrays
#np.savetxt('test.out', x, fmt='%1.4e')   # use exponential notation11=[0+1j*3,2+1j,3+1j,1+1j,4+1j,3+1j,2+1j,3+1j,5+1j,6+1j,5+1j,2+1j]


