import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.strategy import FSMStrategy

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())  # автоматический поиск файла env

from handlers.user_private import user_private_router
from handlers.user_group import user_group_router
from handlers.admin_private import admin_router

from common.bot_cmds_list import private


ALLOWED_UPDATES = ["message, edited_message"]


bot = Bot(token=os.getenv("TOKEN"), parse_mode=ParseMode.HTML)
# bot.my_admins_list = []


# класс, который отвечает за фильтрацию
# сообщений
dp = Dispatcher(fsm_strategy=FSMStrategy.USER_IN_CHAT)


dp.include_router(user_private_router)
dp.include_router(user_group_router)
dp.include_router(admin_router)


async def main():
    await bot.delete_webhook(
        drop_pending_updates=True
    )  # чтобы бот не отвечал на всё сообщения, которые
    # были отправлены во время его отключки или в то время когда он не был в онлайне
    # await bot.delete_my_commands(scope=types.BotCommandScopeAllPrivateChats())

    await bot.set_my_commands(
        commands=private, scope=types.BotCommandScopeAllPrivateChats()
    )
    await dp.start_polling(
        bot, allowed_updates=ALLOWED_UPDATES
    )  # спрашиваем у телеграмма были ли какие-то сообщения


if __name__ == "__main__":
    asyncio.run(main())
