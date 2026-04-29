

# Basic Weather App
# This program lets a user type in a city name and see the current weather
# including temperature, humidity, wind speed, condition, and local time.

import requests  # used to call the weather API
from datetime import datetime  # used for date and time
from zoneinfo import ZoneInfo  # used to get correct time for each city


# This function finds matching cities from the API
def get_coordinates(city_name: str):

    # API URL for searching cities
    geocode_url = "https://geocoding-api.open-meteo.com/v1/search"

    # Parameters sent to API
    params = {
        "name": city_name,
        "count": 5,  # return up to 5 matches
        "language": "en",
        "format": "json",
    }

    # Send request
    response = requests.get(geocode_url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    # Get results list
    results = data.get("results")

    # If no city found
    if not results:
        return None

    # Create list of locations
    locations = []

    # Loop through results and save info
    for location in results:
        locations.append({
            "name": location.get("name", city_name),
            "state": location.get("admin1", ""),
            "country": location.get("country", "Unknown"),
            "latitude": location.get("latitude"),
            "longitude": location.get("longitude"),
            "timezone": location.get("timezone"),
        })

    return locations


# This function lets the user pick the correct city
def choose_location(locations):

    # If only one result, just return it
    if len(locations) == 1:
        return locations[0]

    print("\nMultiple locations found. Please choose one:")
    print("-" * 40)

    # Show list of cities
    for index, location in enumerate(locations, 1):
        if location.get("state"):
            print(f"{index}. {location['name']}, {location['state']}, {location['country']}")
        else:
            print(f"{index}. {location['name']}, {location['country']}")

    # Ask user to pick
    choice = input("\nEnter number: ").strip()

    # Check if input is a number
    if not choice.isdigit():
        print("Invalid selection.")
        return None

    choice = int(choice)

    # Check if number is valid
    if choice < 1 or choice > len(locations):
        print("Invalid selection.")
        return None

    return locations[choice - 1]


# This function gets the current time for a city
def get_city_time(timezone_name: str):
    try:
        now = datetime.now(ZoneInfo(timezone_name))
        day = now.strftime("%Y-%m-%d")
        time = now.strftime("%I:%M %p").lstrip("0")
        return day, time
    except Exception:
        return "N/A", "N/A"


# This function gets weather data
def get_current_weather(latitude: float, longitude: float):

    weather_url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
        "temperature_unit": "fahrenheit",
        "wind_speed_unit": "mph",
    }

    # Call API
    response = requests.get(weather_url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    return data.get("current")


# This function converts weather codes into words
def weather_description(code):

    if code is None:
        return "N/A"

    code_map = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        71: "Snow",
        80: "Rain showers",
        95: "Thunderstorm",
    }

    return code_map.get(code, "Unknown weather condition")


# This function prints the city nicely
def print_location(location):
    if location.get("state"):
        print(f"City: {location['name']}, {location['state']}, {location['country']}")
    else:
        print(f"City: {location['name']}, {location['country']}")


# Main program
def main():
    print("=== Basic Weather App ===")

    # Loop so user can search again
    while True:
        city = input("\nEnter a city name: ").strip()

        # Check for empty input
        if not city:
            print("Please enter a valid city name.")
            continue

        try:
            # Get city options
            locations = get_coordinates(city)

            if locations is None:
                print("City not found. Please try again.")
                continue

            # Let user choose correct one
            location = choose_location(locations)

            if location is None:
                continue

            # Get weather data
            weather = get_current_weather(
                location["latitude"],
                location["longitude"]
            )

            if weather is None:
                print("Weather data unavailable.")
                continue

            # Get local time
            timezone_name = location.get("timezone")
            day, time = get_city_time(timezone_name)

            # Show results
            print("\nCurrent Weather")
            print("-" * 30)
            print_location(location)
            print(f"Temperature: {weather.get('temperature_2m', 'N/A')}°F")
            print(f"Humidity: {weather.get('relative_humidity_2m', 'N/A')}%")
            print(f"Wind Speed: {weather.get('wind_speed_10m', 'N/A')} mph")
            print(f"Condition: {weather_description(weather.get('weather_code'))}")
            print(f"Day: {day}")
            print(f"Time: {time}")

        except requests.exceptions.RequestException:
            print("Connection error. Try again later.")
        except Exception as e:
            print(f"Unexpected error: {e}")

        # Ask if user wants to continue
        again = input("\nWould you like to search another city? (y/n): ").strip().lower()

        if again != "y":
            print("Goodbye!")
            break


# Run the program
if __name__ == "__main__":
    main()