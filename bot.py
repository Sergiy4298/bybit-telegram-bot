import logging
from aiogram import Bot, Dispatcher, types, executor
import requests
import pandas as pd
import pandas_ta as ta
import numpy as np

# Токен з BotFather
API_TOKEN = "ВАШ_ТОКЕН_ТУТ"  # ⚠️ Заміни на свій токен!

# Налаштування логування
logging.basicConfig(level=logging.INFO)

# Ініціалізація бота та диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


# Отримання закритих цін з Binance
def fetch_kline_closes(symbol="BTCUSDT", interval="15m", limit=100):
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    response = requests.get(url, params=params)
    data = response.json()
    closes = [float(candle[4]) for candle in data]  # close ціни
    return closes


# Прогнозування руху
def predict_direction(prices):
    df = pd.DataFrame({'close': prices})

    sma = ta.sma(df['close'], length=14)
    rsi = ta.rsi(df['close'], length=14)
    macd_df = ta.macd(df['close'])

    if macd_df is None or rsi is None or sma is None:
        return "⚠️ Не вдалося розрахувати індикатори."

    # Додаємо MACD значення до df
    df['rsi'] = rsi
    df['macd'] = macd_df['MACD_12_26_9']
    df['signal'] = macd_df['MACDs_12_26_9']

    try:
        if df['rsi'].iloc[-1] < 30 and df['macd'].iloc[-1] > df['signal'].iloc[-1]:
            return "📈 Вгору (LONG)"
        elif df['rsi'].iloc[-1] > 70 and df['macd'].iloc[-1] < df['signal'].iloc[-1]:
            return "📉 Вниз (SHORT)"
        else:
            return "➡️ Бічний рух або невизначеність"
    except Exception as e:
        return f"⚠️ Помилка під час обробки індикаторів: {e}"


# Команда /start
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.reply("Привіт! Надішли /predict щоб отримати прогноз на 15 хвилин по BTC/USDT.")


# Команда /predict
@dp.message_handler(commands=["predict"])
async def predict(message: types.Message):
    try:
        prices = fetch_kline_closes()
        prediction = predict_direction(prices)
        await message.reply(f"📊 Прогноз на 15 хвилин:\n\n{prediction}")
    except Exception as e:
        logging.exception("Помилка під час виконання /predict")
        await message.reply(f"⚠️ Помилка: {e}")


# Відповідь на всі інші повідомлення
@dp.message_handler()
async def unknown(message: types.Message):
    await message.reply("Я поки що розумію лише /start та /predict.")


# Запуск бота
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
