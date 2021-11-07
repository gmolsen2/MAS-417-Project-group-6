# This code will input coordinates in mainland Norway and output a .stl file of that area.
# Originally written by K. M. Knausgård 2021-10-26.
# Forked on 2021.10.29
#
from io import BytesIO
import numpy as np
import requests
from PIL import Image
from stl import mesh
#import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
from matplotlib import pyplot


#Input
MAX_HEIGHT=100
#height=0 for minpix
#height=maxheight for maxpix

def import_lat():
    """
    print('Please input desired latitude within mainland Norway, "north-south direction" http://bboxfinder.com/#0.000000,0.000000,0.000000,0.000000')
    lat = float(input())
    #Suggested value: lat = 59.85

    if lat > 57.0 and lat < 71.0:
            lat = lat
    else:
        print('Latitude out of bounds. Value needs to be between 57 and 71')
        import_lat()
    """
    lat = 59.85
    return lat


def import_lon():
    """
    print('Please input desired longitude within mainland Norway')
    lon = float(input())
    #Suggested value: lon = 8.65

    if lon > 2.0 and lon < 32.88:
        lon = lon
    else:
        print('Longitude out of bounds. Value needs to be between 2 and 32.8')
        import_lon()
    """
    lon = 8.65
    return lon


def get_image(lat, lon):

    #Bounding box calculations
    sq = 5                                                             # This controls size of printout area, sq is side of square in kilometers
    corner_const = 90 * sq / 22000
    BBY = [lon - corner_const * 2, lon + corner_const * 2]
    BBX = [lat - corner_const, lat + corner_const]

    #API call information:

    request_url = 'https://wms.geonorge.no/skwms1/wms.hoyde-dom?' \
           'SERVICE=WMS&' \
           'VERSION=1.3.0&' \
           'REQUEST=GetMap&' \
           'FORMAT=image/png&' \
           'TRANSPARENT=false&' \
           'LAYERS=DOM:None&' \
           'CRS=EPSG:4326&' \
           'STYLES=&' \
           'WIDTH=500&' \
           'HEIGHT=500&' \
           f'BBOX={BBX[0]},{BBY[0]},{BBX[1]},{BBY[1]},'


    response = requests.get(request_url, verify=True)  # SSL Cert verification explicitly enabled. (This is also default.)
    print(f"HTTP response status code = {response.status_code}")
    img = Image.open(BytesIO(response.content))
    np_img = np.asarray(img)
    img = Image.fromarray(np.uint8(np_img))
    img.show()
    return img


# Create the image class based x = lat , y = lon, get_image funtion that gets image based on x and y
class MyImage:
  def __init__(self, x, y):
    self.x = x
    self.y = y
    self.img = get_image(x,y)


first_image = MyImage(import_lat(), import_lon())


# Define the 4 vertices of the surface

img = first_image.img
grey_img = img.convert('L')



#info for making vectors
imageNP= np.array(grey_img)
maxPix = imageNP.max()
minPix = imageNP.min()
(ncols,nrows)=grey_img.size
verticies=np.zeros((nrows,ncols,3))

for x in range(0,ncols):
    for y in range(0,nrows):
        pixelIntensity= imageNP[y][x]
        z = (pixelIntensity * MAX_HEIGHT) / maxPix
        #coordinates
        verticies[y][x]=(x,y,z)
faces=[]

for x in range(0, ncols-1):
  for y in range(0, nrows-1):

       #create face1
    vertice1=verticies[y][x]
    vertice2=verticies[y+1][x]
    vertice3=verticies[y+1][x+1]
    face1=np.array([vertice1,vertice2,vertice3])
       #create face 2
    vertice1 = verticies[y][x]
    vertice2 = verticies[y][x+1]
    vertice3 = verticies[y+1][x+1]

    face2 = np.array([vertice1, vertice2, vertice3])

    faces.append(face1)
    faces.append(face2)
print(f"number of faces:{len(faces)}")

facesNP= np.array(faces)


# Create the mesh
surface = mesh.Mesh(np.zeros(facesNP.shape[0], dtype=mesh.Mesh.dtype))
for i, f in enumerate(faces):
    for j in range(3):
        surface.vectors[i][j] = facesNP[i][j]
# Write the mesh to file "surface.stl"
surface.save('surface.stl')
print(surface)


#Code for displaying .stl file in python

# Create a new plot
figure = pyplot.figure()
axes = mplot3d.Axes3D(figure)

# Load the STL files and add the vectors to the plot
your_mesh = mesh.Mesh.from_file('surface.stl')
axes.add_collection3d(mplot3d.art3d.Poly3DCollection(your_mesh.vectors))

# Auto scale to the mesh size
scale = your_mesh.points.flatten()
axes.auto_scale_xyz(scale, scale, scale)

# Show the plot to the screen
pyplot.show()

