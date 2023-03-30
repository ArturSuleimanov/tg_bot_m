import asyncio

from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from bot import MyBot
from config import *
from messages import *
from models.service import Service
from models.user import User
from models.question import Question


my_bot = MyBot()
dp = my_bot.get_dp() # bot dispatcher
bot = my_bot.get_bot() # getting bot
functions_keyboard = my_bot.generate_functions_keyboard() # generating main menu keyboard


@dp.message_handler(commands=['start']) # Replies to command /start
async def process_start_command(msg: types.Message):
    if msg.from_user.id == ADMIN_ID:    # checks if user is admin
        await msg.answer(admin_greetings)
    else:
        User.add_user(msg)  # adding new user
        current_state = dp.current_state(user=msg.from_user.id)
        data = await current_state.get_data()
        data["chosen_service"] = None
        await current_state.set_data(data)
        await bot.send_message( # sending main menu
            msg.from_user.id,
            main_menu_text,
            parse_mode="markdown",    # if we want font to be bold
            reply_markup=functions_keyboard
        )


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('function'))
async def choose_function_callback(callback_query: types.CallbackQuery):
    # handles main menu callbacks
    await my_bot.chosen_function_keyboard(callback_query)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('page'))
async def change_page_callback(callback_query: types.CallbackQuery):
    # changes either services page or questions page
    await my_bot.change_page(callback_query)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('support'))
async def ask_for_agreement(callback_query: types.CallbackQuery):
    # asks user for agreement after choosing services
    await my_bot.ask_for_user_agreement(callback_query)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('questions'))
async def send_answer(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    # sends answer for question user has chosen
    question_id = int(callback_query.data.split("_")[-1])  # getting question id to find it in db
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text=Question.get_question_answer_by_id(question_id)
    )


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('services'))
async def choose_service(callback_query: types.CallbackQuery):
    # applies for chosen service
    await my_bot.ask_for_user_agreement(callback_query)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('moreDetailedServices'))
async def choose_service_by_detailed_info(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await my_bot.ask_for_user_agreement(callback_query, True)



@dp.callback_query_handler(lambda c: c.data and 'agreement' in c.data)
async def agree_or_disagree(callback_query: types.CallbackQuery):
    # checks if user agree with this cost or not
    await bot.answer_callback_query(callback_query.id)  # lets client know bot has received this request, just need to get information ready
    if callback_query.data == "disagreement":
        await bot.send_message(
            callback_query.from_user.id,
            exit_to_menu[1:],
        )

    elif callback_query.data == "agreement":
        User.set_can_be_supporte(callback_query)
        await bot.send_message(
            callback_query.from_user.id,
            request_for_sharing_contacts,
            parse_mode="markdown",    # if we want font to be bold
        )
    



@dp.message_handler()
async def share_contact(msg: types.Message):
    # checks if user can be supported and sends user contacts to admin
    can_be_supported = User.can_be_supported(msg)
    if all(can_be_supported):
        current_state = dp.current_state(user=msg.from_user.id)
        data = await current_state.get_data()

        await bot.forward_message(ADMIN_ID,msg.from_user.id, msg.message_id)
        if "chosen_service" in data and data["chosen_service"] != None:
            await bot.send_message(
                ADMIN_ID,
                Service.get_by_id(data["chosen_service"]).title,
                parse_mode="markdown",    # if we want font to be bold
            )
        await bot.send_message(
        msg.from_user.id,
            contacts_successfully_sended,
            parse_mode="markdown",    # if we want font to be bold
        )
        data["chosen_service"] = None
        await current_state.set_data(data)
    elif can_be_supported[1]:
        await bot.send_message(
            msg.from_user.id,
            contacts_already_received,
            parse_mode="markdown",    # if we want font to be bold
        )
    else:
        await bot.send_message(
            msg.from_user.id,
            choose_before_message,
            parse_mode="markdown",    # if we want font to be bold
        )


async def noticifications_sender():
    # sending noticifications to every user in db every NOTICIFICATIONS_DELAY seconds
    while True:
        await asyncio.sleep(NOTICIFICATIONS_DELAY)
        user_ids_list = User.find_all()
        if user_ids_list:
            for id in user_ids_list:
                await bot.send_message(
                    id[0],
                    noticification_text,
                    parse_mode="markdown",  # if we want font to be bold
                )
        users_list = None


async def on_startup(dp):
    asyncio.create_task(noticifications_sender()) # if we want to run function but don't want to wait for it's execution


async def shutdown(dispatcher: Dispatcher):
    # shuts down dispatcher
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


if __name__ == '__main__':
    executor.start_polling(dp, on_shutdown=shutdown, on_startup=on_startup)    # runs our bot, on_startup means running this function when bot is started
