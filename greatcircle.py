import numpy as np


def pointInPlane(normal, offset = 0):
    """
    pointInPlane provides a point in a plane defined by the normal
    vector and separated from the origin the distance of the vector
    
    Every plane can be defined from its normal vector as follows:
    Plane N: n_x * x + n_y * y + n_z * z + c = 0
    where the vector normal = (n_x, n_y, n_z)
    and c would be the offset from the origin.

    This function calculates a point p such:
       - belongs to the plane N,
       - It's as far from the origin as the length of n(vector)

    In other words, the point p could form a vector op which is
    the same length than normal.  
    """
    #TODO: check normal is np array with 3 elements
    lengthNormal = np.sum(normal ** 2)
    
    #The 2 eq to solve are:
    # px**2 + py**2 + pz**2 = lengthNormal**2
    # nx * x + ny * y + nz * z + c = 0

    # To solve the plane equation without getting into a Divided by 0
    # situation, we are going to sort the coordinates such way that
    # a pseudo z is obtained.

    # Find the indices for the pseudo coordinates
    # Following array is built by sorting the array by the 2 index, value, and
    # getting just the indices
    indices = [i[0] for i in sorted(enumerate(np.abs(normal)), key=lambda x:x[1])]

    # Solving the equation for pseudo x = 0 and |OP| = |normal|
    #FIXME! this is not accounting of the offset yet; All in respect to origin.
    psX = 0.
    psZ = -1 * normal[indices[1]] / np.sqrt(normal[indices[1]] ** 2 + normal[indices[2]] ** 2)
    psY = np.sqrt(1 - psZ ** 2)
    # NOTE! I've chosen psZ with (-) sign... from +/- -> not right solution with +.. why???

    # We need to return back to the real coordinate system.
    pseudo_point = [psX, psY, psZ]
    p = [pseudo_point[i[0]] for i in sorted(enumerate(indices), key=lambda x:x[1])]
    

    return np.array(p)

def circleInPlane(vectoru, vectorv):
    """
    circleInPlane provides the function of a circle within the plane
    set by two (perpendicular?) vectors.

    The function for a circle is: 
      r(t) = a + Rcos(t) * u + Rsin(t) * v
    For now I'm assuming a = 0, R = 1
    """
    #TODO: R has not been set, so the circle may not be such
    #TODO: What if it's not in the origin?
    return lambda x: vectoru * np.cos(x) + vectorv * np.sin(x)

def GreatCircle(pointP, times = 360, step=1):
    """
    A point in a sphere is used to produce n great cricles for 
    that pass through that point separated 360/n degrees.
    Default 1 per degree.
    """

    #todo: check it's a 3 elements array (pointP)

    # Obtain a point in a plane perpendicular to OP
    vectoru = pointInPlane(pointP)
    # Vector perpendicular to OP and vectoru
    vectorv = np.cross(vectoru, pointP)

    # Circle using vectoru and vectorv with a separation set by user
    circle_perp = circleInPlane(vectoru, vectorv)
    angles = np.linspace(0,2 * np.pi, num = times, endpoint = False)
    pointsA = [circle_perp(i) for i in angles]
    pointsA_arr = np.vstack(pointsA)

    # Create greatcircles for each pair OP, OA
    angles_gc = np.linspace(0, np.pi, num = 180./step, endpoint = False)
    gcircles = [np.vstack([circleInPlane(pointP, pointA)(angl) for angl in angles_gc]) for pointA in pointsA_arr]
    return gcircles

def GCircle2lonlatr(gcircles):
    '''

    '''

    lonlatrgc = [[np.rad2deg(np.arctan2(line[:,1], line[:,0])), 
                  np.rad2deg(np.arcsin(line[:,2])),
                  np.sqrt(np.sum(line ** 2, axis=1))] for line in gcircles]
    return lonlatrgc

def lonlatr2GCircleStart(lon, lat, r = 1):
    lon, lat = np.deg2rad(lon), np.deg2rad(lat)
    x = r * np.cos(lat) * np.cos(lon)
    y = r * np.cos(lat) * np.sin(lon)
    z = r * np.sin(lat)
    return np.array([x, y, z])

###
# Tests! input lon,lat values => known xyz (1,0,0),...



#import numpy as np
#import greatcircle
#import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D
# a = greatcircle.GreatCircle(np.array([1,0,0]), times=10, step = 10)
# fig = plt.figure()
# ax = fig.gca(projection='3d')
# for arr in a:
#     ax.plot(arr[:,0], arr[:,1], arr[:,2])
# plt.show()
