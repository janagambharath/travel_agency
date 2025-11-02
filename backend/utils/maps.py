import googlemaps
from config import Config
import math

# Initialize Google Maps client
gmaps = googlemaps.Client(key=Config.GOOGLE_MAPS_API_KEY)

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two points using Haversine formula
    Returns distance in kilometers
    """
    # Radius of Earth in kilometers
    R = 6371.0
    
    # Convert coordinates to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Differences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Haversine formula
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return round(distance, 2)

def get_distance_matrix(origins, destinations):
    """
    Get distance and duration using Google Maps Distance Matrix API
    
    Args:
        origins: List of origin coordinates [(lat, lon)]
        destinations: List of destination coordinates [(lat, lon)]
    
    Returns:
        dict with distance (km) and duration (minutes)
    """
    try:
        result = gmaps.distance_matrix(
            origins=origins,
            destinations=destinations,
            mode='driving',
            units='metric'
        )
        
        if result['rows'][0]['elements'][0]['status'] == 'OK':
            element = result['rows'][0]['elements'][0]
            distance_km = element['distance']['value'] / 1000  # Convert meters to km
            duration_min = element['duration']['value'] / 60  # Convert seconds to minutes
            
            return {
                'distance_km': round(distance_km, 2),
                'duration_minutes': round(duration_min, 0),
                'distance_text': element['distance']['text'],
                'duration_text': element['duration']['text']
            }
        else:
            return None
    except Exception as e:
        print(f"Error getting distance matrix: {e}")
        return None

def geocode_address(address):
    """
    Convert address to coordinates
    
    Args:
        address: Street address string
    
    Returns:
        dict with latitude and longitude
    """
    try:
        result = gmaps.geocode(address)
        if result:
            location = result[0]['geometry']['location']
            return {
                'latitude': location['lat'],
                'longitude': location['lng'],
                'formatted_address': result[0]['formatted_address']
            }
        return None
    except Exception as e:
        print(f"Error geocoding address: {e}")
        return None

def reverse_geocode(lat, lon):
    """
    Convert coordinates to address
    
    Args:
        lat: Latitude
        lon: Longitude
    
    Returns:
        Formatted address string
    """
    try:
        result = gmaps.reverse_geocode((lat, lon))
        if result:
            return result[0]['formatted_address']
        return None
    except Exception as e:
        print(f"Error reverse geocoding: {e}")
        return None

def get_estimated_fare(distance_km):
    """
    Calculate estimated fare based on distance
    
    Args:
        distance_km: Distance in kilometers
    
    Returns:
        Estimated fare in rupees
    """
    # Base fare + per km rate
    base_fare = Config.BASE_FARE
    per_km_rate = Config.PER_KM_RATE
    
    fare = base_fare + (distance_km * per_km_rate)
    
    # Round to nearest 10
    fare = round(fare / 10) * 10
    
    return fare

def get_nearby_drivers(pickup_lat, pickup_lon, radius_km=50):
    """
    Find drivers within radius of pickup location
    
    Args:
        pickup_lat: Pickup latitude
        pickup_lon: Pickup longitude
        radius_km: Search radius in kilometers
    
    Returns:
        List of drivers with their distance from pickup
    """
    from models.driver import Driver
    
    # Get all available drivers
    available_drivers = Driver.query.filter_by(
        status='available',
        is_verified=True
    ).filter(
        Driver.current_latitude.isnot(None),
        Driver.current_longitude.isnot(None)
    ).all()
    
    nearby_drivers = []
    
    for driver in available_drivers:
        distance = calculate_distance(
            pickup_lat, pickup_lon,
            driver.current_latitude, driver.current_longitude
        )
        
        if distance <= radius_km:
            nearby_drivers.append({
                'driver': driver,
                'distance_km': distance
            })
    
    # Sort by distance
    nearby_drivers.sort(key=lambda x: x['distance_km'])
    
    return nearby_drivers

def get_route_polyline(origin, destination):
    """
    Get route polyline for map display
    
    Args:
        origin: (lat, lon) tuple
        destination: (lat, lon) tuple
    
    Returns:
        Encoded polyline string
    """
    try:
        directions = gmaps.directions(
            origin=origin,
            destination=destination,
            mode='driving'
        )
        
        if directions:
            polyline = directions[0]['overview_polyline']['points']
            return polyline
        return None
    except Exception as e:
        print(f"Error getting route: {e}")
        return None
