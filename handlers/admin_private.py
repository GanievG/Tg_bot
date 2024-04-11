import time

from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

# from sqlalchemy import String


from filters.chat_types import ChatTypeFilter, IsAdmin
from kbds.reply import get_keyboard
from common.connect import conn


admin_router = Router()
# admin_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())


ADMIN_KB = get_keyboard(
    "Добавить запись",
    "Задания",
    # "Изменить запись",
    # "Удалить запись",
    "Я так, просто посмотреть зашел",
    placeholder="Выберите действие",
    sizes=(2, 2, 1),
)


ENTRYS_KB = get_keyboard(
    "Добавить автора",
    "Добавить книгу",
    "Добавить доставку",
    "Добавить издательство",
    "Добавить покупку",
    placeholder="Выберите действие",
    sizes=(2, 2, 1),
)

TABLES = ["Авторы", "Книги", "Доставки", "Издательства", "Покупки"]


TABLE_KB = get_keyboard(
    *TABLES,
    # "Авторы",
    # "Книги",
    # "Доставка",
    # "Издательство",
    # "Покупки",
    placeholder="Выберите таблицу",
    sizes=(2, 2, 1),
)


TASKS_KB = get_keyboard(
    "1.2",
    "1.3",
    "1.6",
    "1.9",
    placeholder="Выберите задание",
    sizes=(2, 2),
)


@admin_router.message(F.text == "Задания")
async def starring_tasks(message: types.Message):
    await message.answer("ОК, вот список заданий", reply_markup=TASKS_KB)


@admin_router.message(F.text == "1.2")
async def task_2(message: types.Message):
    cur = conn.cursor()
    cur.execute(
        "CALL Program()",
    )

    data = cur.fetchall()  # Fetch all rows from the query result
    await message.answer(str(data[0][0]))
    cur.close()


@admin_router.message(F.text == "1.3")
async def task_3(message: types.Message):
    cur = conn.cursor()
    cur.execute(
        "CALL CalculateMaxBookCost()",
    )
    data = cur.fetchall()  # Fetch all rows from the query result
    await message.answer(str(data[0][0]))
    cur.close()


@admin_router.message(F.text == "1.6")
async def task_6(message: types.Message):
    cur = conn.cursor()
    cur.execute(
        """SELECT 
            CAST(
                CASE WHEN SUM(Cost) BETWEEN 1000 AND 5000 THEN NULL)
                ELSE CONCAT('Сумма закупок = ', SUM(Cost))
            END AS CHAR) AS messaage
            FROM purchases;
        """,
    )
    data = cur.fetchall()  # Fetch all rows from the query result
    await message.answer(str(data[0][0]))


@admin_router.message(F.text == "1.9")
async def task_9(message: types.Message):
    await message.answer("Введите текст")

    @admin_router.message()
    async def get_input_text(message: types.Message):
        # user_text = message.text

        cur = conn.cursor()
        cur.execute(
            f"CALL COUNTER('{message.text}')",
        )
        data = cur.fetchall()  # Fetch all rows from the query result
        # await message.answer(str(data))
        await message.answer(str(data[0]))
        cur.close()


@admin_router.message(Command("admin"))
async def admin_features(message: types.Message):
    await message.answer("Что хотите сделать?", reply_markup=ADMIN_KB)


@admin_router.message(F.text == "Я так, просто посмотреть зашел")
async def starring_at_product(message: types.Message):
    await message.answer("ОК, вот список таблиц", reply_markup=TABLE_KB)


values = {
    "Авторы": "authors",
    "Книги": "books",
    "Доставки": "deliveries",
    "Издательства": "publishing_house",
    "Покупки": "purchases",
}


@admin_router.message(F.text == "Добавить запись")
async def starring_at_product(message: types.Message):
    await message.answer("ОК, вот список таблиц", reply_markup=ENTRYS_KB)


