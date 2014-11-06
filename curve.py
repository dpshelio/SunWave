import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation

distance = np.arange(0,800000,5000) #Km
background = np.zeros(len(distance))
front = np.zeros(20) + 80. #%intensity
# damping = #exponential ?

velocity = 250. #km/s
acceleration = 0 #-300. #m/s/s

timestep = 30. #s

fig = plt.figure()
ax = plt.axes(xlim = (0,800000), ylim = (-20,100))
line, = ax.plot([], [], lw=2)

#TODO: add velocity and acceleration to the wave
def wave_func(t):
    wave = background.copy()
    wave[t:t+20] += front
    return wave

def init():
    line.set_data([], [])
    return line,


def animate(t):
    line.set_data(distance, wave_func(t))
    return line,

anim = animation.FuncAnimation(fig, animate, init_func=init,
                               frames = 100, interval = 20)

plt.show()
