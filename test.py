from geopy.geocoders import Nominatim

latitude = "48.85845478413818"
longitude = "2.294513484705865"

geolocator = Nominatim(user_agent='Locations')
location = geolocator.reverse(f"{latitude},{longitude}", language='en')

print(location.raw)