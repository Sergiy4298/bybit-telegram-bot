import logging
import requests
import pandas as pd
import ta
from aiogram import Bot, Dispatcher, executor, types

API_TOKEN = "7557990762:AAHsPB9g7S7ZJWDOwSt3GiR-Pt23C8xSmaA"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Отримання закритих цін з Binance
def fetch_kline_closes(symbol="BTCUSDT", interval="15m"):
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": 100
    }
    response = requests.get(url, params=params)
    try:
        data = response.json()
        if isinstance(data, dict) and data.get("code"):
            raise ValueError(f"Binance API error: {data['msg']}")
        if not data or len(data) < 30:
            raise ValueError("Недостатньо історичних даних з Binance")
    except Exception as e:
        raise ValueError(f"Помилка при обробці відповіді Binance: {e}")
    
    closes = [float(candle[4]) for candle in data]
    return closes

# Прогнозування руху
def predict_direction(prices):
    df = pd.DataFrame({'close': prices})
    if len(df) < 20:
        return "⚠️ Недостатньо даних для аналізу."
    try:
        sma = ta.trend.sma_indicator(df['close'], window=14)
        rsi = ta.momentum.rsi(df['close'], window=14)
        macd = ta.trend.macd(df['close'])
        signal = ta.trend.macd_signal(df['close'])

        if sma.isna().any() or rsi.isna().any() or macd.isna().any() or signal.isna().any():
            return "⚠️ Індикатори ще не сформувались повністю."

        df['sma'] = sma
        df['rsi'] = rsi
        df['macd'] = macd
        df['signal'] = signal

        last_rsi = df['rsi'].iloc[-1]
        last_macd = df['macd'].iloc[-1]
        last_signal = df['signal'].iloc[-1]

        if last_rsi < 30 and last_macd > last_signal:
            return "📈 Вгору (LONG)"
        elif last_rsi > 70 and last_macd < last_signal:
            return "📉 Вниз (SHORT)"
        else:
            return "➡️ Бічний рух або невизначено"
    except Exception as e:
        return f"⚠️ Помилка під час обробки: {e}"

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
        await message.reply(f"📊 Прогноз на 15 хв: {prediction}")
    except Exception as e:
        logging.exception("Помилка у функції predict")
        await message.reply(f"⚠️ Помилка: {e}")

# Обробка інших повідомлень
@dp.message_handler()
async def unknown(message: types.Message):
    await message.reply("Я поки що розумію лише /start та /predict.")

# Запуск бота
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
