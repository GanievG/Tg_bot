from aiogram.types import BotCommand


# В закладке меню будут выведены списки команд

private = [
    BotCommand(command='start', description='Запуск бота'),
    BotCommand(command='menu', description='Посмотреть меню'),
    BotCommand(command='about', description='О нас'),
    BotCommand(command='payment', description='Варианты оплаты'),
    BotCommand(command='shipping', description='Варианты доставки'),
]