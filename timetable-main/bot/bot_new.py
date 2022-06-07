import json
import yaml
import logging
import requests
import telebot
from telebot import types

# API_TOKEN = open('api_token.txt').read()
API_TOKEN = '5387469239:AAGcPJTX8FmFnaLnZ_YisGBdjfoYEL6Mo5o'

bot = telebot.TeleBot(API_TOKEN)
global_position = 0


BACK_BTN = 'В начало'

GROUPS = {
    'RTF': {
        '1': ['111', '111-М1', '121-1', '121-2', '121-3', '141-1', '141-2', '141-3', '141-4', '141-М2', '141-М3', '141-М4', '141-М5', '151', '151-М', '161', '161-М', '181-М', '1А1', '1А1-М', '1В1', '1В1-М'],
        '2': ['110', '120-1', '120-2', '140-1', '140-2', '140-3', '140-4', '150', '160', '1А0', '1В0'],
        '3': ['119', '129', '149-1', '149-2', '149-3', '149-4', '159', '169', '1А9', '1В9'],
        '4': ['118', '128', '148-1', '148-2', '148-3', '148-4', '158', '168', '1А8', '1В9'],
        '5': ['127-1']
    },
    'RKF': {
        '1': ['201-1', '201-2', '211', '221-1', '221-2', '231-1', '231-2', '231-3', '231-4', '231-5', '231-6', '261-М1', '261-М2', '271-М1', '271-М2'],
        '2': ['200', '210', '220', '230-1', '230-2', '230-3', '230-4'],
        '3': ['209', '219-1', '219-2', '229-1', '239-1', '239-2', '239-3'],
        '4': ['208', '218-1', '218-2', '228-1', '238-1', '238-2', '238-3'],
        '5': []
    },
    'FSU': {
        '1': ['401-1', '401-M', '421-1', '421-2', '421-3', '421-4', '421-M1', '431-1', '431-2', '431-3', '431-M1', '431-М2', '441-1', '441-2', '471-1', '471-М'],
        '2': ['400-1', '420-1', '420-2', '420-3', '420-4', '430-1', '430-2', '430-3', '430-4', '440-1', '440-2', '470-1'],
        '3': ['409-1', '429-1', '429-2', '429-3', '439-1', '439-2', '439-3', '439-4', '439-5', '449-1', '449-2', '479-1'],
        '4': ['408', '428-1', '428-2', '428-3', '438-1', '438-2', '438-3', '448-1', '478-1'],
        '5': []
    },
    'FVS': {
        '1': ['511-1','511-M','521','531','541-1','541-M','551-M','571-1','571-2', '581', '581-M', '591-1'],
        '2': ['510-1', '520', '530-1', '540', '580-1', '580-2', '580-3', '590-1'],
        '3': ['519-1', '519-2', '529', '539-1', '549', '589-1', '589-2', '589-3', '599-1'],
        '4': ['518-1', '518-2', '528', '538', '548-1', '588-1', '588-2', '588-3', '598-1', '598-2'],
        '5': []
    },
    'FET': {
        '1': ['311-1', '311-2', '311-M', '321-1', '321-2', '341', '341-M', '351-1', '351-M', '361-1', '361-2', '361-3', '361-M1', '361-M2'],
        '2': ['310', '320-1', '320-2', '340', '350', '360-1', '360-2', '360-4'],
        '3': ['319', '329-1', '349', '359', '369-1', '369-2'],
        '4': ['318', '328-1', '348-1', '358', '368-1', '368-2'],
        '5': []
    },
    'FIT': {
        '1': ['011', '011-M', '021-1', '031-M', '051', '051-М', 'ИП021-1', 'ИП021-2', 'ИП021-3', 'ИП021-4', 'ИП021-5', 'ИП021-6'],
        '2': ['010', '050'],
        '3': ['019', '059'],
        '4': ['018'],
        '5': []
    },
    'EF': {
        '1': ['861-1', '861-M', '871-1', '871-M1', '881-1', '881-2', '881-M'],
        '2': ['860', '870-1', '870-2', '880-1', '880-2', '880-3'],
        '3': ['869', '879-1', '889-1', '889-2'],
        '4': ['868', '878-1', '878-2', '888-1', '888-2'],
        '5': []
    },
    'GF': {
        '1': ['611', '621', '631-1', '631-2'],
        '2': ['610-1', '620-1'],
        '3': ['619', '629'],
        '4': ['618', '628'],
        '5': []
    },
    'YUF': {
        '1': ['091-1', '091-2', '091-3', '091-4'],
        '2': ['090-1', '090-2'],
        '3': ['099-1', '099-2'],
        '4': ['098-1', '098-2'],
        '5': []
    },
    'FB': {
        '1': ['711-1', '711-2', '721-1', '721-2', '731-1', '731-2', '741-1', '761-1'],
        '2': ['710-1', '710-2', '720-1', '720-2', '730-1', '730-2', '740-1', '760-1'],
        '3': ['719-1', '719-2', '729-1', '739-1', '749-1', '769-1', '769-2'],
        '4': ['718-1', '728-1', '728-2', '738-1', '748', '768-1', '768-2'],
        '5': ['737-1', '747']
    }
}


class UserType:
    STUDENT = 'Студент'
    TEACHER = 'Преподаватель'


class GlobalPositionType:
    PROCESS_USER_TYPE = 0
    PROCESS_STUDENT_FACULTY = 1
    PROCESS_STUDENT_COURSE = 2
    PROCESS_STUDENT_GROUP = 3
    PROCESS_STUDENT_WEEK_NUM = 4
    PROCESS_STUDENT_DAY_NUM = 5
    SEND_REQUEST = 6


