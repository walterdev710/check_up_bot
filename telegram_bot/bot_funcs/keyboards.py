from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

contact_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="📞 Raqamni yuborish", request_contact=True)]],
    resize_keyboard=True,
    one_time_keyboard=True
)


tests = [
    "🩺 Umumiy",       
    "👶 Bolajon",     
    "👴 Nuroniy",      
    "❤️ Kardio",      
    "🏡 Yosh Oila",  
    "🧠 Neyro",        
    "🎗️ Onko",
    "👩‍⚕️ Ayollar",
    "👨‍⚕️ Erkaklar",        
    ]

TEST_PER_PAGE = 4
user_pages = {}

VALID_BUTTONS = tests + ["⬅️ Oldingi", "Keyingi ➡️"]


def get_tests_keyboard(user_id:int, page:int=0):
    user_pages[user_id] = page

    keyboard = ReplyKeyboardBuilder()

    start_idx = page * TEST_PER_PAGE
    end_idx = start_idx + TEST_PER_PAGE

    current_tests = tests[start_idx:end_idx]

    for i in range(0, len(current_tests), 2):
        row_buttons = [KeyboardButton(text=current_tests[i])]
        if i + 1 < len(current_tests):
            row_buttons.append(KeyboardButton(text=current_tests[i + 1]))
        keyboard.row(*row_buttons)

    navigation_btns =[]

    if page >0:
        navigation_btns.append(KeyboardButton(text="⬅️ Oldingi"))
    if end_idx < len(tests):
        navigation_btns.append(KeyboardButton(text="Keyingi ➡️"))


    if navigation_btns:
        keyboard.row(*navigation_btns)
    
    return keyboard.as_markup(resize_keyboard=True)

    