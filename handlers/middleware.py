from aiogram import BaseMiddleware
from aiogram.types import Message
from bd import is_registered

class RegistrationMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        if not (message := event.message or event.callback_query and event.callback_query.message):
            return await handler(event, data)

        if message.text and message.text.startswith(('/start', '/reg')):
            return await handler(event, data)

        if (state := data.get('state')) and (current_state := await state.get_state()):
            if "RegisterState" in current_state:
                return await handler(event, data)

        if not await is_registered(message.from_user.id):
            await message.answer("❌ Сначала пройдите регистрацию /reg")
            return

        return await handler(event, data)