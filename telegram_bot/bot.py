import django

import asyncio
import logging
import sys
import os
from dotenv import load_dotenv
from aiogram import Router, F


from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mybot.settings")
django.setup()

from telegram_bot.bot_funcs.handlers import command_start_handler, contact_handler, pagination_test, handler_answer, start_test, process_start_test, handle_unexpected_messages, reject_manual_number, handle_invalid_message
from telegram_bot.bot_funcs.states import TestStates

from telegram_bot.bot_funcs.keyboards import tests, VALID_BUTTONS

load_dotenv()
TOKEN =  os.getenv("BOT_TOKEN")

dp = Dispatcher()
router = Router()

router.message.register(command_start_handler, CommandStart())
router.message.register(
    reject_manual_number, 
    lambda message: message.text and message.text.replace("+", "").isdigit()
)


router.message.register(contact_handler, lambda message: message.contact is not None)
router.message.register(pagination_test, F.text.in_(["⬅️ Oldingi", "Keyingi ➡️"]))
router.message.register(start_test, lambda message:message.text in tests)
router.message.register(handle_unexpected_messages, lambda message: True, TestStates.answering_questions)
router.message.register(handle_invalid_message, F.text.not_in(VALID_BUTTONS))

router.callback_query.register(process_start_test, lambda c: c.data.startswith("start_test:"))
router.callback_query.register(handler_answer, F.data.startswith("answer"))

dp.include_router(router)

async def main() ->None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
