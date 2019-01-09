from time import time
from functools import wraps
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth.models import BaseUserManager
from django.conf import settings as djangoSettings
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
import re
import telegram
from telegram import ForceReply
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram import Location
from telegram.ext import Updater
from telegram.ext import JobQueue
from telegram.ext import MessageHandler
from telegram.ext import CommandHandler
from telegram.ext import CallbackQueryHandler
from telegram.ext import ConversationHandler
from telegram.ext import Filters
from django_telegrambot.apps import DjangoTelegramBot

import logging
from .models import Abonent
from .models import Car
from .models import Customer
from .models import Driver
from .models import Mediator
from .models import Product
from .models import Race
from .models import Units
from .models import Shipment
from .models import Supplier
from .models import Trailer
from .models import Constants
from .models import LoadingPlace
from .models import Log

RACE_DATE_RANGE = 3 # Диапазон дней от текущей даты, за которые рейсы считаются предстоящими

# Bot status list
STATES = 'start', 'auth', 'pass', 'ready', 'accepted', 'loading', 'loaded', 'race', 'unloading', 'unloaded', 'ban'
START, AUTH, PASS, READY, ACCEPTED, LOADING, LOADED, RACE, UNLOADING, UNLOADED, BAN = STATES

STATE = (
    (START, 'Начало'),
    (AUTH, 'Аутентификация'),
    (PASS, 'Запрос ключа'),
    (READY, 'Готов'),
#    (RACE, 'Рейс'),
    (ACCEPTED, 'Принято'),
    (LOADING, 'Погрузка'),
    (LOADED, 'Загружен'),
    (UNLOADING, 'Разгрузка'),
    (UNLOADED, 'Разгружен'),
    (BAN, 'Заблокирован'),
)

main_keyboard = [['Мои рейсы', 'Статистика']]
race_keyboard = [[InlineKeyboardButton('Откуда', callback_data=r'/from'),
                  InlineKeyboardButton('Куда', callback_data=r'/to')]]
race_accept_keyboard = [[InlineKeyboardButton('Приступить', callback_data=r'/accepted')]]
loading_keyboard = [[InlineKeyboardButton('Погрузка', callback_data=r'/loading')]]
unload_keyboard = [[InlineKeyboardButton('Выгрузка', callback_data=r'/unloading')]]
confirm_keyboard = [[InlineKeyboardButton('Да', callback_data=r'/yes'), InlineKeyboardButton('Нет', callback_data=r'/no')]]
close_kb = [[InlineKeyboardButton('Закрыть', callback_data=r'/close')]]

keyboards = {READY: race_accept_keyboard, ACCEPTED: loading_keyboard, RACE: unload_keyboard}

# AvtrgnBot Телеграм-бот для коммуникации диспетчерской системы с водителями
# TO DO: Вынести строковые сообщения в константы

def expire(seconds=15):
    return time()+seconds


def callback_decorator(method):
    @wraps(method)
    def wrapper(self, bot, update):
#        if update.callback_query.answer():
            return method(self, bot, update)
    return wrapper


def reply_callback_decorator(method):
    @wraps(method)
    def wrapper(self, bot, update):
        result = method(self, bot, update)
        if result is not None:
            if result.get('send') is not None and result['send']:
                if update.callback_query:
                    if result.get('reply_markup') is not None:
                        logger.info('Reply markup = {}'.format(result['reply_markup']))
                        if type(result['reply_markup']) is ForceReply or \
                           type(result['reply_markup']) is ReplyKeyboardMarkup:
                            #update.callback_query.edit_message_reply_markup(reply_markup=ForceReply(result['reply_markup']))
                            if result['delete']:
                                update.callback_query.message.delete()
                            bot.sendMessage(update.callback_query.message.chat_id, result['send'],
                                            parse_mode='HTML', reply_markup=result['reply_markup'])
                        else:
                            if result['delete']:
                                update.callback_query.message.edit_text(result['send'], parse_mode='HTML')
                                update.callback_query.message.edit_reply_markup(reply_markup=result['reply_markup'])
                            else:
                                bot.sendMessage(update.callback_query.message.chat_id, result['send'],
                                                parse_mode='HTML', reply_markup=result['reply_markup'])
                else:
                    if result.get('reply_markup') is not None:
                        update.message.reply_html(result['send'], reply_markup=result['reply_markup'])    
                    else:
                        update.message.reply_html(result['send'])                        

            if result.get('call') is not None:
                return result['call'](bot, update)

    return wrapper


def confirm_callback_decorator(method):
    @wraps(method)
    def wrapper(self, bot, update):
        data = update.callback_query.data.split(':')[1]
        if int(data) > 0:
            return method(self, bot, update)
    return wrapper


