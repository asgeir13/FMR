import numpy as np
import matplotlib.pyplot as plt
import scipy as sp
import glob 
from lmfit import Minimizer, Parameters, report_fit
from matplotlib.figure import Figure

fig = plt.figure()
ax = fig.add_subplot(1,1,1)

path = '/home/at/suscept/magnari/Mælingar/'

data = glob.glob(path+ '*.dat')
print(data[4])

f = open(data[4])

lines = (line for line in f if not line.startswith('#'))
FH = np.loadtxt(lines)

x = FH[:,1]
y = FH[:,0]
error = FH[:,2]
 
plt.plot(x,y,'k.')
plt.errorbar(x,y,yerr=None,xerr=error, ls='none')

def fcn2min(params, x,y): 
    h = params['h']
    q = params['q']
    
    Y = h*x + q
    resids = Y - y
    weighted = resids ** 2 / error ** 2
    return weighted

params = Parameters()
params.add('h',value=20)
params.add('q',value=2060)

#print(f'weighted {fcn2min(params,x,y)}')

minner = Minimizer(fcn2min, params, fcn_args=(x,y)) #,scale_covar=False)
result = minner.minimize()
final = y + result.residual

report_fit(result)

plt.plot(x,x*result.params['h'].value + result.params['q'].value,'r-')

# Limit the range of the plot t 

#plt.xlim(0,100)        # Val á kvarðabili
#plt.ylim(0,12)

plt.yticks(fontsize=12)     #Leturstærð á kvarða   
plt.xticks(fontsize=12) 

plt.xlabel('Segulflæðisþéttleiki (G)',fontsize=14)#,color='r')     #Leturstærð og litur í nafni ása
plt.ylabel('Spennu inntak ',fontsize=14)

plt.draw()
plt.pause(10) # <-------
























