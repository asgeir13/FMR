import numpy as np
import numpy_indexed as npi
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression


def is_float_int(string):
    try:
        return float(string)
    except ValueError:
        return False

data=[]
with open('data.dat', 'r') as f:
    d=f.readlines()
    for i in d:
        k = i.rstrip().split(", ")
        data.append([float(i) if is_float_int(i) else i for i in k])
data = np.array(data, dtype='O')

B=data[0][4:]
a=[0.00, 0.00, 0.00] 
B=np.insert(B,0,a)
alpha=data[1][1:]

print(B)
print(alpha)
x_unique, y_mean = npi.group_by(B).mean(alpha)

model=LinearRegression().fit(x_unique.reshape(-1,1),y_mean)
y=model.intercept_+x_unique*model.coef_[0]

plt.plot(x_unique,y_mean,'o')
plt.plot(x_unique,y)
plt.show()

print(f'''Coefficient {model.coef_[0]}
intercept {model.intercept_}
''')
