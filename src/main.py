import argparse
import asyncio
import sys
import aiohttp
import json
import re
from geopy.geocoders import Nominatim


class WeatherFetcher:
    def __init__(self, latitude, longitude):
        self.data = None
        self.longitude = longitude
        self.latitude = latitude
        self.url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=temperature_2m,rain"

    async def get_data(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as response:
                # TODO: Cover it with try/excepts when service is unavailable
                self.data = await response.text()
                self.data = json.loads(self.data)
                return self.data


class WeatherProcessor:
    def __init__(self, data, temperature_treshold, rainfall_treshold, location):
        self.data = data
        self.temperature_treshold = temperature_treshold
        self.rainfall_treshold = rainfall_treshold
        self.location = location

    def process(self):
        if self.data is None:
            raise Exception("Data for parsing was not collected!")
        # Case OR - "(...)received data and print alertS to stdout when(...)" states those two requirements are different
        # for temp, rain, utc in zip(self.data["hourly"]['temperature_2m'], self.data["hourly"]['rain'], self.data["hourly"]['time']):
        #     if rain > self.rainfall_treshold:
        #         print("Warning " + args.location + ", low temperature " + str(temp) + " of C and rain " + str(rain) + " mm expected on " + str(utc))
        #
        # for temp, rain, utc in zip(self.data["hourly"]['temperature_2m'], self.data["hourly"]['rain'], self.data["hourly"]['time']):
        #     if temp < self.temperature_treshold:
        #         print("Warning " + args.location + ", low temperature " + str(temp) + " of C and rain " + str(rain) + " mm expected on " + str(utc))

        # Case AND - from the example output it states that and should be used
        for temp, rain, utc in zip(self.data["hourly"]['temperature_2m'], self.data["hourly"]['rain'], self.data["hourly"]['time']):
            if temp < self.temperature_treshold:
                if rain > self.rainfall_treshold:
                    print("Warning " + self.location + ", low temperature " + str(temp) + " of C and rain " + str(rain) + " mm expected on " + str(utc))

        # Depreciated, slow method. 10 retries on 1 mln reruns is 10s faster for zip method
        # for i in range(len(self.data["hourly"]['time'])):
        #     if self.data["hourly"]['temperature_2m'][i] < self.temperature_treshold:
        #         if self.data["hourly"]['rain'][i] > self.rainfall_treshold:
        #             print("Warning " + args.location + ", low temperature " + str(self.data['hourly']['temperature_2m'][i]) + " of C and rain " + str(self.data['hourly']['rain'][i]) + " mm expected on " + str(self.data['hourly']['time'][i]))


async def runner(name, max_temp, min_rain):
    lat, long = get_location(name)
    fetcher = WeatherFetcher(lat, long)
    data = await fetcher.get_data()
    processor = WeatherProcessor(data, max_temp, min_rain, name)
    processor.process()


def get_location(name):
    # TODO: Make it completely idiotproof for incorrect inputs
    if any(char.isdigit() for char in name):
        lat, long = list(filter(None, re.split('[, ]', name)))
        return lat, long
    else:
        geolocator = Nominatim(user_agent="temporary")
        location = geolocator.geocode(name)
        if not location:
            raise Exception("Location unknown")
        return location.latitude, location.longitude


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Please provide treshold values")
    parser.add_argument('--location', '-l', help='City name or coordinates', default=None)
    parser.add_argument('--max_temp', '-t',  help='Maximum value for rain temperature', type=float, default=None)
    parser.add_argument('--min_rainfall', '-r', help='Minimum value for rain', type=float, default=None)
    args = parser.parse_args()

    if args.location is None:
        print("Missing location, provide location using --location/-l parameter")
        sys.exit()
    if args.max_temp is None:
        print("Missing temperature treshold, provide it by using --max_temp/-t parameter")
        sys.exit()
    if args.min_rainfall is None:
        print("Missing rain treshold, provide it by using --min_rainfall/-r parameter")
        sys.exit()

    args = parser.parse_args()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(runner(args.location, args.max_temp, args.min_rainfall))
