import requests
import logging


logger = logging.getLogger(__name__)


class WeatherHelper:
    def __init__(self, api_key="1stw4frCyId0SiMAlivlDw8NmEowlGOC"):
        self.api_key = api_key
        self.base_url = "http://dataservice.accuweather.com/"

    def get_info(self, query: str) -> int:
        """Get location key by query

        Args:
            query (str): Location query

        Returns:
            key (int): Location key
        """
        url = self.base_url + "locations/v1/search"
        params = {"apikey": self.api_key, "q": query}

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            logger.info(
                f"Response for get_location for {query} is successful(name  - {response.json()[0]['LocalizedName']})!"
            )
        except Exception as e:
            logger.exception(f"Exception during get_location for {query}:\n{e}")
            return None

        info = {
            "name": response.json()[0]["LocalizedName"],
            "key": response.json()[0]["Key"],
            "lat": response.json()[0]["GeoPosition"]["Latitude"],
            "lon": response.json()[0]["GeoPosition"]["Longitude"],
        }

        return info

    def get_weather_daily(self, location_key: int) -> dict:
        """Get daily weather forecast for the next `days` days

        Args:
            location_key (int): Location key
            days (int): Number of days for the forecast

        Returns:
            stat (dict): Dictionary with weather statistics
        """

        url = self.base_url + f"forecasts/v1/daily/5day/{location_key}"
        params = {"apikey": self.api_key, "details": True, "metric": True}

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            logger.info(
                f"Response for get_weather_daily for {location_key} is successful!"
            )
        except Exception as e:
            logger.exception(
                f"Exception during get_weather_daily for {location_key}:\n{e}"
            )
            return None

        response = response.json()
        stat = {
            "date": [response["DailyForecasts"][i]["Date"][:10] for i in range(5)],
            "temperature_max": [
                response["DailyForecasts"][i]["Temperature"]["Maximum"]["Value"]
                for i in range(5)
            ],
            "temperature_min": [
                response["DailyForecasts"][i]["Temperature"]["Minimum"]["Value"]
                for i in range(5)
            ],
            "wind_speed": [
                response["DailyForecasts"][i]["Day"]["Wind"]["Speed"]["Value"]
                for i in range(5)
            ],
            "precipitation": [
                response["DailyForecasts"][i]["Day"]["PrecipitationProbability"]
                for i in range(5)
            ],
        }

        return stat


if __name__ == "__main__":
    wh = WeatherHelper()
    location = wh.get_info("Moscow")
    print(location)
    weather = wh.get_weather_daily(location["key"])
    print(weather)
