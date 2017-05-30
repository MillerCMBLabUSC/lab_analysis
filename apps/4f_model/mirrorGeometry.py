import numpy as np
import numpy.linalg as la
import scipy.optimize as opt

###############################
#  Constants defining mirrors
###############################
#Origin: (x,y) is at the boresight
#		 z is at the base of the parabola

# Foci of the mirrors
d = 22662.69*2 			  # Distance between focal points [mm]
eta = np.deg2rad(62.5980) # Angle between line connecting foci and vertical
h = 32100.     #Height of the first focus [mm]
x0 = 0.   
y0 = 30919.07 # y-distance between boresight and parabola axis [mm]

f1 = np.array([0,-y0 ,h]) #Focus of the parabola and first focus of hyperbola
f2 = np.array([0, -y0 + d * np.sin(eta), h - d * np.cos(eta)]) #second focus of hyperbola

da = 6000. #diameter of aperture [mm]
# This is the difference between the distance to foci of hyperbola
D = d*(np.sin(eta)- np.cos(eta))

r = 1 / (4*h) #Radius of parabola
## Paraboloid is given by: z = r (x^2 + (y + y0)^2)

# Returns the angle between two vectors
def vecAngle(x, y):
	return np.arccos(np.dot(x,y) / (la.norm(x)*la.norm(y)))

#Returns the angle between two planes, each defined by two vectors.
def planeAngle(p1, p2, q1, q2):
	return vecAngle(np.cross(p1, p2), np.cross(q1, q2))

# Takes in the first incidence point and returns the second for a given ray.
def findSecondCollision(m):
    p = lambda x : (x*f1 + (1 - x) * m) #point on the path between m and f1
    dist = lambda x: la.norm(p(x) - f1) - la.norm(p(x) - f2) #Distance between foci
    s = opt.brentq(lambda x:dist(x) - D, 0, 1)
    # print la.norm(p(s) - m)
    return p(s)	


#Sample points:
N = 10
X = np.linspace(-da/2, da/2, N)
Y = np.linspace(-da/2, da/2, N)

angleSum1 = 0
angleSum2 = 0
i = 0
for x in X:
	for y in Y:
		if (x**2 + y**2 < (da/2)**2):
			i+=1 
			m1 = np.array([x,y, r*(x**2 + (y + y0)**2)]) #First intersection
			m2 = findSecondCollision(m1) #Second intersection

			th1 = vecAngle(np.array([0,0,1]), m2 - m1)/2 #First incident angle
			th2 = vecAngle(m1 - m2, f2 - m2)/2 #Second incident angle

			# print (1/np.cos(th1) - np.cos(th1))/(1/np.cos(th1) + np.cos(th1))

			angleSum1 += th1
			angleSum2 += th2



print "Mirror 1: %f deg\nMirror 2: %f deg" %(np.rad2deg(angleSum1 / i), np.rad2deg(angleSum2 / i))

















