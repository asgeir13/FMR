import numpy as np
import matplotlib.pyplot as plt
import scipy as sp
import glob 
from lmfit import Minimizer, Parameters, report_fit
from matplotlib.figure import Figure

fig = plt.figure()
ax = fig.add_subplot(2,1,1)
ax1 = fig.add_subplot(2,1,2)
path = '/home/at/suscept/magnari/Mælingar/'

data = glob.glob(path+ '*.dat')
print(data[3])

f = open(data[3])

lines = (line for line in f if not line.startswith('#'))
FH = np.loadtxt(lines)

x = FH[:,0]
B_ramp_disp = FH[:,1]
B_disp = FH[:,2]
B_ramp = FH[:,3]*100
B = FH[:,4]*100

#ax.plot(x,B_ramp_disp,x,B_ramp, 'k.')
#ax1.plot(x,B_disp,x,B, 'k.')
ax.plot(B_ramp,B_ramp_disp,'k.')
ax1.plot(B,B_disp,'g.')


def fcn2min(params, x,y): 
    h = params['h']
    q = params['q']
    
    Y = h*x + q
    resids = Y - y
    weighted = abs(resids) 
    return weighted

params = Parameters()
params.add('h',value=1)
params.add('q',value=1)

#print(f'weighted {fcn2min(params,x,y)}')
minner_ramp_disp = Minimizer(fcn2min, params, fcn_args=(B_ramp,B_ramp_disp)) #,scale_covar=False)
result_ramp_disp = minner_ramp_disp.minimize()
final_ramp_disp = B_ramp_disp + result_ramp_disp.residual

#minner_ramp = Minimizer(fcn2min, params, fcn_args=(x,B_ramp)) #,scale_covar=False)
#result_ramp = minner_ramp.minimize()
#final_ramp = B_ramp + result_ramp.residual

minner_disp = Minimizer(fcn2min, params, fcn_args=(B,B_disp)) #,scale_covar=False)
result_disp = minner_disp.minimize()
final_disp = B_disp + result_disp.residual

#minner = Minimizer(fcn2min, params, fcn_args=(x,B)) #,scale_covar=False)
#result = minner.minimize()
#final = B + result.residual


report_fit(result_ramp_disp)
#report_fit(result_ramp)
report_fit(result_disp)
#report_fit(result)

ax.plot(B_ramp,B_ramp*result_ramp_disp.params['h'].value + result_ramp_disp.params['q'].value,'r-')
ax1.plot(B,B*result_disp.params['h'].value + result_disp.params['q'].value,'b-')
# Limit the range of the plot t 

#plt.xlim(0,100)        # Val á kvarðabili
#plt.ylim(0,12)

plt.yticks(fontsize=12)     #Leturstærð á kvarða   
plt.xticks(fontsize=12) 

plt.xlabel('Segulflæðisþéttleiki (G)',fontsize=14)#,color='r')     #Leturstærð og litur í nafni ása
plt.ylabel('Spennu inntak ',fontsize=14)

plt.draw()
plt.pause(10) # <-------
























