import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from pybit.unified_trading import HTTP

API_TOKEN = '7810382966:AAExs7mlhKqLy-ogQvleEPJv5Suniw62oNg'
BYBIT_API_KEY = 'YOUR_BYBIT_API_KEY'
BYBIT_API_SECRET = 'YOUR_BYBIT_API_SECRET'
AUTHORIZED_USERS = [770139883]

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

session = HTTP(
    api_key=BYBIT_API_KEY,
    api_secret=BYBIT_API_SECRET,
    testnet=True
)

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    if message.from_user.id not in AUTHORIZED_USERS:
        await message.reply("⛔ У вас немає доступу до цього бота.")
        return
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("📊 Баланс"), KeyboardButton("📈 Відкрити Long"))
    await message.reply("Вітаю! Я бот для торгівлі на Bybit", reply_markup=keyboard)

@dp.message_handler(lambda message: message.text == "📊 Баланс")
async def balance_handler(message: types.Message):
    if message.from_user.id not in AUTHORIZED_USERS:
        await message.reply("⛔ У вас немає доступу до цього бота.")
        return
    wallet = session.get_wallet_balance(accountType="UNIFIED")
    usdt_balance = wallet['result']['list'][0]['coin'][0]['availableToWithdraw']
    await message.reply(f"💰 Доступний баланс USDT: {usdt_balance}")

@dp.message_handler(lambda message: message.text == "📈 Відкрити Long")
async def open_long(message: types.Message):
    if message.from_user.id not in AUTHORIZED_USERS:
        await message.reply("⛔ У вас немає доступу до цього бота.")
        return
    response = session.place_order(
        category="linear",
        symbol="BTCUSDT",
        side="Buy",
        orderType="Market",
        qty=0.001,
        timeInForce="GoodTillCancel"
    )
    await message.reply(f"✅ Ордер на Long відкрито!\nOrder ID: {response['result']['orderId']}")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)