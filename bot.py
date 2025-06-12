import logging
from aiogram import Bot, Dispatcher, types, executor
import requests
import talib
import numpy as np

API_TOKEN = "7557990762:AAHsPB9g7S7ZJWDOwSt3GiR-Pt23C8xSmaA"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

def fetch_klines(symbol="BTCUSDT", interval="15m", limit=100):
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    response = requests.get(url, params=params)
    data = response.json()
    return [float(candle[4]) for candle in data]  # Close prices

def predict_direction(prices):
    closes = np.array(prices)
    sma = talib.SMA(closes, timeperiod=14)
    rsi = talib.RSI(closes, timeperiod=14)
    macd, signal, _ = talib.MACD(closes, fastperiod=12, slowperiod=26, signalperiod=9)

    if rsi[-1] < 30 and macd[-1] > signal[-1]:
        return "⬆ Вгору (LONG)"
    elif rsi[-1] > 70 and macd[-1] < signal[-1]:
        return "⬇ Вниз (SHORT)"
    else:
        return "➡ Бічний рух або невизначеність"

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.reply("Привіт! Надішли /predict щоб отримати прогноз BTC/USDT на 15 хвилин.")

@dp.message_handler(commands=["predict"])
async def predict(message: types.Message):
    try:
        prices = fetch_klines()
        forecast = predict_direction(prices)
        await message.reply(f"📈 Прогноз на 15 хвилин для BTC/USDT:
{forecast}")
    except Exception as e:
        await message.reply(f"⚠️ Помилка під час обробки: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)