class State:
    def __init__(self):
        self.url = 'http://localhost:8080/get_timetable'
        self.headers = {'Content-Type': 'application/json'}
        self.faculty_tag = None
        self.group_name = None
        self.week_num = None
        self.day_num = None
        self.course_num = None

    def clear(self):
        self.faculty_tag = None
        self.group_name = None
        self.week_num = None
        self.day_num = None
        self.course_num = None

    def send_request(self):
        if all([self.faculty_tag, self.group_name, self.week_num, self.day_num]):
            data = {
                'faculty_tag': self.faculty_tag.lower(),
                'group_name': self.group_name,
                'week_num': self.week_num,
                'day_num': int(self.day_num)
            }
            print('data', data)
            response = requests.post(self.url, json=data, headers=self.headers)
            return response.json()


@bot.message_handler(commands=['start'])
def start(msg):
    global global_position, state
    global_position = GlobalPositionType.PROCESS_USER_TYPE
    state.clear()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        types.KeyboardButton(UserType.STUDENT),
        types.KeyboardButton(UserType.TEACHER)
    )
    bot.send_message(msg.chat.id, f'Привет, {msg.from_user.first_name}. Кто ты?', reply_markup=markup)
    print(msg)


@bot.message_handler(content_types=['text'])
def text_handler(msg):
    print(msg.text)
    global global_position, state

    if msg.text == BACK_BTN:
        start(msg)

    if global_position == GlobalPositionType.PROCESS_USER_TYPE:
        if msg.text == UserType.TEACHER:
            bot.send_message(chat_id=msg.chat.id, text="Расписание доступно только для студентов")
        elif msg.text == UserType.STUDENT:
            global_position += 1
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard = []
            for faculty in GROUPS.keys():
                keyboard.append(types.KeyboardButton(faculty))
            markup.add(*keyboard, types.KeyboardButton(BACK_BTN))
            bot.send_message(chat_id=msg.chat.id, text="Выберите факультет", reply_markup=markup)
    elif global_position == GlobalPositionType.PROCESS_STUDENT_FACULTY:
        if msg.text not in GROUPS.keys():
            bot.send_message(chat_id=msg.chat.id, text="Факультет не опознан")
        else:
            state.faculty_tag = msg.text
            global_position += 1
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard = []
            for course in GROUPS[msg.text].keys():
                keyboard.append(types.KeyboardButton(course))
            markup.add(*keyboard, types.KeyboardButton(BACK_BTN))
            bot.send_message(chat_id=msg.chat.id, text="Выберите свой курс", reply_markup=markup)
    elif global_position == GlobalPositionType.PROCESS_STUDENT_COURSE:
        if msg.text not in GROUPS[state.faculty_tag].keys():
            bot.send_message(chat_id=msg.chat.id, text="Курс не найден")
        else:
            state.course_num = msg.text
            global_position += 1
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard = []
            for group in GROUPS[state.faculty_tag][msg.text]:
                keyboard.append(types.KeyboardButton(group))
            markup.add(*keyboard, types.KeyboardButton(BACK_BTN))
            bot.send_message(chat_id=msg.chat.id, text="Выберите свою группу", reply_markup=markup)
    elif global_position == GlobalPositionType.PROCESS_STUDENT_GROUP:
        if msg.text not in GROUPS[state.faculty_tag][state.course_num]:
            bot.send_message(chat_id=msg.chat.id, text="Группа не найдена")
        else:
            state.group_name = msg.text
            global_position += 1
            bot.send_message(chat_id=msg.chat.id,
                             text="Введите номер учебной недели",
                             reply_markup=types.ReplyKeyboardRemove())
    elif global_position == GlobalPositionType.PROCESS_STUDENT_WEEK_NUM:
        try:
            state.week_num = int(msg.text)
            global_position += 1
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard = []
            for i in ['1', '2', '3', '4', '5', '6']:
                keyboard.append(types.KeyboardButton(i))
            markup.add(*keyboard, types.KeyboardButton(BACK_BTN))
            bot.send_message(chat_id=msg.chat.id,
                             text="Введите номер дня недели (Пн-1, Вт-2, Ср-3, Чт-4, Пт-5, Сб-6)",
                             reply_markup=markup)
        except Exception:
            bot.send_message(chat_id=msg.chat.id,
                             text="Номер недели должен быть целым числом",
                             reply_markup=types.ReplyKeyboardRemove())
    elif global_position == GlobalPositionType.PROCESS_STUDENT_DAY_NUM:
        if msg.text not in ['1', '2', '3', '4', '5', '6']:
            bot.send_message(chat_id=msg.chat.id, text="Неверный номер дня недели")
        else:
            state.day_num = msg.text
            global_position += 1
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(types.KeyboardButton('Получить'), types.KeyboardButton(BACK_BTN))
            bot.send_message(chat_id=msg.chat.id, text='Все верно? Получить расписание?', reply_markup=markup)
    elif global_position == GlobalPositionType.SEND_REQUEST:
        try:
            response = state.send_request()
            # text = json.dumps(response, indent=4, ensure_ascii=False)
            text = yaml.safe_dump(response, allow_unicode=True)
        except Exception:
            text = "По заданным параметрам расписание недоступно"
        bot.send_message(chat_id=msg.chat.id, text=text)


if __name__ == '__main__':
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    state = State()
    logging.info('[+] Start bot polling')
    bot.polling(none_stop=True)


