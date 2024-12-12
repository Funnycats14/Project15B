import asyncio
import logging
import sys
from utils import process_answers

from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery


TOKEN = "YOUR_BOT_TOKEN"

dp = Dispatcher()
bot = None
users = {}

# Creating keyboards
# 1 - Point selection
builder_point = InlineKeyboardBuilder()
builder_point.button(
    text="Add intermediate city(or first)", callback_data="intermediate"
)
builder_point.button(text="Add final city", callback_data="final")
builder_point.adjust(1)
point_selection_kb = builder_point.as_markup()
# 2 - Period selection
builder_period = InlineKeyboardBuilder()
builder_period.button(text="1 day", callback_data="1")
builder_period.button(text="3 days", callback_data="3")
builder_period.button(text="5 days", callback_data="5")
builder_point.adjust(1)
period_selection_kb = builder_period.as_markup()


class WeatherStates(StatesGroup):
    point_selection = State()
    intermediate_point_input = State()
    final_point_input = State()
    period_selection = State()


@dp.callback_query(lambda c: c.data == "intermediate")
async def callback_intermediate_handler(
    query: CallbackQuery, state: FSMContext
) -> None:
    await state.set_state(WeatherStates.intermediate_point_input)
    await query.message.answer("Please enter the city name")


@dp.callback_query(lambda c: c.data == "final")
async def callback_final_handler(query: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(WeatherStates.final_point_input)
    await query.message.answer("Please enter the city name")

@dp.callback_query(lambda c: c.data in ["1", "3", "5"])
async def callback_period_selection_handler(
    query: CallbackQuery, state: FSMContext
) -> None:
    period = int(query.data)
    users[query.from_user.id]["period"] = period
    await state.clear()
    await query.message.answer(f"You have selected a forecast period of {period} days.")
    await query.message.answer("Please wait, I'm getting the weather data...")
    await asyncio.create_task(process_answers(query.message.chat.id, users[query.from_user.id], bot))


@dp.message(Command("start"))
async def command_start_handler(message: Message, state: FSMContext) -> None:
    users[message.from_user.id] = {}
    current_state = await state.get_state()
    if current_state is not None:
        await state.clear()

    text = (
        f"Hello, {message.from_user.full_name}! I'm a weather bot!\n"
        "You can use the following commands:\n"
        "/start - Start the bot\n"
        "/help - Get help\n"
        "/weather - Get weather"
    )
    await message.answer(text)


@dp.message(Command("help"))
async def command_start_handler(message: Message) -> None:
    text = (
        "To acess the weather, use the command /weather\n"
        "On each step you will be asked to enter the city name\n"
        "After that you will choose forefast period in days (1, 3, 5)\n"
        "At the end, you will receive the weather forecast for the next X days for chosen cities"
    )
    await message.answer(text)


@dp.message(Command("weather"))
@dp.message(WeatherStates.point_selection)
async def command_start_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(WeatherStates.point_selection)
    await message.answer(
        "Please choose which type of point you want to add",
        reply_markup=point_selection_kb,
    )


@dp.message(WeatherStates.intermediate_point_input)
async def intermediate_point_input_handler(message: Message, state: FSMContext) -> None:
    if "intermediate" not in users[message.from_user.id]:
        users[message.from_user.id]["intermediate"] = [message.text]
    else:
        users[message.from_user.id]["intermediate"].append(message.text)
    await state.set_state(WeatherStates.point_selection)
    await message.answer(
        "Please choose which type of point you want to add",
        reply_markup=point_selection_kb,
    )


@dp.message(WeatherStates.final_point_input)
async def final_point_input_handler(message: Message, state: FSMContext) -> None:
    users[message.from_user.id]["final"] = message.text
    await state.set_state(WeatherStates.period_selection)
    await message.answer(
        "Please choose the forecast period",
        reply_markup=period_selection_kb,
    )


async def main() -> None:
    global bot
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
