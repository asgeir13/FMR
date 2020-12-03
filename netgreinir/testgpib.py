import pyvisa
import time
import numpy as np
import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(1,2,1)
ax1 = fig.add_subplot(1,2,2)

rm = pyvisa.ResourceManager('@py')
#print(rm.list_resources())

inst = rm.open_resource('GPIB0::6::INSTR')#, send_end=True)
#print(inst.query("ONP"))
inst.write("S11")
start="SRT 40 MHz"

stop="STP 5000 MHz"
inst.write(start)
inst.write(stop)
inst.write("HLD;TRS;WFS")
inst.write('*OPC?')
c=True
while c:    
    val=0
    try:
        val=inst.read()
        print(val)
        c=False
    except:
        print('na')
        time.sleep(0.1)
    

#
inst.write("FMA")
time.sleep(3)
inst.write("OFV")
fre_val=inst.read("\n")
fre_val=fre_val.rsplit(", ")
new_fre_val=fre_val[0].rsplit(" ")
new_fre_val.extend(fre_val[1:])
new_fre_val=[float(n) for n in new_fre_val[1:]]
#
#
inst.write("OFD")
valu=inst.read("\n")
valu=valu.rsplit(",")
new_valu=valu[0].rsplit(" ")
new_valu.extend(valu[1:])
new_valu=[float(n) for n in new_valu[1:]]
real_part=imag_part=np.arange(len(new_fre_val),dtype=np.float64)

real_part=new_valu[0:-1:2]
imag_part=new_valu[1:-1:2]
imag_part.append(new_valu[-1])
print(len(real_part))
print(len(imag_part))
inst.write("TRS;WFS")
inst.write('*OPC?')
c=True
while c:    
    val=0
    try:
        val=inst.read()
        print(val)
        c=False
    except:
        print('na')
        time.sleep(0.1)
    

#
#
#print(f'''
#Length of value array: {len(new_valu)} 
#Length of fre_val: {len(new_fre_val)}
#Frequency:
#First value: {new_fre_val[0]}
#Last value: {new_fre_val[-1]}
#
#''')
#
#ax.plot(new_fre_val, real_part)
#ax1.plot(new_fre_val, imag_part)
#plt.show()

