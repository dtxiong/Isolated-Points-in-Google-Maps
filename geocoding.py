from audioop import reverse
import googlemaps
from datetime import datetime

gmaps = googlemaps.Client(key='')

# Geocoding an address
geocode_result = gmaps.geocode('1600 Amphitheatre Parkway, Mountain View, CA')

# Look up an address with reverse geocoding
reverse_geocode_result = gmaps.reverse_geocode((40.714224, -73.961452))

mit_coordinates = (42.35923382978076, -71.09311966503593)
place_query = gmaps.places("police", mit_coordinates, 10000, type = "police")
places = place_query['results'] 
num_places = len(places)
places_coords = []
for place in places:
    loc = place['geometry']['location']
    coord = (loc['lat'], loc['lng'])
    places_coords.append(coord)
#print(reverse_geocode_result[0]['geometry']['location'])

print(places_coords)

