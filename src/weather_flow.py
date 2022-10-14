from prefect import task, flow, get_run_logger
from prefect.task_runners import SequentialTaskRunner
import requests
from dataclasses import dataclass
from prefect.tasks import task_input_hash

@dataclass
class Location:
    latitude: float
    longitude: float
    name: str

@dataclass
class Temperature:
    location: Location
    unit: str
    time: str
    temp: str

@task
def get_locations():
    return [
        Location(latitude=41.8, longitude=-87.6, name="Chicago"),
        Location(latitude=21.0, longitude=105.83, name="Hanoi"),
        Location(latitude=36.5, longitude=-116.9, name="Death Valley"),
        Location(latitude=-79.2, longitude=40.5, name="Eastern Antarctic Plateau")
    ]

@task(retries=3, cache_key_fn=task_input_hash)
def get_weather(location):
    result = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={location.latitude}&longitude={location.longitude}&hourly=temperature_2m")
    result.raise_for_status()
    
    hourly = result.json().get("hourly")
    temp = hourly.get("temperature_2m")[0]
    time = hourly.get("time")[0]

    unit = result.json().get("hourly_units").get("temperature_2m")

    return Temperature(location=location, time=time, temp=temp, unit=unit)

@task
def print_weather(weather):
    logger = get_run_logger()

    logger.info(f"""
Location: {weather.location.name} - ({weather.location.latitude}, {weather.location.longitude})
The temperature is {weather.temp}{weather.unit} at {weather.time}
    """)

# using sequential task runner due to issues with Orion DB locking
@flow(task_runner=SequentialTaskRunner())
def weather_data():
    locations = get_locations()
    weather_data = get_weather.map(locations)
    print_weather.map(weather_data)

if __name__ == "__main__":
    weather_data()
