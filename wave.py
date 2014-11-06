import numpy as np
import itertools
from itertools import izip

def square(time = None, size = 1, max_intensity = 0.8):
    return np.ones(size) * max_intensity

def square_low(time = None, size = 1, max_intensity = 0.8):
    return np.ones(size) * max_intensity * np.exp(100 - time * 0.1)/np.exp(100)

def saw(time = None, size = 5, max_intensity = 0.8):
    return np.linspace(0, max_intensity, size)

def gaussian(time = None, max_intensity = 0.8, fwhm = 1):
    '''
    Notice the size of the result is given by the fwhm
    '''
    c = fwhm / (2 * np.sqrt(2 * np.log(2)))
    x = np.arange(-2*fwhm, 2* fwhm + 1)
    return max_intensity * np.exp(- (x)**2 / (2*c**2))

def wave(len_data1d, velocity = 1, cadence = 1, #deltaX = 1, 
         wave_func=None, wave_args={}):
    '''
    It creates an array with a moving function over time.
    valid functions can be seen above

    fixme: What to do when velocity is not a whole step?
    '''

    maxsteps = int((len_data1d - len(wave_func(time = 0, **wave_args))) / velocity) + 1
    timesteps = np.arange(0,maxsteps, cadence) # an array so we can multiply for it
    wave_matrix = np.array([wave_func(time = t, **wave_args) for t in timesteps])
    wave_final = np.zeros((wave_matrix.shape[0], len_data1d))
    for idx, t, row in izip(itertools.count(), timesteps, wave_final): 
        row[t * velocity : t * velocity + len(wave_matrix[idx,:])] = wave_matrix[idx,:]

    return wave_final, timesteps
