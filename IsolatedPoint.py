import math
from matplotlib import pyplot as plt
import numpy as np
from scipy.spatial import Voronoi, voronoi_plot_2d
import googlemaps
import requests

api_key = ''
gmaps = googlemaps.Client(key=api_key)


#Convert Lat/Lng to World Coordinates
def latlng_to_world(latlng):
    #Also, will swap, since lat is north, long is east
    TILE_SIZE = 256
    siny = math.sin((latlng[0] * math.pi) / 180)
    siny = min(max(siny, -0.9999), 0.9999)
    worldx = TILE_SIZE * (0.5 + latlng[1] / 360)
    worldy = - TILE_SIZE * (0.5 - math.log((1 + siny) / (1 - siny)) / (4 * math.pi))
    return np.array([worldx, worldy])

def world_to_latlng(world):
    worldx, worldy = world
    TILE_SIZE = 256

    lng = (worldx / TILE_SIZE - 0.5) * 360
    f = math.e**((worldy / TILE_SIZE + 0.5) * (4 * math.pi))
    siny = (f-1)/(f + 1)
    lat = math.asin(siny) * 180 / math.pi
    return np.array([lat, lng])

def latlng_to_km(lat_dist):
    #360 degrees is 2pi r
    earth_radius = 6371 #in km
    distance = 2*math.pi*earth_radius/360 * lat_dist
    return distance

def world_to_km(world_dist):
    #2048 is 2pi r
    earth_radius = 6371 #in km
    distance = 2*math.pi*earth_radius/2048*world_dist
    return distance

def latlng_dist(coord1, coord2):
    lat1, lng1 = coord1
    lat2, lng2 = coord2
    earth_radius = 6371 #in km
    distance = math.acos(math.sin(lat1)*math.sin(lat2)+math.cos(lat1)*math.cos(lat2)*math.cos(lng2-lng1))*earth_radius*2*math.pi/360
    return distance

# Geocoding an address
#geocode_result = gmaps.geocode('1600 Amphitheatre Parkway, Mountain View, CA')

# Look up an address with reverse geocoding
#reverse_geocode_result = gmaps.reverse_geocode((40.714224, -73.961452))

mit_lng_coordinates = (42.35923382978076, -71.09311966503593)
mit_world_coordinates = latlng_to_world(mit_lng_coordinates)
print(world_to_latlng(mit_world_coordinates))
place_name = "McDonalds"
place_type = "restaurant" 
place_query = gmaps.places(place_name, mit_lng_coordinates, 4000, type = place_type)
places = place_query['results'] 
num_places = len(places)
places_coords = []
for place in places:
    loc = place['geometry']['location']
    latlng_coord = np.array([loc['lat'], loc['lng']])
    coord = latlng_to_world(latlng_coord)
    places_coords.append(coord)
places_coords = np.array(places_coords)
#print(reverse_geocode_result[0]['geometry']['location'])

#plotting
fig = plt.figure()
ax = fig.gca()
ax.axes.xaxis.set_ticks([])
ax.axes.yaxis.set_visible(False)
ax.figure.set_size_inches(10, 10)
#ax.scatter(mit_world_coordinates[0], mit_world_coordinates[1],  c = 'blue')
ax.scatter(places_coords[:,0], places_coords[:,1], c = 'red')
ax.set_title("Isolated Point: " + place_name)
#ax.annotate('d = ' + str(float(d)), (0.01, 0.03), textcoords='axes fraction')


#Get Image
  
url = "https://maps.googleapis.com/maps/api/staticmap?"
center = "Cambridge, Massachusetts"
zoom = 13
r = requests.get(url + "center=" + str(mit_lng_coordinates)[1:-1] + "&zoom=" +
                   str(zoom) + "&size=512x512&scale=2&key=" +
                             api_key)

# wb mode is stand for write binary mode
f = open('map.png', 'wb')
# r.content gives content,
# in this case gives image
f.write(r.content)
  
# close method of file object
# save and close the file
f.close()

#plot image
img = plt.imread("map.png")
center_world = mit_world_coordinates
width = 256/2**(zoom)
xlim = (center_world[0] - width, center_world[0] + width)
ylim = (center_world[1] - width, center_world[1] + width)
ax.imshow(img, extent=[xlim[0], xlim[1], ylim[0], ylim[1]])

# Calculate Voronoi Polygons 
vor = Voronoi(places_coords)

def simple_voronoi(vor, saveas=None, xlim=None, ylim = None):
    # Make Voronoi Diagram 
    fig = voronoi_plot_2d(vor, show_points=False, show_vertices=False, s=4, ax = ax, line_colors = "blue", line_width=2, line_alpha=0.3, point_size=2)

    # Configure figure 
    #ax.set_size_inches(5,5)
    #ax.set_aspect("equal")

    if xlim and ylim:
        ax.set_xlim(*xlim)
        ax.set_ylim(*ylim)
simple_voronoi(vor, xlim = xlim, ylim = ylim)

points = vor.points
vertices = vor.vertices 
ridge_points = vor.ridge_points
ridge_vertices = vor.ridge_vertices
num_vertices = len(vertices)
num_ridge = len(ridge_points)
max_dist = 0
max_vertex = 0
max_point = 0

for i in range(num_ridge):
    ridge_point = ridge_points[i][0]
    ridge_vertex = ridge_vertices[i][0]
    if ridge_vertex != -1:
        coord = vertices[ridge_vertex]
        if xlim[0] < coord[0]  and coord[0] < xlim[1] and ylim[0] < coord[1]  and coord[1] < ylim[1]:
            dist = math.dist(points[ridge_point], vertices[ridge_vertex])
            if dist > max_dist:
                max_dist = dist
                max_vertex = ridge_vertex
                max_point = ridge_point
    ridge_vertex = ridge_vertices[i][1]
    coord = vertices[ridge_vertex]
    if ridge_vertex != -1:
        if xlim[0] < coord[0]  and coord[0] < xlim[1] and ylim[0] < coord[1]  and coord[1] < ylim[1]: 
            dist = math.dist(points[ridge_point], vertices[ridge_vertex])
            if dist > max_dist:
                max_dist = dist
                max_vertex = ridge_vertex
                max_point = ridge_point
max_vertex_coord = vertices[max_vertex]
max_point_coord = points[max_point]
reverse_geocode_result = gmaps.reverse_geocode(world_to_latlng(max_vertex_coord))
print(reverse_geocode_result[0]['formatted_address'])
print(max_dist)
max_dist_km = latlng_to_km(math.dist(world_to_latlng(max_vertex_coord), world_to_latlng(max_point_coord)))
print(world_to_latlng(max_vertex_coord), world_to_latlng(max_point_coord))
print(max_dist_km, latlng_dist(world_to_latlng(max_vertex_coord), world_to_latlng(max_point_coord)))
#max_dist_km = world_to_km(max_dist)
ax.scatter(vertices[:,0], vertices[:,1], s = (2)**2*np.ones(num_vertices), c = 'black') 
ax.scatter(max_vertex_coord[0], max_vertex_coord[1], s = 8**2, c = "navy")
ax.set_xlabel(reverse_geocode_result[0]['formatted_address'] + "\n d = " + str(np.round(max_dist_km, 2)) + " km")
print(latlng_to_world((41.85, -87.65)))
plt.show()