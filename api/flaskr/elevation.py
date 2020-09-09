import requests
from api.flaskr.great_circle import great_circle
from api.settings import GOOGLE_MAPS_API_KEY

DIFFICULTY_MAP = {
    0: "Flat",
    1: "Lightly Uphill",
    2: "Moderately uphill",
    3: "Steeply uphill",
    4: "Very steeply uphill. PROCEED WITH CAUTION"
}

def get_elevation(coords):
    """
    Function to retrieve elevation for a set of coordinates from Google maps API
    :return: list of one dictionary for coordinate in structure: {elevation: float, location:{lat: float, lng: float}}
    """
    locations_string = ""

    for coord in coords:
        locations_string += str(coord["lat"]) + "," + str(coord["lng"]) + "|"

    locations_string = locations_string[0:-1]

    payload = {
        "locations": locations_string,
        "key": GOOGLE_MAPS_API_KEY
    }

    endpoint = "https://maps.googleapis.com/maps/api/elevation/json?"

    result = requests.get(endpoint, payload).json()

    return result["results"]

def determine_difficulty(elevation_change, distance_change):
    MILES_TO_FEET = 5280
    distance_change *= MILES_TO_FEET
    slope = elevation_change / distance_change
    if slope > 0.5:
        return 4
    if slope > 0.4:
        return 3
    if slope > 0.3:
        return 2
    if slope > 0.1:
        return 1
    return 0

def process_elevation(coords_with_elevation):
    """
    Function to analyze relationship between elevation changes and distance changes along a route
    :return: dictionary containing latitude, longitude, elevation and distance from start for each coordinate,
    along with difficulty of the route in Class 1-5. 
    """
    if not coords_with_elevation:
        return {}

    FEET_TO_METERS = 3.28084

    # function will iterate through list forwards if the starting elevation is lower than
    # the ending elevation, otherwise it will iterate through the list backwards
    i = 0
    incrementer = 1
    if coords_with_elevation[-1]["elevation"] < coords_with_elevation[0]["elevation"]:
        incrementer = -1
        i = len(coords_with_elevation) - 1

    # initializing all the values that will be kept track of while iterating through the array
    starting_coords = coords_with_elevation[0]
    distance = 0
    max_elevation = starting_coords["elevation"]
    max_elevation_coords = { "lat": starting_coords["location"]["lat"], "lng": starting_coords["location"]["lng"]}
    max_difficulty = 0
    chart_data = []

    # keeping track of previous dictionary to compute distance between two points
    prev = {}

    while 0 <= i and i < len(coords_with_elevation):
        
        current_coords = coords_with_elevation[i]

        # resolution is unused
        del current_coords["resolution"]

        # lat and lng taken out of the location sub-dictionary and moved to the current_coords dictionary
        current_coords["lat"] = current_coords["location"]["lat"]
        current_coords["lng"] = current_coords["location"]["lng"]
        del current_coords["location"]

        # converting elevation from feet to meters
        current_coords["elevation"] = current_coords["elevation"] * FEET_TO_METERS

        # for all coordinates except the first pair on the path, update distance and determine the difficulty for that section
        if prev:
            lat1, lon1 = prev["lat"], prev["lng"]
            lat2, lon2 = current_coords["lat"], current_coords["lng"]
            distance_change = great_circle(lat1, lon1, lat2, lon2)
            elevation_change = abs(current_coords["elevation"] - prev["elevation"])
            difficulty = determine_difficulty(elevation_change, distance_change)
            max_difficulty = max(max_difficulty, difficulty)
            distance += distance_change
        
        current_coords["distance"] = distance

        # need to test and update max elevation and its coordinates
        if current_coords["elevation"] > max_elevation:
            max_elevation = current_coords["elevation"]
            max_elevation_coords["lat"] = current_coords["lat"]
            max_elevation_coords["lng"] = current_coords["lng"]

        # finally, need to keep track of the distance and elevation data such that it can be parsed by the elevation chart
        chart_data.append({
            "x": round(current_coords["distance"], 2),
            "y": round(current_coords["elevation"])
        })

        prev = current_coords
        
        i += incrementer
    
    return {
        "coords": coords_with_elevation, 
        "difficulty": DIFFICULTY_MAP[max_difficulty], 
        "maximumElevation": max_elevation,
        "maximumElevationCoordinates": max_elevation_coords,
        "chartData": chart_data
        }
