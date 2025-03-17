from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from telegram_bot.models import UserTest
from asgiref.sync import sync_to_async
from aiogram.types import FSInputFile
import os

from telegram_bot.bot_funcs.save_photo import load_file_id, save_file_id
from telegram_bot.bot_funcs.risk_categories import risk_categories



async def send_question(message:Message,state:FSMContext):
    data = await state.get_data()
    questions = data["questions"]
    index = data["index"]

    if index >= len(questions):
        await finish_test(message, state, message.bot)
        return

    question_text = questions[index]
    

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👍Ҳа",callback_data="answer:1"),
        InlineKeyboardButton(text="👎Йўқ", callback_data="answer:0")],
    ])
    await message.answer(f"{index + 1}. {question_text}", reply_markup=keyboard)





async def finish_test(message: Message, state: FSMContext, bot:Bot):
    data = await state.get_data()
    total_score = data["score"]
    user_test_id = data["user_test_id"]
    category = data["category"]

    # Update the test record in the database
    await sync_to_async(update_test_status, thread_sensitive=True)(user_test_id, total_score)


    risk_message = (
        f"📝 Тест тугади!\n\n"
        f"{get_category_risk_message(category, total_score)}\n\n"
        f"👉 Javohir Medical Centre'га мурожаат қилишингиз мумкин:\n"
        f"📞 <a href='tel:+998554030666'>554030666</a>\n"
        f"📞 <a href='tel:+998554020666'>554020666</a>\n\n"
        f"🔗 <a href='https://javohirmedical.com/check-up/'>Батафсил маълумот</a>"
    )


    file_id = load_file_id()

    if file_id:
        # Send photo using cached file_id (Faster)
        await message.answer_photo(
            photo=file_id,
            caption=risk_message,
            parse_mode="HTML"
        )
    else:
        # If no cached file_id, upload the photo
        current_dir = os.path.dirname(os.path.abspath(__file__))
        photo_path = os.path.join(current_dir, "photos", "logo.jpg")
        msg = await bot.send_photo(message.chat.id, photo=FSInputFile(photo_path), caption=risk_message, parse_mode="HTML")

        # Save new file_id for future use
        new_file_id = msg.photo[-1].file_id
        save_file_id(new_file_id)


    # current_dir = os.path.dirname(os.path.abspath(__file__))
    # photo_path = os.path.join(current_dir, "photos", "logo.jpg")
    # photo = FSInputFile(photo_path)

    # await message.answer_photo(
    #     photo=photo,
    #     caption=risk_message,
    #     parse_mode="HTML"
    # )

    # Reset state
    await state.clear()



def update_test_status(user_test_id, total_score):
    UserTest.objects.filter(id=user_test_id).update(status="tugatgan",score=total_score)


def get_category_risk_message(category:str, score:int):
    risk_thresholds_group_1 = {"Kardio", "Neyro", "Onko", "Bolajon", "Nuroniy"}
    risk_thresholds_group_2 = {"Yosh Oila", "Erkaklar", "Onko", "Bolajon", "Ayollar"}

    if category not in risk_categories:
        return "Категория топилмади."

    if category == "Umumiy":
        if score <=5:
            return f"✅ {risk_categories[category]['✅']}"
        elif 6 <= score <=10:
            return f"⚠ {risk_categories[category]['⚠']}"
        elif 11<= score <=15:
            return f"🚨 {risk_categories[category]['🚨']}"
        else:
            return "🚨 Сизга шошилинч тиббий кўрик ва маслаҳат зарур."

    
    if category in risk_thresholds_group_1:
        low, medium = 3, 7
    elif category in risk_thresholds_group_2:
        low, medium = 5, 10
    else:
        return "Риск мезонлари аниқланмади."

    
    if score <=low:
        return f"✅ {risk_categories[category]['✅']}"
    elif low < score < medium:
        return f"⚠ {risk_categories[category]['⚠']}"
    else:
        return f"🚨 {risk_categories[category]['🚨']}"