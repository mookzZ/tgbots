import os, asyncio, json, re
from fileinput import close

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from requests import get_data, get_coin, get_joke, fetch_ebay_links
from datetime import datetime

# globals
load_dotenv("/src")
BOT_TOKEN = os.getenv('BOT_TOKEN')
CARD = os.getenv('CARD')
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot=bot)
ebay_state = {}

logs_path = "logs/"
if not os.path.exists(logs_path):
    os.makedirs(logs_path)

def get_current_time():
    return datetime.now().strftime("%Y-%m-%d | %H:%M:%S")

# START HANDLER -> gives all bot opportunities
@dp.message(CommandStart())
async def start(message: Message):
    text = f"Hello, {message.from_user.full_name}"
    with open(f"{logs_path}start.txt", "a", encoding="utf-8") as f:
        f_now = get_current_time()
        f.write(f"{f_now} || ID={message.from_user.id} FULL_NAME={message.from_user.full_name} USERNAME={message.from_user.username} IS_PREMIUM={message.from_user.is_premium} \n")

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Crypto-coins", callback_data="crypto"),
            InlineKeyboardButton(text="Schedule", callback_data="schedule"),
        ],
        [
            InlineKeyboardButton(text="Joke", callback_data="joke"),
            InlineKeyboardButton(text="eBay finder", callback_data="ebay"),
        ]
    ])
    await message.reply(text, reply_markup=markup)

# Crypto and Schedule HANDLER -> crypto[info, coins], schedule[week days]
@dp.callback_query(lambda call: call.data in ["crypto", "schedule"])
async def callbacks(call: CallbackQuery):
    if call.data == "crypto":
        text = "Crypto-bot:"
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Info", callback_data="info"),
                InlineKeyboardButton(text="Coins", callback_data="coins"),
            ]
        ])
        await call.message.answer(text, reply_markup=markup)
    elif call.data == "schedule":
        text = "Schedule IT-1-23:"
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="ПН", callback_data="monday"),
                InlineKeyboardButton(text="ВТ", callback_data="tuesday")
            ],
            [
                InlineKeyboardButton(text="СР", callback_data="wednesday"),
                InlineKeyboardButton(text="ЧТ", callback_data="thursday")
            ],
            [
                InlineKeyboardButton(text="ПТ", callback_data="friday"),
                InlineKeyboardButton(text="СБ", callback_data="saturday")
            ]
        ])
        await call.message.answer(text, reply_markup=markup)

# week days HANDLER
@dp.callback_query(lambda call: call.data in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"])
async def callbacks(call: CallbackQuery):
    with open('src/schedule.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    text = None
    for day in data:
        if day["id"] == call.data:
            lessons = day["lessons"]
            text = f"{day['id'].capitalize()}:\n" + "\n".join(
                [f"{i + 1}: {lesson}" for i, lesson in enumerate(lessons)])
            break
    await call.message.reply(text)

# crypto coins HANDLER, every single coin info
@dp.callback_query(lambda call: call.data in ["info", "coins"])
async def callback(call: CallbackQuery) -> None:
    if call.data == "info":
        await bot.send_message(call.message.chat.id,f"Hello, {call.from_user.full_name}, please donate us: {CARD} (VISA)")
    elif call.data == "coins":
        data = await get_data("https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&per_page=10")
        text = "Coins available:"
        buttons = [
            [InlineKeyboardButton(text=f"{coin['name']}", callback_data=f"coin_{coin['id']}")]
            for coin in data
        ]
        markup = InlineKeyboardMarkup(inline_keyboard=buttons)
        await bot.send_message(call.message.chat.id, text, reply_markup=markup)

@dp.callback_query(lambda call: call.data.startswith("coin_"))
async def callback(call: CallbackQuery) -> None:
    id = call.data.replace("coin_", "")
    data = await get_coin(f"https://api.coingecko.com/api/v3/coins/{id}")
    link = f"Coin: [{id}]({data["links"]["homepage"][0]}) \n" + f"{data["market_data"]["current_price"]["usd"]} USD"
    await bot.send_message(call.message.chat.id, link, parse_mode="Markdown")

# joke handler categories
@dp.callback_query(lambda call: call.data == "joke")
async def callback(call: CallbackQuery) -> None:
    text = "Select joke type:"
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Any", callback_data="joke_Any"),
        ],
        [
            InlineKeyboardButton(text="Programming", callback_data="joke_Programming"),
            InlineKeyboardButton(text="Misc", callback_data="joke_Misc"),
        ],
        [
            InlineKeyboardButton(text="Dark", callback_data="joke_Dark"),
            InlineKeyboardButton(text="Pun", callback_data="joke_Pun"),
        ],
        [
            InlineKeyboardButton(text="Spooky", callback_data="joke_Spooky"),
            InlineKeyboardButton(text="Christmas", callback_data="joke_Christmas"),
        ]
    ])
    await call.message.answer(text, reply_markup=markup)

@dp.callback_query(lambda call: call.data.startswith("joke_"))
async def callback(call: CallbackQuery) -> None:
    id = call.data.replace("joke_", "")
    joke = await get_joke(id)
    print(joke)
    def escape_markdown(text):
        return re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', text)
    if joke["type"] == "single":
        await bot.send_message(call.message.chat.id, text=f"||id: {joke["id"]}|| \n{escape_markdown(joke["joke"])}", parse_mode="MarkdownV2")
    else:
        await bot.send_message(call.message.chat.id,text=(f"||id: {joke["id"]}|| \n{escape_markdown(joke['setup'])}\n" + f"{escape_markdown(joke["delivery"])}"), parse_mode="MarkdownV2")

# ebay finder
@dp.callback_query(lambda call: call.data == "ebay")
async def callback(call: CallbackQuery) -> None:
    user_id = call.from_user.id
    ebay_state[user_id] = True
    await bot.send_message(call.message.chat.id, text=f"Send the product name that you want to find: ")

@dp.message()
async def search_item(message: Message):
    user_id = message.from_user.id
    if ebay_state.get(user_id, False):
        query = message.text
        await message.answer("Searching...")
        try:
            links = await fetch_ebay_links(query)
            if links:
                response = "\n\n".join(links)
                ebay_state[user_id] = False
                await message.answer(f"There are they:\n{response}")
            else:
                ebay_state[user_id] = False
                await message.answer("Nothing found.")
        except Exception as e:
            ebay_state[user_id] = False
            print(e)
            await message.answer("Error. Try again later.")


async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    print("Loading...")
    asyncio.run(main())