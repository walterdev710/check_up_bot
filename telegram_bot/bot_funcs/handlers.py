import logging
from asgiref.sync import sync_to_async
from aiogram import html
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold
import asyncio
from django.db.utils import IntegrityError


from telegram_bot.models import Patient, TestQuestion, UserTest
from telegram_bot.bot_funcs.keyboards import contact_keyboard, get_tests_keyboard, user_pages, tests

from telegram_bot.bot_funcs.states import TestStates
from telegram_bot.bot_funcs.question_control import send_question





async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with /start command and checks if the user is registered
    """
    user_id = message.from_user.id
    full_name = message.from_user.full_name

    user_exists = await sync_to_async(Patient.objects.filter(user_id=user_id).exists)()

    if user_exists:
        await message.answer(f"👋 Салом, {html.bold(full_name)}! Сиз аллақачон рўйхатдан ўтгансиз. Хуш келибсиз! 😊", reply_markup=get_tests_keyboard(user_id, 0))
        await message.answer("Check-up Дастурларимиздан бирини тангланг👇")

    else:
        await message.answer(f"👋 Салом, {html.bold(message.from_user.full_name)}☺️\nИлтимос Рўйхатдан ўтиш учун рақамингизни юборинг👇",
        reply_markup=contact_keyboard
        )

async def contact_handler(message:Message):
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    phone_number = message.contact.phone_number

    try:
        user,created = await sync_to_async(Patient.objects.get_or_create)(
            user_id=user_id,
            defaults={
                "full_name":full_name,
                "phone_number":phone_number,
            }
        )
        if created:
            await message.answer("✅ Рўйхатдан муваффақиятли ўтдингиз!",reply_markup=get_tests_keyboard(user_id, 0))
            await message.answer("Check-up Дастурларимиздан бирини тангланг👇")
        
    except IntegrityError:
        logging.info("An error occurred while saving your data. Please try again.")


async def pagination_test(message:Message):
    user_id = message.from_user.id
    current_page = user_pages.get(user_id, 0)

    if message.text == "⬅️ Oldingi":
        new_page = max(0, current_page - 1)
    else:
        max_page = (len(tests) - 1)
        new_page = min(max_page, current_page+1)

    await message.answer("Саҳифа ўзгартирилди✅", reply_markup=get_tests_keyboard(user_id, new_page))

async def start_test(message:Message, state:FSMContext):
    full_category = message.text.strip()

    category = full_category.split(' ',1)[1] if ' ' in full_category else full_category       
    # print(f"Looking for category: {category}")

    # user,created =  await sync_to_async(Patient.objects.get_or_create)(user_id=message.from_user.id, defaults={"full_name":message.from_user.full_name})

    questions_count = await sync_to_async(TestQuestion.objects.filter(category=category).count)()
    # print(f"Found {questions_count} questions in category: {category}")
    
    if questions_count == 0:
        await message.answer("Бу категорияда саволлар мавжуд эмас")
        return

    # user_test, _ = await sync_to_async(UserTest.objects.get_or_create)(user=user, test_name=category, defaults={"status":"jarayonda", "score":0})

    await state.update_data(category=category,user_id= message.from_user.id)

    start_test_btn = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="📝 Тестни бошлаш", callback_data=f"start_test:{category}")]]
    )



    await message.answer(
        f"📋 Сиз {category} категориясини танладингиз.\n"
        f"Бу категорияда {questions_count} та савол бор.\n\n"
        f"Тестни бошлаш учун қуйидаги тугмани босинг:",
        reply_markup=start_test_btn
    )


    # await state.set_state(TestStates.answering_questions)

    # await send_question(message,state)


async def process_start_test(callback:CallbackQuery, state:FSMContext):
    category = callback.data.split(":")[1]
    data = await state.get_data()
    user_id = data.get("user_id")

    questions = await sync_to_async(list)(TestQuestion.objects.filter(category=category))

    user = await sync_to_async(Patient.objects.get)(user_id=user_id)
    user_test, _ = await sync_to_async(UserTest.objects.get_or_create)(
        user=user, test_name=category, defaults={"status": "jarayonda", "score": 0}
    )

    await sync_to_async(user_test.refresh_from_db)()

    if callback.message.reply_markup:
        await callback.message.edit_reply_markup(reply_markup=None)

    await state.update_data(
        questions=questions,
        index=0,
        score=0,
        user_test_id=user_test.id
    )

    await state.set_state(TestStates.answering_questions)
    await send_question(callback.message, state)

    await callback.answer()



async def handler_answer(callback:CallbackQuery, state:FSMContext):
    score = int(callback.data.split(":")[1])

    data = await state.get_data()
    current_score = data["score"]
    index = data["index"]
    category = data["category"]

    special_scoring = {
        "Yosh Oila":{5:10},
    }

    points =special_scoring.get(category,{}).get(index,1)*score

    await state.update_data(
        score = current_score + points,
        index = index+1
    )

    await callback.message.edit_reply_markup(reply_markup=None)

    await send_question(callback.message, state)


async def handle_unexpected_messages(message:Message):
    """Delete any text messages sent while answering questions."""
    await message.delete()


async def reject_manual_number(message: Message):
    """Delete manually typed phone numbers and ask to use the button."""
    await message.delete()
    
    await message.answer(
        f"📢 Ҳурматли {hbold(message.from_user.username)}, "
        "телефон рақамингизни '📲 Raqamni yuborish' тугмаси орқали юборишингиз сўрайман! ✅"
    )

async def handle_invalid_message(message:Message):
    try:
        await message.delete()
    except Exception as e:
        logging.error(f"Error deleting message: {e}")
    
    warning = await message.answer("❌ Бот матн қабул қилмайди, фақат тугмалардан фойдаланинг.")

    await asyncio.sleep(3)
    await warning.delete()