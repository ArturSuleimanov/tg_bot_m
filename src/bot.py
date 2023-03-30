from config import *
from aiogram import Bot
from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from messages import *
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from models.question import Question
from models.service import Service


class MyBot:

    __TOKEN = TOKEN
    __bot = Bot(token=__TOKEN)
    __dp = Dispatcher(__bot, storage=MemoryStorage())


    def __init__(self):
        self.__services_list = Service.get_services_list()
        self.__dp.middleware.setup(LoggingMiddleware())    # need this to add some data to user


    __functions_list = [
        '❓ FAQ',
        'Перечень услуг',
    ]   # main menu functions list


    __functions_callbacks_list = [
        'function_questions',
        'function_services',
    ]   # main menu functions callback list


    __faq_callback = 'function_questions'   # main menu function callback
    __services_list_callback = 'function_services'   # main menu function callback
    __moreDetailedServices_callback = "function_moreDetailedServices"


    def get__moreDetailedServices_callback(self):
        return self.__moreDetailedServices_callback

    def get_dp(self):
        # getter for dispatcher
        return self.__dp


    def add_ask_for_support_button(self, inline_keyboard: InlineKeyboardMarkup):
        ask_for_support_button = InlineKeyboardButton(
                text="Связаться с поддержкой",
                callback_data='agreement'
            ) #button description
        inline_keyboard.add(ask_for_support_button)


    def generate_functions_keyboard(self):
        # generating main menu keyboard
        inline_keyboard = InlineKeyboardMarkup(row_width=2)

        for i in range(len(self.__functions_list)):
            inline_button = InlineKeyboardButton(
                text=self.__functions_list[i],
                callback_data=self.__functions_callbacks_list[i]
            ) #button description
            inline_keyboard.add(inline_button)
        self.add_ask_for_support_button(inline_keyboard)
        return inline_keyboard


    def generate_keyboard(self, page: int, key: str):
        # generating keyboard for every function
        """

        :param page: current page
        :param key: name of function
        :return:
        """
        current_items_list = []
        if key == "questions":
            current_items_list = Question.get_questions_list()


        elif key == "services" or key=="moreDetailedServices":
            current_items_list = [service for service in self.__services_list]

        current_callbacks_list = [key + "_" + str(item.id) \
                                  for item in current_items_list]   # questions callbacks

        inline_keyboard = InlineKeyboardMarkup(row_width=2)
        # generating key_board
        last_item = page + KEYBOARD_BUTTONS_PER_PAGE \
            if page + KEYBOARD_BUTTONS_PER_PAGE <= len(current_items_list)\
                else len(current_items_list)

        for i in range(page, last_item):
            inline_button = InlineKeyboardButton(
                                text=current_items_list[i].title,
                                callback_data=current_callbacks_list[i]
                            ) #button description
            inline_keyboard.add(inline_button)

        self.generate_navigation(last_item,     #generating navbar
                                 inline_keyboard,
                                 current_items_list,
                                 key,
                                 page)

        if key == "services":   # adding support button
            more_information_about_service_button =  InlineKeyboardButton(
                                text="Подробнее об услугах",
                                callback_data=self.__moreDetailedServices_callback
                            ) #button description
            inline_keyboard.add(more_information_about_service_button)
        self.add_ask_for_support_button(inline_keyboard)
        return inline_keyboard


    def generate_navigation(self,
                            last_item: int,
                            inline_keyboard: InlineKeyboardMarkup,
                            current_items_list: list,
                            key: str,
                            page: int):
        #   generating navbar
        """

        :param last_item:   gives us position of last item
        :param inline_keyboard: our keyboard
        :param current_items_list: list of our items
        :param key: name of function
        :param page: page number
        :return: None
        """
        prev_page = InlineKeyboardButton('<', callback_data='page_' + key + '_prev')
        next_page = InlineKeyboardButton('>', callback_data='page_' + key + '_next')

        if page == 0 and KEYBOARD_BUTTONS_PER_PAGE < len(current_items_list):
            inline_keyboard.row(next_page)

        elif last_item == len(current_items_list) and \
                KEYBOARD_BUTTONS_PER_PAGE < len(current_items_list):
            inline_keyboard.row(prev_page)

        elif KEYBOARD_BUTTONS_PER_PAGE < len(current_items_list):
            inline_keyboard.row(prev_page, next_page)





    async def chosen_function_keyboard(self, callback_query: types.CallbackQuery):
        state = self.__dp.current_state(user=callback_query.from_user.id)  # need this to safe some data in user
        page = 0  # to start from very begining of our list
        code = callback_query.data  # getting callback code
        key = code.split("_")[-1]  # we want to know current function to generate menu
        await self.__bot.answer_callback_query(
            callback_query.id)  # lets client know bot has received this request, just need to get information ready
        keyboard = self.generate_keyboard(page, key)  # generating keyboard with our params
        if code == self.get_services_list_callback():   # which text do we want to send user depends on callback code
            current_text = service_menu_text
        elif code == self.get_faq_callback():
            current_text = questions_menu_text
        else:
            current_text = more_info_about_services_menu_text

        await self.__bot.send_message(
            callback_query.from_user.id,
            current_text,
            reply_markup=keyboard
        )  # sending message to user

        current_data = await state.get_data()
        current_data["page_" + key] = 0
        await state.set_data(current_data)  # setting some additional data to our user




    async def change_page(self, callback_query: types.CallbackQuery):
        # changes page in current message and saves current state for this user
        await self.__bot.answer_callback_query(callback_query.id)
        action = callback_query.data.split("_")[-1]
        key = callback_query.data.split("_")[1]
        current_state = self.__dp.current_state(user=callback_query.from_user.id)   # getting user's state
        data = await current_state.get_data()   # getting current data from user's state
        if "page_" + key in data:   # checking if such key in data
            current_page = data["page_" + key]
        else:
            current_page = 0

        if action == "next":
            current_page += KEYBOARD_BUTTONS_PER_PAGE

        elif action == "prev":
            current_page -= KEYBOARD_BUTTONS_PER_PAGE

        data["page_" + key] = current_page
        await current_state.set_data(data)  # sets new data for current user state



        keyboard = self.generate_keyboard(current_page, key)

        await self.__bot.edit_message_text(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            reply_markup=keyboard,
            text=callback_query.message.text
        )


    async def ask_for_user_agreement(self,
                                     callback_query: types.CallbackQuery,
                                     is_full_info: bool = False):
        # asks user for agreement and generates message to ask
        await self.__bot.answer_callback_query(callback_query.id)
        current_service_id = int(callback_query.data.split("_")[-1])
        current_state = self.__dp.current_state(user=callback_query.from_user.id)
        data = await current_state.get_data()
        data["chosen_service"] = current_service_id
        await current_state.set_data(data)
        current_service = Service.get_by_id(current_service_id)
        if not is_full_info:
            agreement = InlineKeyboardButton('Да', callback_data='agreement')
            disagreement = InlineKeyboardButton('Нет', callback_data='disagreement')
            inline_keyboard = InlineKeyboardMarkup(row_width=2).add(agreement,
                                                                    disagreement)

        else:
            agreement = InlineKeyboardButton('Меня заинтересовала эта услуга',
                                             callback_data='agreement')
            inline_keyboard = InlineKeyboardMarkup(row_width=2).add(agreement)

        text = contract_text.format(current_service.more_detailed_description if \
                                        is_full_info else current_service.short_description,
                                    current_service.price,
                                    currency)

        await self.__bot.edit_message_text(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            text=text,
            reply_markup=inline_keyboard,
            parse_mode="markdown",    # if we want font to be bold
        )



    # async def user_has_chosen_service(self, callback_query: types.CallbackQuery):
    #     # if user has chosen service, adds this service id to user state data to exclude it from keyboard and generates new keyboard
    #     current_state = self.__dp.current_state(user=callback_query.from_user.id)
    #     data = await current_state.get_data()
    #     service_id = int(callback_query.data.split()[-1])
    #
    #     await current_state.set_data(data)
    #     if "page_services" in data:
    #         current_page = data["page_services"]
    #     else:
    #         current_page = 0
    #
    #     keyboard = self.generate_keyboard(current_page, "services")
    #
    #     await self.__bot.edit_message_text(
    #         chat_id=callback_query.message.chat.id,
    #         message_id=callback_query.message.message_id,
    #         reply_markup=keyboard,
    #         text=callback_query.message.text
    #     )


    def get_faq_callback(self):
        # getter for __faq_callback
        return self.__faq_callback

    
    def get_services_list_callback(self):
        # getter for __services_list_callback
        return self.__services_list_callback


    def get__functions_list(self):
        # getter for __functions_list
        return self.__functions_list


    def get__functions_callbacks_list(self):
        # getter for __functions_callbacks_list
        return self.__functions_callbacks_list


    def get_bot(self):
        # getter for __bot
        return self.__bot
