from aiogram import types, Router, F
from aiogram.filters import CommandStart, Command, or_f
from aiogram.enums.parse_mode import ParseMode
from aiogram.utils.formatting import as_list, as_marked_section, Bold


from filters.chat_types import ChatTypeFilter
from kbds import reply


user_private_router = Router()

# Установка фильтра для сообщений только из чатов
user_private_router.message.filter(ChatTypeFilter(["private"]))


@user_private_router.message(F.text.lower() == "варианты оплаты")
@user_private_router.message(Command("payment"))
async def payment_cmd(message: types.Message):
    text = as_marked_section(
        Bold("Варианты оплаты:"),
        "Картой в боте",
        "При получении карта/кеш",
        "В заведении",
        marker="✅",
    )
    await message.answer(text.as_html())


# @user_private_router.message(
#     (F.text.lower().contains("доставк")) | (F.text.lower() == "варианты доставки")
# )
# @user_private_router.message(Command("shipping"))
# async def menu_cmd(message: types.Message):
#     text = as_list(
#         as_marked_section(
#             Bold("Варианты доставки/заказа:"),
#             "Курьер",
#             "Самовынос (сейчас прибегу заберу)",
#             "Покушаю у Вас (сейчас прибегу)",
#             marker="✅ ",
#         ),
#         as_marked_section(Bold("Нельзя:"), "Почта", "Голуби", marker="❌ "),
#         sep="\n----------------------\n",
#     )
#     await message.answer(text.as_html())


# если оставить декоратор пустым, то бот будет реагировать
# на любые сообщения
@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer(
        "Привет, я виртуальный помощник",
        #  reply_markup=reply.start_kb3.as_markup(
        reply_markup=reply.get_keyboard(
            # "Меню",
            "О нас",
            # "Варианты оплаты",
            # "Варианты доставки",
            # reize_keyboard=True,
            # input_field_placeholder="Что вас интересует?",
            placeholder="Что вас интересует?",
            sizes=(2, 2),
        ),
    )


# @user_private_router.message(
#     (F.text.lower().contains("доставк")) | (F.text.lower() == "варианты доставки")
# )
# @user_private_router.message(Command("shipping"))
# async def menu_cmd(message: types.message):
#     await message.answer("Варианты доставки:")


@user_private_router.message(F.text.lower() == "о нас")
@user_private_router.message(Command("about"))
async def about_cmd(message: types.Message):
    await message.answer("О нас: ")


# @user_private_router.message(F.contact)
# async def get_contact(message: types.Message):
#     await message.answer(f"номер получен")
#     await message.answer(str(message.contact))


# @user_private_router.message(F.location)
# async def get_location(message: types.Message):
#     await message.answer(f"Локация получен")
#     await message.answer(str(message.location))


# функцию ниже нужно писать после старта
# иначе оно захватится первым и команда start_cmd никогда ъ
# не заработает
# or_f - эта функция конвертирует запятые в логические "или",
# потому что по умолчаниюстоят логичекие "и"

# @user_private_router.message(F.text.lower() == 'меню')
# @user_private_router.message(or_f(Command("menu"), (F.text.lower() == "меню")))
# async def menu_cmd(message: types.Message):
    # await message.answer(message.text)

    # reply.del_kbd - удаление клавиатуры с конпками после выбора команды "меню"
    # ещё можно вывести новую клавиатуру если нужно
    
    # await message.answer("Вот меню: ", reply_markup=reply.del_kbd)
    
    # await message.reply(message.text)
    # Если нужна реализация ниже, то к параметрам
    # функции нужно добавить "bot: Bot"
    # await bot.send_message(message.from_user.id, 'Ответ:')

    # text = message.text
    # if text in ['Привет', 'привет', 'hi', 'hello']:
    #     await message.answer("И тебе привет!")
    # elif text in ['пока', 'Пока', 'goodbye', 'bye']:
    #     await message.answer("И тебе пока!")
    # else:
    #     await message.answer(message.text)


# Если пользователь напишет пространный текст,
# то будет обрабатываться событие ниже;
# Вообще вместо F.text можно записать F.photo
# или F.audio, бот будет реагировать в зависисмости
# от контента, которго мы отправляем

# @user_private_router.message(F.text.lower() == 'варианты доставки')
# async def menu_cmd(message: types.Message):
#     await message.answer("Это магический фильтр")


# При перечеслении через запятую обработчик считывает это
# как логичекое "и", можно вместо запятой поставить "&",
# а если нужно получить логическое "или",
# то ставим ветикальную черту "|"
# при использовании оператора | и & нужно выражения записать в скобках


# @user_private_router.message(
#     (F.text.lower().contains("доставк")) | (F.text.lower() == "варианты доставки")
# )
# async def menu_cmd(message: types.Message):
#     await message.answer("Это магический фильтр")


# можно использовать регулярные выражения
# F.text.regexp(r"Hello, .+")
# ~(F.text.lower().contains('варианты доставки')) - работает наобзрот
#
# @user_private_router.message(F.text.lower().contains('варианты доставки'))
# async def menu_cmd(message: types.Message):
#     await message.answer("Это магический фильтр 2")
