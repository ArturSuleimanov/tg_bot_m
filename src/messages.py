from config import SUPPORT_DELAY

currency = "руб"

exit_to_menu = "\n/start - чтобы вернуться в главное меню."

service_menu_text = "Выберите интересующую вас услугу или " +\
                    "свяжитесь с поддержкой."+ exit_to_menu

questions_menu_text = "Выберите интересующий вас вопрос " +\
                      "или свяжитесь с поддержкой."+ exit_to_menu

request_for_sharing_contacts = "*Пришлите свои контакты (почту, номер телефона или ник в телеграмме), " + \
                                "чтобы наш консультант мог связаться " + \
                                "c вами.*" + exit_to_menu

contacts_already_received = "Ваши контакты *уже получены*.\n" + \
                            "Вы можете воспользоваться данной услугой один раз " + \
                            "в *{0} минут*.".format(int(SUPPORT_DELAY/60)) + exit_to_menu

contacts_successfully_sended = "Ваши контакты успешно отправлены." + \
                               "Наш специалист свяжется с вами в " + \
                               "ближайшее время." + exit_to_menu

main_menu_text = "Здравствуйте, выберете что именно вас интересует.\
    \n*FAQ / Перечень услуг*"

noticification_text = "Напоминание!"

admin_greetings = "Привет, админ"

support_button_text = 'Узнать примерную стоимость и связаться с поддержкой'

contract_text = "{0}\n*Стоимость: *{1} {2}.\nИнтересна ли вам данная услуга?"

choose_before_message = "Сначала выберете, что вас интересует." + exit_to_menu

more_info_about_services_menu_text = "Здесь вы можете узнать подробную информацию " +\
    "о каждой услуге." + exit_to_menu