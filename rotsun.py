import datetime
from skimage.util import img_as_float
from sunpy import wcs
from sunpy.time import parse_time
import sunpy.coords.util as cu

def warp_sun(xy, data, deltatime):
    x,y = xy.T
    
    #Define some tuples
    scale = [data.scale['x'], data.scale['y']]
    ref_pix = [data.reference_pixel['x'], data.reference_pixel['y']]
    ref_coord = [data.reference_coordinate['x'], data.reference_coordinate['y']]

    #Calculate the hpc coords for all pixels
    hpc_coords = wcs.convert_pixel_to_data(data.shape, scale,
                                           ref_pix, ref_coord)
    
    #Calculate the shift in hpc coords for all pixels
    rotted = cu.rot_hpc(hpc_coords[1], hpc_coords[0], data.date,
                parse_time(data.date)- deltatime)
    
    #Translate back to pixel coords
    x2,y2 = wcs.convert_data_to_pixel(rotted[0], rotted[1], scale, ref_pix,
                                      ref_coord)
    
    #Restack the data to make it correct output form
    xy2 = np.column_stack([x2.flat,y2.flat])
    
    #Remove NaNs
    mask = np.isnan(xy2)
    xy2[mask] = 0.0

    return xy2
#Scikit-image needs float arrays between 0 and 1
def to_norm(arr):
    arr = img_as_float(arr)
    if arr.min() < 0:
        arr += arr.min()
    arr /= arr.max()
    return arr

def un_norm(arr, ori):
    arr *= ori.max()
    if ori.min() < 0:
        arr -= ori.min()
    
    return arr#.astype(ori.dtype, copy=False)   
