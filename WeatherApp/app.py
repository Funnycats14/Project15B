import logging
from flask import Flask, request, jsonify
from models import WeatherHelper

app = Flask(__name__)
helper = WeatherHelper()
QueryStorage = {}
CityStorage = {}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.get("/get_prediction")
def serve_predictions():
    query = request.args.get("query", None)

    if query is None:
        return {"error": "Query is required"}, 400
    
    try:
        if query in QueryStorage:
            return QueryStorage[query]
        else:
            cities = query.split(",")
            result = {}

            for city in cities:
                if city not in CityStorage:
                    info = helper.get_info(city)
                    if info is None:
                        return {"error": "Location not found"}, 404
                    CityStorage[city] = info
                
                location_key = CityStorage[city]["key"]
                weather_info = helper.get_weather_daily(location_key)
                if weather_info is None:
                    return {"error": "Internal server error"}, 500
                
                result[city] = weather_info
            
            QueryStorage[query] = result
            return jsonify(result), 200
    except Exception as e:
        logger.exception(f"Exception during get_prediction for {query}:\n{e}")
        return {"error": "Internal server error"}, 500


if __name__ == "__main__":
    app.run()