def modal_input_decorator(regex=r'^\d+$', confirm_text='confirm', error_text='error'):
    def decorator(method):
        @wraps(method)
        def decorated(*args, **kwargs):
            self = args[0]
            bot = args[1]
            update = args[2]
            upd = update
            if update.callback_query is not None:
                upd = update.callback_query

            keyboard = method(*args, **kwargs)
            keyboard[0][0].callback_data = kwargs['callback_command'] + ':' + update.message.text.strip()
            logger.info('Modal callback data = {}'.format(keyboard[0][0].callback_data))
            
            if re.search(regex, upd.message.text.strip(), flags=re.IGNORECASE) is not None:
                bot.sendMessage(upd.message.chat_id, confirm_text.format(upd.message.text.strip()),
                                     parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
            else:
                bot.sendMessage(upd.message.chat_id, error_text,
                                     parse_mode='HTML', reply_markup=ForceReply(force_reply=True))

        return decorated
    return decorator

def log_decorator(method):
    @wraps(method)
    def wrapper(self, bot, update, *args, **kwargs):
        cdata = None
        upd = update
        if update.callback_query is not None:
            upd = update.callback_query
            cdata = update.callback_query.data
            
        abonents = Abonent.objects.filter(pk=upd.message.chat_id)
        for a in abonents:
            log = Log(abonent=a, driver=a.driver, method=method.__name__, state=a.state, car=a.car, race=a.race_id, cdata=cdata, message=str(upd.message.text))
            log.save()
        return method(self, bot, update, *args, **kwargs)
    return wrapper
    
    
class AvtrgnBot():
    #updater = TELEGRAM
    #bot = updater.bot
    #disp = updater.dispatcher
    #job_queue = updater.job_queue
    #me = bot.getMe()
    #states = dict(STATE)
    number_mask = r'^[ABCEHKMOPTYXАВСЕНКМОРТУХ]\s*\d{3}\s*[ABCEHKMOPTYXАВСЕНКМОРТУХ]{2}\s*(\d{2})?$'
    number_sub_mask = r'^([ABCEHKMOPTYXАВСЕНКМОРТУХ])\s*(\d{3})\s*([ABCEHKMOPTYXАВСЕНКМОРТУХ]{2})\s*(\d{2})?$'
    messages = {
        'hello' : u'Автоматический бот-диспетчер ООО "Авторегион" приветствует Вас. Для дальнейшей работы Вам нужно авторизоваться.',
        'auth' : u'Для регистрации в системе пришлите госномер автомобиля в формате x123xy.',
        'pass'  : u'Теперь пришлите секретный ключ для подтверждения полномочий. Если он вам неизвестен, обратитесь к диспетчеру.',
        'errauth' : u'Неверный номер автомобиля. Пробуйте ещё.',
        'errpass' : u'Неверный секретный ключ. Попробуйте ещё.',
        'authok' : u'Вы авторизованы.\n-----\nИспользуйте кнопки с командами внизу для получения информации о рейсах.',
        'tryout' : u'Количество попыток авторизации исчерано.',
        'banned' : u'Вам отказано в доступе.',
        'select' : u'Выберите команду',
    }

    # Обработка начального статуса
    @log_decorator
    def start(self, abon, update):
        update.message.reply_text(self.messages['hello'])
        if START in abon.state:
            abon.state = AUTH
            abon.save()
            update.message.reply_text(self.messages['auth'], reply_markup=ForceReply(force_reply=True))


    # Процедура отправки типового сообщения
    def send(self, uid, m = 'hello', **kwargs):
        bot = DjangoTelegramBot.getBot()
        bot.sendMessage(uid, self.messages[m], reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True))

    # Процедура движения по статусам авторизации
    def move_auth(self, abonent, msg='auth', next_state=AUTH, try_increment=1, reset_auth_car=True):
        self.send(str(abonent.telegram_id), msg)    # Отправляем сообщение
        abonent.state = next_state                  # Присваиваем следующий статус
        abonent.auth_try += try_increment
        abonent.last_seen = timezone.now()
        if reset_auth_car:
            abonent.context = None          # Сбрасываем контекст
        abonent.save()


    # Обработка запроса авторизации        --- Подумать над вопросом использования имени в телеграм в качестве номера авто при авторизации
    @log_decorator
    def auth(self, abon, update):
        auth_fail = True
        if abon.car is not None:
            return 1
        # Проверить доступное количество попыток авторизации и при исчерпании этого лимита отправить клиента восвояси
        if abon.auth_try < 3 and BAN not in abon.state and abon.active:
            number = re.sub(self.number_sub_mask, r'\1 \2 \3 \4', update.message.text.strip().upper())
            if re.search(self.number_mask, number, flags=re.IGNORECASE) is not None:
                # Далее нужно проверить наличие автомобиля в базе данных
                try:
                    c = Car.objects.get(number__istartswith=number)
                except Car.DoesNotExist:
                    logger.info('Car number {} does not exist'.format(str(number)))
                    pass 
                else:
                    auth_fail = False
                    abon.context = c.number
                    abon.save()
                    self.move_auth(abon, 'pass', PASS, 0, False)
            if auth_fail:
                self.move_auth(abon, msg='errauth')
        else:
            abon.active = 0
            abon.save()
            self.move_auth(abon, 'tryout', BAN)


    # Обработка ключа авторизации
    @log_decorator
    def passw(self, abon, upd):
        if PASS in abon.state and abon.secret == upd.message.text.strip():
            try:
                c = Car.objects.get(number__iexact=abon.context)
            except Car.DoesNotExist:
                pass
            else:
                abon.car = c
                abon.save()
                self.move_auth(abon, 'authok', READY, 0, True)
        else:
            self.move_auth(abon, 'errpass', PASS, 1, False)


    # Проверка привязанности автомобиля
    def carcheck(self, abon, upd):
        if abon.car is None:
            abon.state = START
            abon.auth_try = 0
            abon.last_seen = timezone.now()
            abon.save()
            self.move_auth(abon)


    def status(self, update, state, context=None):
        #st = [s[0] for s in STATE]
        abonent = self.abonent(update)
        if abonent:
            # Проверка соответствия статуса для перехода текущему статусу, переход возможет только вперед
            if abonent.state != STATES[STATES.index(state)-1] and abonent.state != state and not (state == READY and abonent.state == UNLOADED):
                # print('invalid state abonent.state = ', abonent.state, ' state to set = ', state)
                return None
            if context is not None:
                abonent.context = context
            abonent.state = state #st[st.index(abonent.state)-1]
            abonent.save()
            return abonent


    # Обработка начальной команды /start
    @log_decorator
    def start_callback(self, bot, update):
        update.message.reply_text('Авторегион: бот-диспетчер на связи',
                                  reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True))
        self.main(bot, update)


    # Обработка текущего статуса "READY"
    @log_decorator
    def ready(self, bot, update):
        """ READY state processing """
        self.myrace(bot, update)


    # Обработка команды от кнопки "ПРИСТУПИТЬ" и переход в статус "ACCEPTED"
    @log_decorator
    @callback_decorator
    def race_accepted_callback(self, bot, update):
        """ ACCEPT callback processing """
        r_id = update.callback_query.data.split(':')[1] # Получаем id принимаемого рейса из callback_data
        a = self.abonent(update)
        if a:
            race = a.driver.race_set.get(pk=r_id)
            # Сохраняем в абоненте рейс, статус и id запроса
            if race.state == Race.CREATE:
                logger.info('Accepting: Callback race ID = {}'.format(r_id))
                a = self.status(update, ACCEPTED, update.callback_query.id + ':' + str(expire()))
                if a is not None:
                    a.race = race
                    a.car = race.car
                    a.save()

                    # Сохраняем в рейсе дату принятия
                    race.race_date = timezone.now()
                    race.state = Race.ACCEPTED
                    race.save()

                    self.accepted(bot, update)


    # Обработка текущего статуса "ACCEPTED"
    @log_decorator
    @reply_callback_decorator
    def accepted(self, bot, update):
        """ ACCEPTED state processing """
        a = self.abonent(update)
        if a:
            kb = keyboards[a.state]
            kb[0][0].callback_data = r'/loading:' + str(a.race_id)
    #        text  = u'<pre>┏━━━━━━━━━━━━━━━━┓</pre>\n'
            text = self.race_info(a.race)
            text += u'\n---\n'
            text += u'Направляйтесь к месту погрузки.\nПо прибытию на место и завершения погрузки нажмите соответствующую кнопку и введите данные одометра и загруженный вес.\n'
            #text += u'---\n'
            #text += u'<pre>' + a.race.supplier.name + '</pre>\n'
            #text += u'<pre>──────────────────────────────</pre>\n'
            #text += u'<pre>' + a.race.get_load_place + '</pre>\n'
            return {
                'delete': True,
                'send': text,
                'reply_markup': InlineKeyboardMarkup(kb)
            }


    # Обработка текущего статуса "RACE"
    @log_decorator
    @reply_callback_decorator
    def race(self, bot, update):
        """ RACE state processing """
        a = self.abonent(update)
        if a:
            kb = keyboards[a.state]
            kb[0][0].callback_data = r'/unloading:' + str(a.race_id)
            #text = self.race_info(a)
            text = self.race_info(a.race)
            text += u'\n---\n'
            text += u'Направляйтесь к месту выгрузки.\nПо прибытию на место и завершения выгрузки нажмите соответствующую кнопку и введите данные одометра и выгруженный вес.\n'
            #text += u'---\n'
            #text += u'<pre>' + a.race.customer.name + '</pre>\n'
            #text += u'<pre>' + a.race.get_unload_place + '</pre>\n'
            return {
                'delete': True,
                'send': text,
                'reply_markup': InlineKeyboardMarkup(kb)
            }


    # Обработка команды от кнопки "ПОГРУЗКА" и переход в статус "LOADING"
    @log_decorator
    @reply_callback_decorator
    def loading_callback(self, bot, update):
        if self.status(update, LOADING, update.callback_query.id + ':' + str(expire())):
            return {
                'delete': True,
                'send': 'Ваш рейс в состоянии погрузки. Введите показания одометра на момент погрузки:',
                'reply_markup': ForceReply(force_reply=True)
            }


    # Обработка команды от кнопки "ВЫГРУЗКА" и переход в статус "UNLOADING"
    @log_decorator
    @reply_callback_decorator
    def unloading_callback(self, bot, update):
        if self.status(update, UNLOADING, update.callback_query.id + ':' + str(expire())):
            return {
                'delete': True,
                'send': 'Ваш рейс в состоянии выгрузки. Введите показания одометра на момент выгрузки:',
                'reply_markup': ForceReply(force_reply=True)
            }


    # Обработка команды от кнопки "Да" подтверждения ввода одометра на ПОГРУЗКЕ
    @log_decorator
    @reply_callback_decorator
    @confirm_callback_decorator
    def confirm_load_odometer_callback(self, bot, update):
        data = update.callback_query.data.split(':')[1]
        a = self.status(update, LOADED, update.callback_query.id + ':' + str(expire()))
        if a:        
            race = a.race
            race.s_milage = int(data)
            race.save()
            return {
                'delete': True,
                'send': 'Ваш рейс в состоянии погрузки. Введите загруженный вес в килограммах: ',
                'reply_markup': ForceReply(force_reply=True)
            }


    # Запрос ввода данных одометра на ПОГРУЗКЕ
    @log_decorator
    @modal_input_decorator(confirm_text=u'Введенное показание одометра на погрузке: <b>{}</b> км. Всё верно?',
                           error_text=u'Показания одометра на погрузке введены с ошибкой. Введите правильно:')
    def query_load_odometer(self, bot, update, keyboard=confirm_keyboard, callback_command=''):
        return keyboard


    # Обработка команды от кнопки "Да" подтверждения ввода одометра на ВЫГРУЗКЕ
    @log_decorator
    @reply_callback_decorator
    @confirm_callback_decorator
    def confirm_unload_odometer_callback(self, bot, update):
        data = update.callback_query.data.split(':')[1]
        a = self.status(update, UNLOADED, update.callback_query.id + ':' + str(expire()))
        if a:
            race = a.race
            race.e_milage = int(data)
            race.save()
            return {
                'delete': True,
                'send': 'Ваш рейс в состоянии выгрузки. Введите выгруженный вес в килограммах: ',
                'reply_markup': ForceReply(force_reply=True)
            }


    # Запрос ввода данных одометра на ВЫГРУЗКЕ
    @log_decorator
    @modal_input_decorator(confirm_text=u'Введенное показание одометра на выгрузке: <b>{}</b> км. Всё верно?',
                           error_text=u'Показания одометра на выгрузке введены с ошибкой. Введите правильно:')
    def query_unload_odometer(self, bot, update, keyboard=confirm_keyboard, callback_command=''):
        return keyboard


    # Обработка команды от кнопки "Да" подтверждения ввода загруженного веса на ПОГРУЗКЕ
    @log_decorator
    @reply_callback_decorator
    @confirm_callback_decorator
    def confirm_load_weight_callback(self, bot, update):
        data = update.callback_query.data.split(':')[1]
        a = self.status(update, RACE, update.callback_query.id + ':' + str(expire()))
        if a:
            race = a.race
            race.weight_load = int(data) / 1000
            race.state = Race.LOAD
            race.save()
            return {
                'delete': True,
                'send': False,
                'call': self.race # call - вызов следующего обработчика
            }


    # Запрос ввода данных загруженного веса на ПОГРУЗКЕ
    @log_decorator
    @modal_input_decorator(confirm_text=u'Введенный вес: <b>{}</b> кг. Всё верно?',
                           error_text=u'Вес введён с ошибкой. Введите загруженный вес в килограммах:')
    def query_load_weight(self, bot, update, keyboard=confirm_keyboard, callback_command=''):
        return keyboard


    # Обработка команды от кнопки "Да" подтверждения ввода выгруженного веса на ВЫГРУЗКЕ
    @log_decorator
    @reply_callback_decorator
    @confirm_callback_decorator
    def confirm_unload_weight_callback(self, bot, update):
        data = update.callback_query.data.split(':')[1]        
        a = self.status(update, READY, update.callback_query.id + ':' + str(expire()))
        if a:
            a.race.weight_unload = int(data) / 1000
            a.race.state = Race.UNLOAD
            a.race.arrival_time = timezone.now()
            a.race.shoulder = a.race.e_milage - a.race.s_milage
            a.race.save()
            race_id = a.race.id_race
            a.race = None
            a.save()
            return {
                'delete': True,
                'send': 'Рейс №{} завершён. Приступайте к следующему.'.format(str(race_id)),
                'call': self.complete
            }


    # Запрос ввода данных выгруженного веса на ВЫГРУЗКЕ
    @log_decorator
    @modal_input_decorator(confirm_text=u'Введенный вес: <b>{}</b> кг. Всё верно?',
                           error_text=u'Вес введён с ошибкой. Введите выгруженный вес в килограммах:')
    def query_unload_weight(self, bot, update, keyboard=confirm_keyboard, callback_command=''):
        return keyboard

        
    @log_decorator
    @reply_callback_decorator
    def complete(self, bot, update):
        return {
            'delete': True,
            'send': u'Ваш текущий рейс завершен.\nНажмите кнопку "Мои рейсы", чтобы узнать о предстоящих новых рейсах.\n',
            'reply_markup': ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True)
        }

        
    # Отправка данных по текущему рейсу
    @log_decorator
    @callback_decorator
    def race_callback(self, bot, update):
        update.callback_query.edit_message_text(text='РЕЙС: ')
