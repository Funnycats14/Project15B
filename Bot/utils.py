import io
import aiohttp
import matplotlib.pyplot as plt
from aiogram import Bot
from aiogram.types import BufferedInputFile
from datetime import datetime


async def filter_data(user_info: dict):
    if len(user_info["intermediate"]) == 0:
        return "Вы, не ввели начальный пункт, пожалуйста, напишите /start и попробуйте снова"
    if len(user_info["final"]) == 0:
        return "Вы, не ввели конечный пункт, пожалуйста, напишите /start и попробуйте снова"
    if user_info["period"] not in [1, 3, 5]:
        return "Вы, не выбрали период прогноза, пожалуйста, напишите /start и попробуйте снова"
    return None
    

async def get_weather_data(user_info: dict):
    async with aiohttp.ClientSession() as session:
        params = {"query": ",".join(user_info["intermediate"] + [user_info["final"]])}
        async with session.get("http://127.0.0.1:5000/get_prediction", params=params) as response:
            data = await response.json()
            return data


async def send_weather_plots(weather_data: dict, chat_id: int, bot: Bot, period: int):
    for city, data in weather_data.items():
        dates_str = data["date"][:period]
        dates = [datetime.strptime(date_str, '%Y-%m-%d').date() for date_str in dates_str]
        temp_max = data["temperature_max"][:period]
        temp_min = data["temperature_min"][:period]
        precipitation = data["precipitation"][:period]
        wind_speed = data["wind_speed"][:period]

        fig, ax1 = plt.subplots(figsize=(10, 6))

        ax1.plot(dates, temp_max, label="Max Temp (°C)", marker="o", color="tab:red")
        ax1.plot(dates, temp_min, label="Min Temp (°C)", marker="o", color="tab:blue")
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Temperature (°C)")
        ax1.tick_params(axis="y")
        ax1.legend(loc="upper left")

        ax1.plot(
            dates,
            wind_speed,
            label="Wind Speed (km/h)",
            linestyle="--",
            color="tab:green",
        )
        ax1.legend(loc="upper left")

        ax2 = ax1.twinx()
        ax2.bar(
            dates, precipitation, alpha=0.3, color="tab:cyan", label="Precipitation (%)"
        )
        ax2.set_ylabel("Precipitation (%)")
        ax2.tick_params(axis="y")
        ax2.legend(loc="upper right")

        plt.xticks(rotation=45)
        plt.title(f"Weather Forecast for {city}")
        plt.tight_layout()

        buffer = io.BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)
        plt.close(fig)

        photo = BufferedInputFile(buffer.getvalue(), filename="weather.png")
        await bot.send_photo(
            chat_id=chat_id, photo=photo, caption=f"Weather forecast for {city}"
        )

        buffer.close()


async def process_answers(user_id: int, user_info: dict, bot: Bot):
    response = await filter_data(user_info)

    if response is not None:
        await bot.send_message(chat_id=user_id, text=response)
        return
    
    weather_data = await get_weather_data(user_info)


    await send_weather_plots(weather_data, user_id, bot, user_info["period"])