from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove, BufferedInputFile
from handlers.middleware import RegistrationMiddleware
import matplotlib.pyplot as plt
from bd import is_registered
from keyboards.keyboard import help_button
from aiogram.filters import Command
from aiogram.enums import ParseMode
from datetime import datetime, timedelta
from config import Config
import aiohttp
import io
crypto_router = Router()
async def crypto_price(pair: str) -> str:
    url = f"https://api.api-ninjas.com/v1/cryptoprice?symbol={pair.upper()}"
    headers = {'X-Api-Key': Config.API_NINJAS_KEY}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                data = await response.json()

                if response.status == 200:
                    return format_data(data)
                return f"❌ Ошибка API: {data.get('error', 'Unknown error')}"

    except Exception as e:
        return f"⚠️ Ошибка: {str(e)}"

def format_data(data: dict) -> str:
    symbol = data.get('symbol', 'N/A')
    price = data.get('price', 'N/A')
    timestamp = data.get('timestamp')

    if price == 'N/A':
        return price

    if '.' in price:
        price = price.rstrip('0').rstrip('.')

    if timestamp:
        try:
            formatted_time = datetime.fromtimestamp(int(timestamp)).strftime('%d.%m.%Y %H:%M:%S')
        except (ValueError, TypeError):
            formatted_time = "неизвестно"
    else:
        formatted_time = "неизвестно"

    return (
        f"🔹 <b>{symbol}</b>\n"
        f" Текущая цена: <code>{price}</code>\n"
        f" Время обновления: <i>{formatted_time}</i>\n"
    )

class CryptoStates(StatesGroup):
    waiting_for_pair = State()
    waiting_for_coin_id = State()

@crypto_router.message(Command("price"))
async def price_command(message: types.Message, state: FSMContext):
    if await is_registered(message.from_user.id):
        await state.set_state(CryptoStates.waiting_for_pair)
        await message.answer(
            "Введите пару криптовалют в формате:\n"
            "<code>BTCUSD</code> (Bitcoin → Доллар)\n"
            "<code>ETHUSD</code> (Ethereum → Доллар)\n"
            "<code>SOLBTC</code> (Solana → Bitcoin)\n"
            "<code>SUIUSD</code> (Sui → Доллар)\n\n"
            "Доступные валюты: BTC, ETH, USDT, SOL, BNB, Sui и многие другие",
            parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await message.answer("Для начала пройдите регистрацию /reg")

@crypto_router.message(F.text == "Цены криптовалют")
async def crypto_button(message: types.Message, state: FSMContext):
    await state.set_state(CryptoStates.waiting_for_pair)
    await message.answer(
        "Введите пару в формате <code>BTCUSDT</code>:",
        parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardRemove()
    )

@crypto_router.message(
    CryptoStates.waiting_for_pair,
    F.text.regexp(r'^[A-Za-z]{3,6}[A-Za-z]{3,6}$')  #Фильтр
)
async def crypto_pair(message: types.Message, state: FSMContext):
    symbol_pair = message.text.upper()
    await message.answer(f"⏳ Запрашиваю данные для {symbol_pair}...")

    try:
        result = await crypto_price(symbol_pair)
        await message.answer(result, parse_mode=ParseMode.HTML)
    except Exception as e:
        await message.answer(f"⚠️ Ошибка: {str(e)}")
    finally:
        await state.clear()

@crypto_router.message(CryptoStates.waiting_for_pair)
async def wrong_pair(message: types.Message):
    await message.answer(
        "❌ Неверный формат. Примеры:\n"
        "<code>BTCUSDT</code> - Bitcoin к доллару\n"
        "<code>ETHBTC</code> - Ethereum к Bitcoin",
        parse_mode=ParseMode.HTML
    )

# апи coingecko и построение графика

async def get_history(coin_id: str, days: int = 7, currency: str = "usd") -> list:
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": currency, "days": days, "interval": "daily"
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"API error {response.status}: {error_text}")

                data = await response.json()
                return [
                    {
                        "time": datetime.fromtimestamp(entry[0] // 1000).strftime("%d.%m.%Y"),
                        "price": entry[1]
                    }
                    for entry in data["prices"]
                ]

    except aiohttp.ClientError as e:
        raise Exception(f"Connection error: {str(e)}")
    except Exception as e:
        raise Exception(f"Unexpected error: {str(e)}")


async def chart(data: list, coin_name: str) -> BufferedInputFile:
    plt.figure(figsize=(10, 5))

    dates = [entry["time"] for entry in data]
    prices = [entry["price"] for entry in data]

    plt.plot(dates, prices, 'b-', linewidth=2)
    plt.title(f"Цена на {coin_name.upper()} (за {len(data)} дней)")
    plt.xlabel("Дата")
    plt.ylabel("Цена (USD)")
    plt.xticks()
    plt.grid(True)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    plt.close()
    return BufferedInputFile(buf.getvalue(), filename=f"{coin_name}_chart.png")

@crypto_router.message(F.text == "График криптовалют")
async def chart_command(message: types.Message, state: FSMContext):
    if await is_registered(message.from_user.id):
        await state.set_state(CryptoStates.waiting_for_coin_id)
        await message.answer(
            "Введите ID криптовалюты в следующем формате:\n"
            "<code>bitcoin</code> (BTC)\n"
            "<code>ethereum</code> (ETH)\n"
            "<code>solana</code> (SOL)\n"
            "<code>sui</code> (SUI)\n\n"
            "А также многие другие",
            parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await message.answer("Для начала пройдите регистрацию /reg")

@crypto_router.message(CryptoStates.waiting_for_coin_id, F.text)
async def handle_coin_chart(message: types.Message, state: FSMContext):
    coin_id = message.text.lower()
    try:
        processing_msg = await message.answer(f"🔄 Генерирую график для {coin_id}...")

        history = await get_history(coin_id)

        chart_file = await chart(history, coin_id)

        await message.answer_photo(
            photo=chart_file,
            caption=f"📊 {coin_id.upper()} | Текущая цена: {history[-1]['price']:.2f} USD",
            parse_mode=ParseMode.HTML
        )

    except Exception as e:
        await message.answer(f"⚠️ Ошибка при обработке: {str(e)}")
    finally:
        await state.clear()
        try:
            await processing_msg.delete()
        except:
            pass

@crypto_router.message(~Command("price", "start", "help", "menu", "chart"), ~(F.text == "Цены криптовалют"), ~(F.text == "график криптовалют"))
async def other_messages(message: types.Message):
    if await is_registered(message.from_user.id):
        await message.answer(
            "ℹ️ Для начала работы введите /price\n"
                 "Если хотите продолжить работу с графиками введите:\n"
                 "<code>График криптовалют</code>",
            parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await message.answer("Для начала пройдите регистрацию /reg")

_all__ = ['crypto_router']