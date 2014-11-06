import numpy as np
from  sunpy.wcs import wcs
import greatcircle
import sunpy
import sunpy.map as smap
import sunpy.time as stime
import datetime
from scipy import ndimage
import copy
from itertools import izip
import wave
import rotsun
from skimage import transform

i0 = smap.Map('./ssw_cutout_20110607_063514_AIA_211_.fts')
if i0.shape[0] > 2048:
    i0 = i0.resample((2048,2048))
x = -320
y = -364
step = 0.1
times = 720 # around focus
velocity = 700 # km/s
cadence = 200 # sec
lonlat = wcs.convert_hpc_hg(x, y, dsun_meters = i0.meta['dsun_obs'])
start_point_xyz = greatcircle.lonlatr2GCircleStart(lonlat[0], lonlat[1])
lonlatgc = greatcircle.GCircle2lonlatr(greatcircle.GreatCircle(start_point_xyz, step = step, times = times))

xycoord = [wcs.convert_hg_hpc(line[0] , line[1], 
                              dsun_meters = i0.meta['dsun_obs'], 
                              occultation = True) for line in lonlatgc]

pxcoord = [np.array(np.round(np.nan_to_num(wcs.convert_data_to_pixel(line[0], line[1], 
                                                                     i0.scale.values(), i0.reference_pixel.values(), 
                                                                     [0,0]))), #i0.reference_coordinate.values()))),
                    dtype = np.int) for line in xycoord]
pxcoord_arr = np.array(pxcoord) # shape for default -> (360,2,180)
# Convert the values from physical to pixel values
deltaX = wcs.rsun_meters * np.deg2rad(step) / 1e3 # km
velocity_px = velocity / deltaX
deltaT = 1 / velocity_px # sec
cadencewave = int(cadence / deltaT)
front = int(150e3 / deltaX)
# Create the wave 
wavearr, tsteps = wave.wave(len(line[0]), velocity = velocity_px, cadence = cadencewave,
                            wave_func = wave.square, wave_args = {'size': front })

messa = \
"""The velocity used is: {velocity} km/s 
with a front size of: {front} km
and a cadence of: {cadence} s""".format(velocity = velocity, 
                                        front = front * deltaX, 
                                        cadence = cadencewave * deltaT)
print messa
# Create t-x-y array for all the images
mask_series = np.zeros((wavearr.shape[0],) + i0.shape)
time0 = stime.parse_time(i0.meta['date-obs'])
times_str = [(time0 + datetime.timedelta(0,deltaT * ts + cadence)).isoformat() for ts in tsteps]  # the first image is at dt = cadence from i0.

for ind, mask in enumerate(mask_series):
    for line in pxcoord_arr:
        mask[tuple(line[[1,0],:])] = wavearr[ind,:]
    
mask_series_g = ndimage.gaussian_filter(mask_series,sigma = 1)
final_images = mask_series_g * i0.data + i0.data

#import matplotlib.pyplot as plt
#from matplotlib import animation
#fig = plt.figure()
#ims = [[plt.imshow(mas)] for mas in mask_series_g]
#ani = animation.ArtistAnimation(fig, ims, interval = 50, blit = True)
#plt.show()
##
for image,time in izip(final_images, times_str):
    i0.meta['date-obs'] = time
    i0.meta['date_obs'] = time
    i0.data = transform.warp(rotsun.to_norm(image), inverse_map=rotsun.warp_sun,
                             map_args={'data':i0, 'deltatime':stime.parse_time(time) - time0})
    i0.save('./results/{inst}_{filt}_{date}.fts'.format(inst = i0.meta['telescop'].replace('/','_') ,
                                                        date = stime.parse_time(time).strftime("%Y%m%d_%H%M%S"),
                                                        filt = i0.meta['wavelnth']))


#background = np.zeros(len(line[0]))

#front = np.zeros(150 / (wcs.rsun_meters * np.deg2rad(step) / 1e6)) + 0.80 #%intensity
#def wave_func(t):
#    wave = background.copy()
#    wave[t:t+len(front)] += front
#    return wave
#timemaps = []
#timemaps.append(i0)
#deltaX = wcs.rsun_meters * np.deg2rad(step) / 1e3 # km
#deltaT = deltaX / velocity
##  Each step will be separated as defined by the cadence
#it = smap.Map(sunpy.AIA_171_IMAGE)
#for time in range(0,len(background)-len(front), int(cadence / deltaT)):
#
#    it.meta['date-obs'] = (stime.parse_time(i0.meta['date-obs']) + datetime.timedelta(0,deltaT * time)).isoformat()
#    #it.data[:,:] = np.zeros(it.shape)
#    wave = wave_func(time)
#    for line in pxcoord:
#        points = [np.hstack((np.int(np.round(np.nan_to_num(a))) for a in elem)) for elem in line]
#        points.reverse()  # so we get Y,X
#        points_sort = tuple(points)
#        it.data[points_sort] *= wave #*=
#    it.data += i0.data
#    timemaps.append(it)
#
#cc = smap.MapCube(timemaps)
#
#import matplotlib.pyplot as plt
#fig = plt.figure()
#an = cc.plot(controls=True)
#fig.show()


#import os
#import sunpy.time as stime
#
#inputs = os.listdir('results/')
#for f in inputs:
#    m0 = smap.Map('results/'+f)
#    flist =  f.split('_')
#    ndate = stime.parse_time("_".join(flist[1:3])).strftime("%Y-%m-%dT%H:%M:%S")
#    m0.meta['date_obs'] = ndate
#    m0.save('results2/'+f)
#
#import sunpy.map as smap
#import matplotlib.pyplot as plt
#cube = smap.Map('results/*fts', cube = True)
#for amap in cube._maps:
#    amap.norm = plt.Normalize(vmin=0, vmax=1200)
#fig = plt.figure()
#an = cube.plot(controls = True)
#fig.show()
###
##for amap in cube._maps:
#    amap.data = 100 * (amap.data - i0.data)/i0.data
#    amap.norm = plt.Normalize(vmin=0, vmax=100)
#fig = plt.figure()
#an = cube.plot(controls = True)
#fig.show()
##
