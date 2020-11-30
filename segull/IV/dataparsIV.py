import numpy as np
import numpy_indexed as npi
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression


def is_float_int(string):
    try:
        return float(string)
    except ValueError:
        return False

def flott(string):
    if string == '0.000' or string == '0.00':
        return 0.00
    else:
        return string

data=[]
with open('IV_data_hallsense.dat', 'r') as f:
    d=f.readlines()
    for i in d:
        k = i.rstrip().split(", ")
        data.append([float(i) if is_float_int(i) else flott(i) for i in k])
data = np.array(data, dtype='O')

lengthdata=len(data)
variables=[None]*lengthdata
i=0
while i<lengthdata:
    variables[i]=data[i][0]
    i+=1 

for i, val in enumerate(variables):
    if val == 'V':
        V=np.array(data[i][1:])
    elif val == 'I':
        I=np.array(data[i][1:])
    elif val == 'delta_V':
        delta_V=data[i][1:]
    elif val == 'delta_I':
        delta_I=data[i][1:]
    else:
        V_tolva=np.array(data[i][1:])

print(f'''
V er {V}
I er {I}
ovissa V er {delta_V}
ovissa I er {delta_I}
''')

model=LinearRegression().fit(I.reshape(-1,1),V)
#y=model.intercept_+x_unique*model.coef_[0]

plt.plot(I,V,'o')
#plt.plot(x_unique,y)
plt.show()

print(f'''Coefficient {model.coef_[0]}
intercept {model.intercept_}
''')