#            race_accept_keyboard = [[InlineKeyboardButton(text='✅ Принято', callback_data='/race_accepted')]]
        reply_markup = InlineKeyboardMarkup(race_accept_keyboard)
        update.callback_query.edit_message_reply_markup(reply_markup=reply_markup)


    @log_decorator    
    @reply_callback_decorator
    def stat_callback(self, bot, update):
        a = self.abonent(update)
        if a:
            if a.driver:
                period = update.callback_query.data.split(':')[1]
                ms, ys = period.split('.')
                m, y = int(ms), int(ys)
                start = timezone.make_aware(datetime(y, m, 1))
                if int(m) == 12:
                    end = timezone.make_aware(datetime(y+1, 1, 1))
                else:
                    end = timezone.make_aware(datetime(y, m+1, 1))
                stat = u'Статистика за: {}\n'.format(period)
                stat += u'Водитель: ' + a.driver.name + '\n'
                query_state = Q(state=Race.UNLOAD)|Q(state=Race.FINISH)|Q(state=Race.CHECKED)|Q(state=Race.END)
                races = Race.objects.filter(query_state, driver_id=a.driver.id_driver, race_date__range=(start, end)).exclude().order_by('race_date')
                sum = 0
                if len(races) == 0:
                    stat += u'<pre>В выбранном периоде нет завершенных рейсов.</pre>\n'
                else:
                    stat += u'<pre> Рейс | Дата       | Цена</pre>\n'
                    stat += u'<pre>───────────────────────────</pre>\n'
                for r in races:
                    stat += u'<pre>{}\t|\t{}\t|\t{}</pre>\n'.format(str(r.id_race), r.race_date.strftime('%d.%m.%Y'), str(r.price))
                    sum += r.price
                else:
                    stat += u'<pre>───────────────────────────</pre>\n'
                    stat += u'<pre>Итого рейсов: {}\nСумма: {} руб.</pre>\n'.format(str(len(races)), str(sum))
                return {
                    'delete': True,
                    'send': stat,
                    'reply_markup': ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True)
                }
            else:
                return {
                    'delete': True,
                    'send': u'Ваш профиль не связан с водителем. Обратитесь к диспетчеру.',
                    'reply_markup': ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True)                
                }
    
    @log_decorator
    @callback_decorator
    def from_callback(self, bot, update):
        pk = update.callback_query.data.split('|')[1]
        race = Race.objects.get(pk=pk)
        for lk in load_keyboard[0]:
            lk.callback_data += '|' + pk
        bot.sendVenue(update.callback_query.from_user.id,
                      51.2875544, 58.4370285,
                      'Место погрузки',
                      race.get_load_place,
                      reply_markup=InlineKeyboardMarkup(load_keyboard))

    @log_decorator
    @callback_decorator
    def to_callback(self, bot, update):
        pk = update.callback_query.data.split('|')[1]
        race = Race.objects.get(pk=pk)
        bot.sendVenue(update.callback_query.from_user.id,
                      51.6089419, 52.9732831,
                      'Место разгрузки',
                      race.get_unload_place,
                      reply_markup=InlineKeyboardMarkup(unload_keyboard))


    @log_decorator                  
    @callback_decorator
    def no_callback(self, bot, update):
        a = self.abonent(update)
        if a:
            if LOADING == a.state:
                self.loading_callback(bot, update)
            if LOADED == a.state:
                update.callback_query.data = '/load_odo:' + str(a.race.s_milage)
                self.confirm_load_odometer_callback(bot, update)
            if UNLOADING == a.state:
                self.unloading_callback(bot, update)
            if UNLOADED == a.state:
                update.callback_query.data = '/unload_odo:' + str(a.race.e_milage)
                self.confirm_unload_odometer_callback(bot, update)


    @callback_decorator
    def close_callback(self, bot, update):
        bot.delete_message( chat_id=update.callback_query.message.chat.id,
                            message_id=update.callback_query.message.message_id)

    def get_keyboard(self, abon):
        return keyboards[abon.state]


    @log_decorator    
    @reply_callback_decorator
    def current_race(self, bot, update):
        """ Sending info about current race """
        r = None
        text = u''
        abon = self.abonent(update)
        if abon:
            if abon.driver_id is None:
                # Если водитель не привязан к абоненту, то диспетчеру нужно сделать такую привязку
                text += u'Водитель не определён. Обратитесь к диспетчеру для сопоставления с данными водителя.\n\n'
            elif abon.race_id is None:
                # Если рейс не привязан, значит выбираем все рейсы для авто в статусе "Создан"
                # и не позднее RACE_DATE_RANGE от текущей даты
                all = Race.objects.filter(driver_id=abon.driver.id_driver,
                                          state=Race.CREATE,
                                          race_date__gte=timezone.now()-timedelta(days=RACE_DATE_RANGE)).order_by('race_date')
                if len(all) > 0:
                    r = all[0]
                    r_id = r.id_race
            else:
                r = abon.race
            
            kb = None
            result = {'delete': True}
            if r is not None:
                text += u'ВАШ ТЕКУЩИЙ РЕЙС:\n---\n'
                text += self.race_info(r)
                kb = self.get_keyboard(abon)
                kb[0][0].callback_data = r'/accepted:' + str(r.id_race)
                result.update({'reply_markup': InlineKeyboardMarkup(kb)})
            else:
                result.update({'reply_markup': ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True)})
                text += u'Текущие рейсы отсутствуют.\n'

            result.update({'send': text})    
            return result
        
    
    @log_decorator
    def future_race(self, bot, update, send=False):
        """ Get future and current race for the abonent """ 
        abon = self.abonent(update)
        if abon:
            current_race_id = 0
            current_race = None
            
            # Если водитель не привязан к абоненту, то выдаём соответствующее сообщение и выходим из функции
            if abon.driver is None:
                text = u'Ваш профиль не связан с водителем. Обратитесь к диспетчеру.\n\n'
                bot.sendMessage(str(abon.telegram_id), text, parse_mode='HTML')            
                return False

            if abon.race is not None:
                current_race_id = abon.race.id_race
                current_race = abon.race

            # Выбираем будущие рейсы в статусе "Создан" и с датой начала не ранее X (2/3/7 - сколько нужно) дней от текущего
            future_races = Race.objects.filter( driver_id=abon.driver.id_driver,
                                                state=Race.CREATE,
                                                race_date__gte=timezone.now()-timedelta(days=RACE_DATE_RANGE)).order_by('race_date')

            # Если текущий рейс из контекста, то удаляем его из выборки будущих рейсов
            if current_race_id:
                future_races = future_races.exclude(id_race=current_race_id)
            # Иначе, если в контексте не содержится номера текущего рейса,
            # то берём самый ближайший из выборки будущих и так же удаляем его из выборки будущих
            elif len(future_races):
                current_race = future_races[0]
                current_race_id = current_race.id_race
                future_races = future_races[1:]

            # Если выборка будущих рейсов не пуста, то выводим информацию по предстоящим рейсам
            if len(future_races) != 0 and send:
                text = u'Предстоящие рейсы для водителя ' + abon.driver.name + u'\n'
                text += u'<pre>_____________________________________________</pre>\n'
                text += u'<pre>Номер | Дата             | Машина</pre>\n'
                text += u'<pre>—————————————————————————————————————————————</pre>\n'
                for r in future_races:
                    text += u'<pre>' + str(r.id_race).rjust(5, ' ')
                    text += u' | ' + r.race_date.strftime('%d.%m.%Y %H:%M')
                    text += u' | ' + r.car.number + u'</pre>\n'
                text += u'<pre>—————————————————————————————————————————————</pre>\n'
                bot.sendMessage(str(abon.telegram_id), text, parse_mode='HTML')

            if current_race is None and current_race_id != 0:
                current_race = Race.objects.get(pk=current_race_id)

            if current_race_id != 0:
                # Сохраняем номер текущего рейса в контекст
                if abon.context is None:
                    abon.context = str(current_race_id)
                    abon.save()
            else:
                bot.sendMessage(str(abon.telegram_id), u'У вас нет назначенных рейсов.', reply_markup = ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True))

                
    def myrace(self, bot, update):
        self.future_race(bot, update, send=True)
        self.current_race(bot, update)

    @staticmethod
    def get_tid(update):
        """ Get Telegram ID of user """
        upd = update
        if update.callback_query is not None:
            upd = update.callback_query
        return upd.message.chat_id, upd.message.chat.first_name

    @staticmethod    
    def abonent(update):
        """ Create or get Abonent from DB by chat_id from message """
        tid, name = AvtrgnBot.get_tid(update)
        a, created = Abonent.objects.get_or_create(telegram_id=tid)
        if created:
            a.telegram_nick = name
            a.secret = BaseUserManager.make_random_password(length=8, allowed_chars='0123456789')
            a.last_seen = timezone.now()
            a.save()
            self.admin_notify(a)
        else:
            a.telegram_nick = name
            a.last_seen = timezone.now()
            a.save()
            
        if a.active:
            return a
        else:
            return None

        
    def admin_notify(self, abonent):
        """ Notify administrators the new abonent connected """
        admins = Abonent.objects.filter(admin=True)
        bot = DjangoTelegramBot.getBot()
        if len(admins) > 0:
            for a in admins:
                result = bot.sendMessage(
                    str(a.telegram_id),
                    u'=== ADMIN NOTIFY ===\n<Новый абонент подключен>\n{}/secret:{}'.format(str(abonent), str(abonent.secret))
                )
                logger.info('NOTIFY: Abonent created = {} result = {}'.format(str(abonent), result))
    

    @log_decorator
    def statistics(self, bot, update):
        """ Send statistics dialog to abonent """
        a = self.abonent(update)
        if a:
            if a.driver:
                months = ('Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь')
                d = datetime.today()
                month_now = d.month - 1
                y1, y2 = d.year, d.year
                if month_now == 0:
                    month_last = 11
                    y1 = d.year - 1
                else:
                    month_last = month_now - 1
                kb = InlineKeyboardMarkup([[InlineKeyboardButton(u'За {} {}'.format(months[month_last], y1), callback_data=r'/stat:'+str(month_last+1)+'.'+str(y1)),
                                            InlineKeyboardButton(u'За {} {}'.format(months[month_now], y2), callback_data=r'/stat:'+str(month_now+1)+'.'+str(y2))]])    
                update.message.reply_html(u'Выберите период, за который необходима статистика по выполненным рейсам.', reply_markup=kb)
            else:
                update.message.reply_html(u'Ваш профиль не связан с водителем. Обратитесь к диспетчеру.\n\n')
            

    @log_decorator        
    def main(self, bot, update):
        """ Main dispatcher of text messages from abonent """
        a = self.abonent(update)
        if a:                    
            logger.info('Abonent {} state = {} at time = {}'.format(str(a), a.state, time()))
            
            # Обработка статусов авторизации
            if START in a.state:
                self.start(a, update)
            elif AUTH == a.state:
                self.auth(a, update)
            elif PASS == a.state:
                self.passw(a, update)
            elif BAN == a.state:
                pass

            # Обработка команды "Мои рейсы" и рабочих статусов
            if update.message.text == 'Мои рейсы':
                if READY == a.state:
                    #self.carcheck(a, update)
                    self.ready(bot, update)
                elif ACCEPTED == a.state:
                    self.accepted(bot, update)
                elif LOADING == a.state:
                    self.query_load_odometer(bot, update, callback_command=r'/load_odo')
                elif LOADED == a.state:
                    self.query_load_weight(bot, update, callback_command=r'/load_weight')
                elif RACE == a.state and update.message.text == 'Мои рейсы':
                    self.race(bot, update)
                elif UNLOADING == a.state:
                    self.query_unload_odometer(bot, update, callback_command=r'/unload_odo')
                elif UNLOADED == a.state:
                    self.query_unload_weight(bot, update, callback_command=r'/unload_weight')
