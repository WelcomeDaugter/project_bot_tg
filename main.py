import asyncio
import logging
from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command
from config_reader import config
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from handlers.middleware import RegistrationMiddleware
from handlers import common, crypto
from handlers.common import common_router
from handlers.crypto import crypto_router
from bd import init_db, is_registered
bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher()

# Вы нашли пасхалку)
@dp.message(Command("dice"))
async def cmd_dice(message: types.Message):
    await message.answer_dice(emoji="🎲")

async def main():
    init_db()
    dp.update.middleware(RegistrationMiddleware())

    dp.include_routers(common_router, crypto_router)
    try:
        await bot.delete_webhook(drop_pending_updates=True)

        print("Бот запущен")
        await dp.start_polling(bot)

    except (KeyboardInterrupt, SystemExit):
        print("\nПолучен сигнал остановки...")
    except Exception as e:
        print(f"\nКритическая ошибка: {repr(e)}")
    finally:
        try:
            print("Закрытие соединений...")
            await bot.session.close()
            await bot.close()
            print("Ресурсы освобождены")
        except Exception as e:
            print(f"Ошибка при закрытии: {repr(e)}")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Принудительное завершение")
    except Exception as e:
        print(f"Необработанная ошибка: {repr(e)}")
    finally:
        print("Работа программы завершена")