# @admin_router.message(F.text.lower() == "Добавить запись")
# async def add_all_author(message: types.Message, state: FSMContext):
class AddAuthor(StatesGroup):
    code_author = State()
    name_author = State()
    birthday = State()
    # image = State()

    texts = {
        "AddAuthor:code_author": "Введите код заново:",
        "AddAuthor:name_author": "Введите имя заново:",
        "AddAuthor:birthday": "Введите дату рождения заново:",
        # "AddAuthor:image": "Этот стейт последний, поэтому...",
    }


# Становимся в состояние ожидания ввода code_author
@admin_router.message(
    StateFilter(None), F.text == "Добавить автора"
)  # "Добавить автора"
async def add_author(message: types.Message, state: FSMContext):

    await message.answer(
        "Введите код автора записи", reply_markup=types.ReplyKeyboardRemove()
    )

    await state.set_state(AddAuthor.code_author)


# Хендлер отмены и сброса состояния должен быть всегда именно здесь,
# после того как только встали в состояние номер 1 (элементарная очередность фильтров)


@admin_router.message(StateFilter("*"), Command("отмена"))
@admin_router.message(StateFilter("*"), F.text.casefold() == "отмена")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:

    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await message.answer("Действия отменены", reply_markup=TABLE_KB)  # ADMIN_KB


# Вернутся на шаг назад (на прошлое состояние)
@admin_router.message(StateFilter("*"), Command("назад"))
@admin_router.message(StateFilter("*"), F.text.casefold() == "назад")
async def back_step_handler(message: types.Message, state: FSMContext) -> None:

    current_state = await state.get_state()

    if current_state == AddAuthor.code_author:
        await message.answer(
            'Предыдущего шага нет, или введите код автора или напишите "отмена"'
        )
        return

    previous = None
    for step in AddAuthor.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(
                f"Ок, вы вернулись к прошлому шагу \n {AddAuthor.texts[previous.state]}"
            )
            return
        previous = step


# Ловим данные для состояние code_author и потом меняем состояние на name_author
@admin_router.message(AddAuthor.code_author, F.text)
async def add_code(message: types.Message, state: FSMContext):
    # Здесь можно сделать какую либо дополнительную проверку
    # и выйти из хендлера не меняя состояние с отправкой соответствующего сообщения
    # например:
    if message.text.isdigit():
        await state.update_data(code_author=message.text)
        await message.answer("Введите имя автора")
        await state.set_state(AddAuthor.name_author)
    else:
        await message.answer(
            "Код автора должен быть числом больше нуля. \n Введите заново"
        )
        return


