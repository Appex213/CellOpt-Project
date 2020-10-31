
import numpy as np
from scipy.interpolate import interp2d
from mpl_toolkits import mplot3d
import matplotlib.pyplot as plt

x = np.array([0,10,50,90,100])
y = np.array([0,10,50,90,100])

X, Y = np.meshgrid(x, y)

Z = np.array([[ 100    ,  0   ,     0   ,   0   , 100  ],
              [   0    ,  0   ,     0   ,   0   ,   0  ],
              [   0    ,  0   ,  -100   ,   0   ,   0  ],
              [   0    ,  0   ,     0   ,   0   ,   0  ],              
              [ 100    ,  0   ,     0   ,   0   , 100  ]])

x2 = np.linspace(0, 100, 100)
y2 = np.linspace(0, 100, 100)

X2, Y2 = np.meshgrid(x2, y2)

f = interp2d(x, y, Z, kind='cubic')
Z2 = f(x2, y2)

ax = plt.axes(projection="3d")
ax.plot_surface(X2, Y2, Z2)
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('z');
ax.view_init(60, 35)
plt.show()

