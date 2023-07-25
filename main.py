from generate import generation
# Импортируем библиотеки
import telebot
from telebot import types

bot = telebot.TeleBot('6336968258:AAEPAgGOR5lGHqFp9yeW68CpiSVzdlL9PWI')

# Создание базовых кнопок
button_generate = types.KeyboardButton("Новая генерация")
button_settings = types.KeyboardButton("Выбор модели")
button_continue = types.KeyboardButton("Продолжить")
button_menu = types.KeyboardButton("Выход в меню")
button_generate_again = types.KeyboardButton("Сгенерировать заново")
button_back = types.KeyboardButton("Назад")

# Создание кнопок настроек
model_button_a = types.KeyboardButton("RUGPT2 XL")
model_button_b = types.KeyboardButton("RUGPT3 SMALL")
model_button_c = types.KeyboardButton("RUGPT3 MEDIUM")
model_button_d = types.KeyboardButton("RUGPT3 LARGE")

# Создание переменных под настройки
model = "sberbank-ai/rugpt3large_based_on_gpt2"
text_after_generation = "Продолженный текст"
text_for_generation = "Начальный"
length = 100

# Создание шаблонов клавиатур
keyboard_model = types.ReplyKeyboardMarkup(row_width=1)
keyboard_model.add(model_button_a, model_button_b, model_button_c, model_button_d, button_back)

keyboard_main = types.ReplyKeyboardMarkup(row_width=1)
keyboard_main.add(button_settings, button_generate)

keyboard_vibor = types.ReplyKeyboardMarkup(row_width=1)
keyboard_vibor.add(button_menu, button_continue, button_generate, button_generate_again)

# Нужные флажки
generation_flag = False

@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(message.chat.id, 'RuGPT активирован', reply_markup=keyboard_main)
    bot.register_next_step_handler(message, choice_handler)

@bot.message_handler(commands=['choice'])
def choice_handler(message):
    global generation_flag
    if message.text == button_generate.text:
        bot.send_message(message.chat.id, "Введите текст для дополнения", reply_markup=types.ReplyKeyboardRemove())
        generation_flag = True
    elif message.text == button_settings.text:
        bot.send_message(message.chat.id, "Выберите модель", reply_markup=keyboard_model)
        bot.register_next_step_handler(message, model_settings)

@bot.message_handler(commands= ["model_settings"])
def model_settings(message):
    global model, model_button_a, model_button_b, model_button_c, model_button_d
    if message.text == model_button_a.text:
        model = "sberbank-ai/rugpt2large"
    elif message.text == model_button_b.text:
        model = "sberbank-ai/rugpt3small_based_on_gpt2"
    elif message.text == model_button_c.text:
        model = "sberbank-ai/rugpt3medium_based_on_gpt2"
    elif message.text == model_button_d:
        model = "sberbank-ai/rugpt3large_based_on_gpt2"
    else:
        pass
    bot.register_next_step_handler(message, choice_handler)
    bot.send_message(message.chat.id, 'Возврат в главное меню', reply_markup=keyboard_main)

@bot.message_handler(commands= ['vibor'])
def vibor(message):
    global original_text, past_generation, generation_flag
    if message.text == button_menu.text:
        bot.send_message(message.chat.id, "Переход в настройки", reply_markup=keyboard_main)
        generation_flag = False
        bot.register_next_step_handler(message, choice_handler)
    elif message.text == button_generate.text:
        bot.send_message(message.chat.id, "Введите новый текст для генерации", reply_markup=types.ReplyKeyboardRemove())
    elif message.text == button_continue.text:
        past_generation = past_generation[-200:]
        new_length = len(past_generation) + length
        generated_text = generation(past_generation, model, new_length)
        generated_text = generated_text[len(past_generation):]
        past_generation = generated_text
        bot.send_message(message.chat.id, f"Продолженный текст:\n{generated_text}",
                         reply_markup=keyboard_vibor)
        bot.register_next_step_handler(message, vibor)
    else:
        new_length = len(original_text) + length
        generated_text = generation(original_text, model, new_length)
        past_generation = generated_text
        bot.send_message(message.chat.id, f"Перегенерированный текст:\n{generated_text}",
                         reply_markup=keyboard_vibor)
        bot.register_next_step_handler(message, vibor)

@bot.message_handler(func= lambda message: True)
def messages_handler(message):
    global generation_flag, length, model, past_generation, original_text
    if generation_flag:
        original_text = message.text
        new_length = len(original_text) + length
        generated_text = generation(original_text, model, new_length)
        past_generation = generated_text
        bot.send_message(message.chat.id, f"Вот продолженный текст:\n{generated_text}",
                         reply_markup=keyboard_vibor)
        bot.register_next_step_handler(message, vibor)
    else:
        bot.send_message(message.chat.id, "Что-то пошло не так, возврат в меню", reply_markup=keyboard_main)
        generation_flag = False
        bot.register_next_step_handler(message, choice_handler)

bot.polling(non_stop=True)