# Хендлер для отлова некорректных вводов для состояния code
@admin_router.message(AddAuthor.code_author)
async def add_code2(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели не допустимые данные, введите код")


@admin_router.message(AddAuthor.name_author, F.text)
async def add_name_author(message: types.Message, state: FSMContext):
    if len(message.text) >= 100:  # or (len(message.text) == message.text.count(" ")):
        await message.answer(
            "Имя автора не должно превышать 100 символов и состоять из пробельных символов. \n Введите заново"
        )
        return

    if any(ch.isdigit() for ch in message.text):
        await message.answer("Имя автора не должно содержать цифр. \n Введите заново")
        return

    await state.update_data(name_author=message.text)
    await message.answer("Введите дату рождения в виде год-месяц-день")
    await state.set_state(AddAuthor.birthday)


# Хендлер для отлова некорректных вводов для состояния name_author
@admin_router.message(AddAuthor.name_author)
async def add_name_author2(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели не допустимые данные, введите текст имя автора")


@admin_router.message(AddAuthor.birthday, F.text)
async def add_birthday(message: types.Message, state: FSMContext):
    # if message.text == None:
    #     pass
    # else:
    try:
        time.strptime(message.text, "%Y-%m-%d")

    except ValueError:
        await message.answer('Введите корректное значение даты в виде "год-месяц-день"')
        return

    await state.update_data(birthday=message.text)
    # await message.answer("Загрузите изображение товара")
    # await state.set_state(AddAuthor.image)
    # print(tuple(state.get_data()))
    data = await state.get_data()
    # print(data)
    # print(tuple(data.values()))
    # Здесь вы можете использовать полученные данные для записи в базу данных
    # Например, если у вас есть объект для работы с базой данных `cur`, вы можете сделать что-то вроде:
    # cur = conn.cursor()

    # Работает
    cur = conn.cursor()
    # async with conn.cursor() as cur:
    cur.execute(
        "INSERT INTO authors(Code_author, name_author, Birthday) values(%s, %s, %s)",
        # (data["code_author"], data["name_author"], data["birthday"]),
        tuple(data.values()),
    )

    conn.commit()
    cur.close()
    # Не забудьте выполнить commit транзакции, если это необходимо
    await message.answer("Данные успешно сохранены в базе данных")
    # await state.finish()
    await state.clear()


@admin_router.message(AddAuthor.birthday)
async def add_birthday2(message: types.Message, state: FSMContext):
    await message.answer(
        'Вы ввели не допустимые данные, введите дату рождения в виде: "год-месяц-день"'
    )


ADD_FUNCTIONS = {
    # "Добавить автора": add_author,
    # "Добавить автора": add_all_author,
    # "Добавить книгу": add_book,
    # "Добавить доставку": add_delivery,
    # "Добавить издательство": add_publishing_house,
    # "Добавить Покупки": add_purchases,
}


for table in TABLES:

    @admin_router.message(F.text == table)
    async def select_data(message: types.Message):
        if message.text in values:
            await message.answer(f"ОК, вот данные с таблицы {message.text}")
            cur = conn.cursor()
            cur.execute(
                f"SELECT * from {values[message.text]}",
            )

            data = cur.fetchall()  # Fetch all rows from the query result
            # for row in data:
            #     await message.answer(
            #         str(row)
            #     )  # Convert row to string and send as a message

            await message.answer(str(data))
            cur.close()
        else:
            await message.answer("Таблица не найдена в списке значений.")


class AddBook(StatesGroup):
    code_book = State()
    title_book = State()
    code_author = State()
    pages = State()
    code_publish = State()
    # image = State()

    texts = {
        "AddBook:code_book": "Введите код заново:",
        "AddBook:title_book": "Введите имя заново:",
        "AddBook:code_author": "Введите код заново:",
        "AddBook:pages": "Введите колич. страниц заново:",
        "AddBook:code_publish": "Введите код заново:",
        # "AddAuthor:image": "Этот стейт последний, поэтому...",
    }


# Становимся в состояние ожидания ввода code_author
@admin_router.message(
    StateFilter(None), F.text == "Добавить книгу"
)  # "Добавить автора"
async def add_book(message: types.Message, state: FSMContext):

    await message.answer("Введите код книги", reply_markup=types.ReplyKeyboardRemove())

    await state.set_state(AddBook.code_book)


# Вернутся на шаг назад (на прошлое состояние)
@admin_router.message(StateFilter("*"), Command("назад"))
@admin_router.message(StateFilter("*"), F.text.casefold() == "назад")
async def back_step_handler_book(message: types.Message, state: FSMContext) -> None:

    current_state = await state.get_state()

    if current_state == AddBook.code_book:
        await message.answer(
            'Предыдущего шага нет, или введите код книги или напишите "отмена"'
        )
        return

    previous = None
    for step in AddBook.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(
                f"Ок, вы вернулись к прошлому шагу \n {AddBook.texts[previous.state]}"
            )
            return
        previous = step


# Ловим данные для состояние code_author и потом меняем состояние на name_author
@admin_router.message(AddBook.code_book, F.text)
async def add_code_book(message: types.Message, state: FSMContext):
    # Здесь можно сделать какую либо дополнительную проверку
    # и выйти из хендлера не меняя состояние с отправкой соответствующего сообщения
    # например:
    if message.text.isdigit():
        await state.update_data(code_book=message.text)
        await message.answer("Введите название книги")
        await state.set_state(AddBook.title_book)
    else:
        await message.answer("Код должен быть числом больше нуля. \n Введите заново")
        return


# Хендлер для отлова некорректных вводов для состояния code
@admin_router.message(AddBook.code_book, F.text)
async def add_code_book2(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели не допустимые данные, введите код")


@admin_router.message(AddBook.title_book, F.text)
async def add_title_book(message: types.Message, state: FSMContext):
    if len(message.text) >= 100:  # or (len(message.text) == message.text.count(" ")):
        await message.answer(
            "Название не должно превышать 100 символов и состоять из пробельных символов. \n Введите заново"
        )
        return

    await state.update_data(title_book=message.text)
    await message.answer("Введите код автора")
    await state.set_state(AddBook.code_author)


# Хендлер для отлова некорректных вводов для состояния name_author
@admin_router.message(AddBook.title_book, F.text)
async def add_title_book2(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели не допустимые данные, введите название")


@admin_router.message(AddBook.code_author, F.text)
async def add_code_author(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(code_author=message.text)
        await message.answer("Введите количества страниц")
        await state.set_state(AddBook.pages)
    else:
        await message.answer(
            "Код автора должен быть числом больше нуля. \n Введите заново"
        )
        return


@admin_router.message(AddBook.code_author, F.text)
async def add_code_author2(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели не допустимые данные, введите код")


@admin_router.message(AddBook.pages, F.text)
async def add_pages(message: types.Message, state: FSMContext):
    if message.text.isdigit() or (int(message.text) > 0):
        await state.update_data(pages=message.text)
        await message.answer("Введите код издательства")
        await state.set_state(AddBook.code_publish)
    else:
        await message.answer("Вы ввели некорректные данные страницы. \n Введите заново")
        return


@admin_router.message(AddBook.pages, F.text)
async def add_pages2(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели не допустимые данные, введите количество страниц")


@admin_router.message(AddBook.code_publish, F.text)
async def add_code_publish(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(code_publish=message.text)

    else:
        await message.answer(
            "Код издательства должен быть числом больше нуля. \n Введите заново"
        )
        return

    data = await state.get_data()
    # print(data)
    # print(tuple(data.values()))
    # Здесь вы можете использовать полученные данные для записи в базу данных
    # Например, если у вас есть объект для работы с базой данных `cur`, вы можете сделать что-то вроде:
    # cur = conn.cursor()

    # Работает
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO books(code_book, title_book, code_author, pages, code_publish) values(%s, %s, %s, %s, %s)",
        tuple(data.values()),
    )

    conn.commit()
    cur.close()
    # Не забудьте выполнить commit транзакции, если это необходимо
    await message.answer("Данные успешно сохранены в базе данных")
    # await state.finish()
    await state.clear()


@admin_router.message(AddBook.code_publish, F.text)
async def add_code_publish2(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели не допустимые данные, введите код")


class AddDelivery(StatesGroup):
    code_delivery = State()
    name_delivery = State()
    name_company = State()
    address = State()
    phone = State()
    inn = State()

    texts = {
        "AddDelivery:code_delivery": "Введите код доставки заново:",
        "AddDelivery:name_delivery": "Введите название доставки заново:",
        "AddDelivery:name_company": "Введите название компании заново:",
        "AddDelivery:address": "Введите адрес заново:",
        "AddDelivery:phone": "Введите телефон заново:",
        "AddDelivery:inn": "Введите ИНН заново:",
    }


@admin_router.message(StateFilter(None), F.text == "Добавить доставку")
async def add_delivery(message: types.Message, state: FSMContext):

    await message.answer(
        "Введите код доставки", reply_markup=types.ReplyKeyboardRemove()
    )

    await state.set_state(AddDelivery.code_delivery)


@admin_router.message(StateFilter("*"), Command("назад"))
@admin_router.message(StateFilter("*"), F.text.casefold() == "назад")
async def back_step_handler_delivery(message: types.Message, state: FSMContext) -> None:

    current_state = await state.get_state()

    if current_state == AddDelivery.code_delivery:
        await message.answer(
            'Предыдущего шага нет, или введите код доставки или напишите "отмена"'
        )
        return

    previous = None
    for step in AddDelivery.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(
                f"Ок, вы вернулись к прошлому шагу \n {AddDelivery.texts[previous.state]}"
            )
            return
        previous = step


@admin_router.message(AddDelivery.code_delivery, F.text)
async def add_code_delivery(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(code_delivery=message.text)
        await message.answer("Введите название доставки")
        await state.set_state(AddDelivery.name_delivery)
    else:
        await message.answer("Код должен быть числом больше нуля. \n Введите заново")
        return


@admin_router.message(AddDelivery.name_delivery, F.text)
async def add_name_delivery(message: types.Message, state: FSMContext):
    await state.update_data(name_delivery=message.text)
    await message.answer("Введите название компании")
    await state.set_state(AddDelivery.name_company)


@admin_router.message(AddDelivery.name_company, F.text)
async def add_name_company(message: types.Message, state: FSMContext):
    await state.update_data(name_company=message.text)
    await message.answer("Введите адрес")
    await state.set_state(AddDelivery.address)


@admin_router.message(AddDelivery.address, F.text)
async def add_address(message: types.Message, state: FSMContext):
    await state.update_data(address=message.text)
    await message.answer("Введите телефон")
    await state.set_state(AddDelivery.phone)


@admin_router.message(AddDelivery.phone, F.text)
async def add_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("Введите ИНН")
    await state.set_state(AddDelivery.inn)


@admin_router.message(AddDelivery.inn, F.text)
async def add_inn(message: types.Message, state: FSMContext):
    await state.update_data(inn=message.text)

    data = await state.get_data()

    cur = conn.cursor()
    cur.execute(
        "INSERT INTO deliveries(code_delivery, name_delivery, name_company, address, phone, inn) values(%s, %s, %s, %s, %s, %s)",
        tuple(data.values()),
    )

    conn.commit()
    cur.close()

    await message.answer("Данные успешно сохранены в базе данных")
    await state.clear()


class AddPurchase(StatesGroup):
    code_purchase = State()
    code_book = State()
    date_order = State()
    code_delivery = State()
    type_purchase = State()
    cost = State()
    amount = State()

    texts = {
        "AddPurchase:code_purchase": "Введите код Покупки заново:",
        "AddPurchase:code_book": "Введите код книги заново:",
        "AddPurchase:date_order": "Введите дату заказа заново:",
        "AddPurchase:code_delivery": "Введите код доставки заново:",
        "AddPurchase:type_purchase": "Введите тип Покупки заново:",
        "AddPurchase:cost": "Введите стоимость заново:",
        "AddPurchase:amount": "Введите количество заново:",
    }


@admin_router.message(StateFilter(None), F.text == "Добавить покупку")
async def add_purchase(message: types.Message, state: FSMContext):

    await message.answer(
        "Введите код Покупки", reply_markup=types.ReplyKeyboardRemove()
    )

    await state.set_state(AddPurchase.code_purchase)


@admin_router.message(StateFilter("*"), Command("назад"))
@admin_router.message(StateFilter("*"), F.text.casefold() == "назад")
async def back_step_handler_purchase(message: types.Message, state: FSMContext) -> None:

    current_state = await state.get_state()

    if current_state == AddPurchase.code_purchase:
        await message.answer(
            'Предыдущего шага нет, или введите код Покупки или напишите "отмена"'
        )
        return

    previous = None
    for step in AddPurchase.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(
                f"Ок, вы вернулись к прошлому шагу \n {AddPurchase.texts[previous.state]}"
            )
            return
        previous = step


@admin_router.message(AddPurchase.code_purchase, F.text)
async def add_code_purchase(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(code_purchase=message.text)
        await message.answer("Введите код книги")
        await state.set_state(AddPurchase.code_book)
    else:
        await message.answer("Код должен быть числом больше нуля. \n Введите заново")
        return


@admin_router.message(AddPurchase.code_book, F.text)
async def add_code_book(message: types.Message, state: FSMContext):
    await state.update_data(code_book=message.text)
    await message.answer("Введите дату заказа (гггг-мм-дд)")
    await state.set_state(AddPurchase.date_order)


@admin_router.message(AddPurchase.date_order, F.text)
async def add_date_order(message: types.Message, state: FSMContext):
    # Проверяем формат даты
    try:
        time.strptime(message.text, "%Y-%m-%d")
    except ValueError:
        await message.answer(
            "Некорректный формат даты. Пожалуйста, введите дату в формате 'гггг-мм-дд'"
        )
        return

    await state.update_data(date_order=message.text)
    await message.answer("Введите код доставки")
    await state.set_state(AddPurchase.code_delivery)


# Продолжайте добавление обработчиков для остальных состояний аналогичным образом...


@admin_router.message(AddPurchase.code_delivery, F.text)
async def add_code_delivery(message: types.Message, state: FSMContext):
    await state.update_data(code_delivery=message.text)
    await message.answer("Введите тип Покупки")
    await state.set_state(AddPurchase.type_purchase)


@admin_router.message(AddPurchase.type_purchase, F.text)
async def add_type_purchase(message: types.Message, state: FSMContext):
    if (message.text == "1") or (message.text == "0"):
        await state.update_data(type_purchase=message.text)
        await message.answer("Введите стоимость")
        await state.set_state(AddPurchase.cost)
    else:
        await message.answer("Тип должени быть 0 или 1. \n Введите заново")


@admin_router.message(AddPurchase.cost, F.text)
async def add_cost(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(cost=message.text)
        await message.answer("Введите количество")
        await state.set_state(AddPurchase.amount)
    else:
        await message.answer("Стоимость должна быть числом. \n Введите заново")


# Продолжайте добавление обработчиков для остальных состояний аналогичным образом...


@admin_router.message(AddPurchase.amount, F.text)
async def add_amount(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(amount=message.text)

        data = await state.get_data()

        cur = conn.cursor()
        cur.execute(
            "INSERT INTO purchases(code_purchase, code_book, date_order, code_delivery, type_purchase, cost, amount) values(%s, %s, %s, %s, %s, %s, %s)",
            tuple(data.values()),
        )

        conn.commit()

        await message.answer("Покупка добавлена успешно")

        cur.close()

        await state.clear()
    else:
        await message.answer("Количество должно быть числом. \n Введите заново")
        return


class AddPublishingHouse(StatesGroup):
    code_publish = State()
    publish = State()
    city = State()

    texts = {
        "code_publish": "код издательства",
        "publish": "издательство",
        "city": "город",
    }


@admin_router.message(StateFilter(None), F.text == "Добавить издательство")
async def add_publishing_house(message: types.Message, state: FSMContext):
    await message.answer(
        "Введите код издательства", reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(AddPublishingHouse.code_publish)


async def back_step_handler_publishing_house(
    message: types.Message, state: FSMContext
) -> None:
    current_state = await state.get_state()

    if current_state == AddPublishingHouse.code_publish:
        await message.answer(
            'Предыдущего шага нет, или введите код издательства или напишите "отмена"'
        )
        return

    previous = None
    for step in AddPublishingHouse.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(
                f"Ок, вы вернулись к прошлому шагу \n {AddPublishingHouse.texts[previous.state]}"
            )
            return
        previous = step


@admin_router.message(AddPublishingHouse.code_publish)
async def add_code_publish(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(code_publish=message.text)
        await message.answer("Введите название издательства")
        await state.set_state(AddPublishingHouse.publish)
    else:
        await message.answer("Код должен быть числом больше нуля. \n Введите заново")


@admin_router.message(AddPublishingHouse.publish)
async def add_publish(message: types.Message, state: FSMContext):
    await state.update_data(publish=message.text)
    await message.answer("Введите город")
    await state.set_state(AddPublishingHouse.city)


@admin_router.message(AddPublishingHouse.city)
async def add_city(message: types.Message, state: FSMContext):
    await state.update_data(city=message.text)

    data = await state.get_data()

    cur = conn.cursor()
    cur.execute(
        "INSERT INTO publishing_house(code_publish, publish, city) values(%s, %s, %s)",
        tuple(data.values()),
    )

    conn.commit()
    cur.close()

    await message.answer("Данные успешно сохранены в базе данных")
    await state.clear()