#                else:
#                    a.state = START             # Сброс статуса на начальный
#                    a.save()
            # Обработка команды "Статистика" в статусах, отличных от статусов авторизации
            elif update.message.text == 'Статистика' and a.state not in (START, AUTH, PASS, BAN):
                self.statistics(bot, update)

    def get_secret_command(self, bot, update):
        a = self.abonent(update)
        if a and a.admin:
            data = update.message.text.split(' ')
            abn = Abonent.objects.filter(telegram_nick__iexact=data[1])
            if abn.count() > 0:
                for ab in abn:
                    update.message.reply_text(ab.telegram_nick + ':' + ab.secret)


    @staticmethod
    def race_info(race):
        text = u''
        text += u'<b>Рейс:</b> <pre>№ {} / {}</pre>\n'.format(str(race.id_race), race.race_date.strftime('%d.%m.%Y %H:%M'))
        text += u'<b>Водитель:</b> <pre>{}</pre>\n'.format(race.driver.name)
        text += u'<b>Машина:</b> <pre>{} {}</pre>\n'.format(race.car.brand, race.car.number)
        text += u'<b>Место погрузки:</b>\n'
        text += u'<pre>{}</pre>\n<pre>{}</pre>\n'.format(race.supplier.name, race.get_load_place)
        text += u'<b>Место выгрузки:</b>\n'
        text += u'<pre>{}</pre>\n<pre>{}</pre>\n'.format(race.customer.name, race.get_unload_place)
        text += u'<b>Груз:</b> <pre>{}</pre>\n<b>Цена:</b> <pre>{} руб.</pre>\n'.format(race.product.name, str(race.price))
        text += u'<b>Статус:</b> <pre>{}</pre>\n'.format(race.state)
        if race.s_milage > 0:
            text += u'<b>Одометр на погрузке:</b> <pre>{} км</pre>\n'.format(str(race.s_milage))
        if race.weight_load > 0:
            text += u'<b>Загружено:</b> <pre>{} т.</pre>\n'.format(str(race.weight_load))
        if race.e_milage > 0:
            text += u'<b>Одометр на выгрузке:</b> <pre>{} км</pre>\n'.format(str(race.e_milage))
        if race.weight_unload > 0:
            text += u'<b>Выгружено:</b> <pre>{} т.</pre>\n'.format(str(race.weight_unload))
        return text
                    

    @staticmethod
    @receiver(post_save, sender=Race)
    def race_save_notify(sender, instance, created, **kwargs):
        """ Notifier of Race model update """
        # Нужно добавить синхронизацию статусов модели Race и статуса абонента
        abonents = Abonent.objects.filter(driver_id=int(instance.driver_id))
        bot = DjangoTelegramBot.getBot()
        if len(abonents) > 0:
            if created:
                for a in abonents:
                    result = bot.sendMessage(
                                str(a.telegram_id), 
                                u'Вам назначен новый рейс.\n---\n' +
                                AvtrgnBot.race_info(instance) +
                                u'\n---\nЧтобы приступить отправьте команду <b>"Мои рейсы"</b>.', 
                                parse_mode='HTML',
                                reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True))
                    logger.info('NOTIFY: Race {} created for abonent = {}'.format(str(instance.id_race), a))
                    log = Log(abonent='bot > '+str(a), driver=instance.driver, method='race_save_notify', state=a.state, car=instance.car, race=instance.id_race, message='Создан новый рейс')
                    log.save()
            else:
                #if instance.state == Race.CREATE:
                for a in abonents:
                    logger.info('NOTIFY: To Abonent = {} Context = {}'.format(str(a), a.context))
                    if instance.state == Race.UNLOAD and a.race == instance:
                        # Если рейс выгружен (статус Race.UNLOAD), то отвязываем этот текущий рейс от абонента
                        a.race = None
                        a.state = READY
                    if a.context is not None and len(a.context) > 12:
                        query_id, exp = a.context.split(':')
                        expire = float(exp)
                        a.context = None
                        if time() < expire:
                            result = bot.answerCallbackQuery(query_id, 'Рейс №' + str(instance.id_race) + ' обновлён.')
                            logger.info('NOTIFY: Race {} updated, Abonent = {}'.format(str(instance.id_race), a))
                    a.save()
                log = Log(abonent='bot > '+str(a), driver=instance.driver, method='race_save_notify', state=a.state, car=instance.car, race=instance.id_race, message='Рейс изменён')
                log.save()

        

    @log_decorator
    def decimal(self, bot, update):
        """ Decimal input dispatcher """
        a = self.abonent(update)
        if a:
            if PASS == a.state:
                self.passw(a, update)
            if LOADING == a.state:
                self.query_load_odometer(bot, update, callback_command=r'/load_odo')
            if LOADED == a.state:
                self.query_load_weight(bot, update, callback_command=r'/load_weight')
            if UNLOADING == a.state:
                self.query_unload_odometer(bot, update, callback_command=r'/unload_odo')
            if UNLOADED == a.state:
                self.query_unload_weight(bot, update, callback_command=r'/unload_weight')


    def start_bot(self):
        dp = DjangoTelegramBot.dispatcher
        dp.add_handler(CommandHandler('start', self.start_callback))
        dp.add_handler(CommandHandler('secret', self.get_secret_command))
        dp.add_handler(CallbackQueryHandler(self.race_callback, pattern=r'/race$'))
        dp.add_handler(CallbackQueryHandler(self.from_callback, pattern=r'/from'))
        dp.add_handler(CallbackQueryHandler(self.to_callback, pattern=r'/to'))
        dp.add_handler(CallbackQueryHandler(self.loading_callback, pattern=r'/loading'))
        dp.add_handler(CallbackQueryHandler(self.unloading_callback, pattern=r'/unloading'))
        dp.add_handler(CallbackQueryHandler(self.race_accepted_callback, pattern=r'/accepted'))
        dp.add_handler(CallbackQueryHandler(self.stat_callback, pattern=r'/stat'))
        dp.add_handler(CallbackQueryHandler(self.close_callback, pattern=r'/close$'))
        dp.add_handler(CallbackQueryHandler(self.confirm_load_odometer_callback, pattern=r'/load_odo'))
        dp.add_handler(CallbackQueryHandler(self.confirm_load_weight_callback, pattern=r'/load_weight'))
        dp.add_handler(CallbackQueryHandler(self.confirm_unload_odometer_callback, pattern=r'/unload_odo'))
        dp.add_handler(CallbackQueryHandler(self.confirm_unload_weight_callback, pattern=r'/unload_weight'))
        dp.add_handler(CallbackQueryHandler(self.no_callback, pattern=r'/no'))
        dp.add_handler(MessageHandler(Filters.regex(r'^\d+$'), self.decimal))
        dp.add_handler(MessageHandler(Filters.text, self.main))
        return True

    def __str__(self):
        return '{}:{}'.format(self.me['id'], self.me['username'])

                

#logging.basicConfig(filename=u'bot.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("Loading handlers for telegram bot")

    bot = AvtrgnBot()
    bot.start_bot()
