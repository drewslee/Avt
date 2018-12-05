from time import time
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth.models import BaseUserManager
from django.conf import settings as djangoSettings
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

RACE_DATE_RANGE = 3 # Диапазон дней от текущей даты, за которые рейсы считаются предстоящими

# Bot status list
START, AUTH, PASS, READY, RACE, ACCEPTED, LOADING, LOADED, UNLOADING, UNLOADED, BAN = \
'start', 'auth', 'pass', 'ready', 'race', 'accepted', 'loading', 'loaded', 'unloading', 'unloaded', 'ban'
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

main_keyboard = [['Мои рейсы']]
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
    def wrapper(self, bot, update):
#        if update.callback_query.answer():
            return method(self, bot, update)
    return wrapper

    
def reply_callback_decorator(method):
    def wrapper(self, bot, update):
        print('reply decorator')
        result = method(self, bot, update)
        if result is not None:            
            if result.get('send') is not None and result['send']:                      
                if update.callback_query:
                    update.callback_query.message.edit_text(result['send'], parse_mode='HTML')
                    if result.get('reply_markup') is not None:
                        update.callback_query.message.edit_reply_markup(reply_markup=result['reply_markup'])
                else:
                    if result.get('reply_markup') is not None:
                        update.message.reply_html(result['send'], reply_markup=result['reply_markup'])    
                    else:
                        update.message.reply_html(result['send'])                        

            if result.get('call') is not None:
                return result['call'](bot, update)
                
    return wrapper
        
    
def confirm_callback_decorator(method):
    def wrapper(self, bot, update):
        print('confirm decorator')
        data = update.callback_query.data.split(':')[1]
        if int(data) > 0:
            return method(self, bot, update)
    return wrapper
    
    
def modal_input_decorator(regex=r'^\d+$', confirm_text='confirm', error_text='error'):
    def decorator(method):
        def decorated(*args, **kwargs):
            self = args[0]
            bot = args[1]
            update = args[2]
            upd = update
            if update.callback_query is not None:
                upd = update.callback_query
                
            keyboard = method(*args, **kwargs)
            print('callback data', keyboard[0][0].callback_data)
            keyboard[0][0].callback_data = kwargs['callback_command'] + ':' + update.message.text.strip()
            print(keyboard[0][0].callback_data)
            print(keyboard[0][1].callback_data)
            
            if re.search(regex, upd.message.text.strip(), flags=re.IGNORECASE) is not None:
                bot.sendMessage(upd.message.chat_id, confirm_text.format(upd.message.text.strip()), 
                                     parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
            else:
                bot.sendMessage(upd.message.chat_id, error_text, 
                                     parse_mode='HTML', reply_markup=ForceReply(force_reply=True))    
                    
        return decorated
    return decorator
    
    
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
        'authok' : u'Вы авторизованы.',
        'tryout' : u'Количество попыток авторизации исчерано.',
        'banned' : u'Вам отказано в доступе.',
        'select' : u'Выберите команду',
    }            
        
    # Обработка начального статуса            
    def start(self, abon, update):
        update.message.reply_text(self.messages['hello'])
        if START in abon.state:
            abon.state = AUTH
            abon.save()
            update.message.reply_text(self.messages['auth'], reply_markup=ForceReply(force_reply=True))

            
    # Процедура отправки типового сообщения
    def send(self, uid, m = 'hello', **kwargs):
        bot = DjangoTelegramBot.getBot()
        bot.sendMessage(uid, self.messages[m])

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
                    print('car does not exist')
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
        if context is not None:
            abonent.context = context
        abonent.state = state #st[st.index(abonent.state)-1]
        abonent.save()
        return abonent
             
            
    # Обработка начальной команды /start
    def start_callback(self, bot, update):
        update.message.reply_text('Авторегион: бот-диспетчер на связи', 
                                  reply_markup = ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True))        
        self.main(bot, update)
        
                   
    # Обработка текущего статуса "READY"
    def ready(self, bot, update):
        """ READY state processing """
        self.myrace(bot, update)


    # Обработка команды от кнопки "ПРИСТУПИТЬ" и переход в статус "ACCEPTED"
    @callback_decorator
    def race_accepted_callback(self, bot, update):
        """ ACCEPT callback processing """    
        r_id = update.callback_query.data.split(':')[1] # Получаем id принимаемого рейса из callback_data
        # Сохраняем в абоненте рейс, статус и id запроса
        a = self.status(update, ACCEPTED, update.callback_query.id + ':' + str(expire()))
        race = a.car.race_set.get(pk=r_id)
        a.race = race
        a.save()
                
        # Сохраняем в рейсе дату принятия
        race.race_date = timezone.now()
        race.state = Race.ACCEPTED
        race.save()
        
        self.accepted(bot, update)
        

    def race_info(self, abon):
        text = u''
        text += u'<pre>Рейс: {} | Статус: {} </pre>\n'.format(str(abon.race_id), abon.race.state)
        text += u'<pre>──────────────────────────────</pre>\n'
        return text
    
    
    # Обработка текущего статуса "ACCEPTED" 
    @reply_callback_decorator    
    def accepted(self, bot, update):
        """ ACCEPTED state processing """
        abon = self.abonent(update)
        kb = keyboards[abon.state]
        kb[0][0].callback_data += ':' + str(abon.race_id)
#        text  = u'<pre>┏━━━━━━━━━━━━━━━━┓</pre>\n'
        text = self.race_info(abon)
        text += u'<pre>Направляйтесь к месту погрузки</pre>\n'
        text += u'<pre>──────────────────────────────</pre>\n'
        text += u'<pre>' + abon.race.supplier.name + '</pre>\n'
        text += u'<pre>──────────────────────────────</pre>\n'
        text += u'<pre>' + abon.race.get_load_place + '</pre>\n'
        return {
            'delete': True,
            'send': text,
            'reply_markup': InlineKeyboardMarkup(kb)            
        }


    # Обработка текущего статуса "RACE"    
    @reply_callback_decorator    
    def race(self, bot, update):
        """ RACE state processing """
        abon = self.abonent(update)
        kb = keyboards[abon.state]
        kb[0][0].callback_data += ':' + str(abon.race_id)
        text = self.race_info(abon)
        text += u'<pre>Направляйтесь к месту выгрузки</pre>\n'
        text += u'<pre>──────────────────────────────</pre>\n'
        text += u'<pre>' + abon.race.customer.name + '</pre>\n'
        text += u'<pre>' + abon.race.get_unload_place + '</pre>\n'
        return {
            'delete': True,
            'send': text,
            'reply_markup': InlineKeyboardMarkup(kb)            
        }
            
            
    # Обработка команды от кнопки "ПОГРУЗКА" и переход в статус "LOADING"        
    @reply_callback_decorator
    def loading_callback(self, bot, update):
        self.status(update, LOADING, update.callback_query.id + ':' + str(expire()))
        return {
            'delete': True,
            'send': 'Ваш рейс в состоянии погрузки. Введите показания одометра на момент погрузки:',
            'reply_markup': ForceReply(force_reply=True)
        }

        
    # Обработка команды от кнопки "ВЫГРУЗКА" и переход в статус "UNLOADING"        
    @reply_callback_decorator
    def unloading_callback(self, bot, update):
        self.status(update, UNLOADING, update.callback_query.id + ':' + str(expire()))
        return {
            'delete': True,
            'send': 'Ваш рейс в состоянии выгрузки. Введите показания одометра на момент выгрузки:',
            'reply_markup': ForceReply(force_reply=True)
        }
        

    # Обработка команды от кнопки "Да" подтверждения ввода одометра на ПОГРУЗКЕ   
    @reply_callback_decorator    
    @confirm_callback_decorator
    def confirm_load_odometer_callback(self, bot, update):
        data = update.callback_query.data.split(':')[1]
        a = self.status(update, LOADED, update.callback_query.id + ':' + str(expire()))
        race = a.race
        race.s_milage = int(data)
        race.save()
        return {
            'delete': True, 
            'send': 'Ваш рейс в состоянии погрузки. Введите загруженный вес: ',
            'reply_markup': ForceReply(force_reply=True) 
        }
                    

    # Запрос ввода данных одометра на ПОГРУЗКЕ   
    @modal_input_decorator(confirm_text=u'Введенное показание одометра на погрузке: <b>{}</b> км. Всё верно?', 
                           error_text=u'Показания одометра на погрузке введены с ошибкой. Введите правильно:')
    def query_load_odometer(self, bot, update, keyboard=confirm_keyboard, callback_command=''):
        return keyboard

        
    # Обработка команды от кнопки "Да" подтверждения ввода одометра на ВЫГРУЗКЕ   
    @reply_callback_decorator    
    @confirm_callback_decorator
    def confirm_unload_odometer_callback(self, bot, update):
        data = update.callback_query.data.split(':')[1]
        a = self.status(update, UNLOADED, update.callback_query.id + ':' + str(expire()))
        race = a.race
        race.e_milage = int(data)
        race.save()
        return {
            'delete': True, 
            'send': 'Ваш рейс в состоянии выгрузки. Введите выгруженный вес: ',
            'reply_markup': ForceReply(force_reply=True) 
        }
            

    # Запрос ввода данных одометра на ВЫГРУЗКЕ   
    @modal_input_decorator(confirm_text=u'Введенное показание одометра на выгрузке: <b>{}</b> км. Всё верно?', 
                           error_text=u'Показания одометра на выгрузке введены с ошибкой. Введите правильно:')
    def query_unload_odometer(self, bot, update, keyboard=confirm_keyboard, callback_command=''):
        return keyboard
        
        
    # Обработка команды от кнопки "Да" подтверждения ввода загруженного веса на ПОГРУЗКЕ   
    @reply_callback_decorator    
    @confirm_callback_decorator
    def confirm_load_weight_callback(self, bot, update):
        data = update.callback_query.data.split(':')[1]
        a = self.status(update, RACE, update.callback_query.id + ':' + str(expire()))
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
    @modal_input_decorator(confirm_text=u'Введенный вес: <b>{}</b> кг. Всё верно?', 
                           error_text=u'Вес введён с ошибкой. Введите загруженный вес в килограммах:')
    def query_load_weight(self, bot, update, keyboard=confirm_keyboard, callback_command=''):
        return keyboard


    # Обработка команды от кнопки "Да" подтверждения ввода выгруженного веса на ВЫГРУЗКЕ   
    @reply_callback_decorator    
    @confirm_callback_decorator
    def confirm_unload_weight_callback(self, bot, update):
        data = update.callback_query.data.split(':')[1]        
        print('data', data)
        a = self.status(update, READY, update.callback_query.id + ':' + str(expire()))
        a.race.weight_unload = int(data) / 1000
        a.race.state = Race.UNLOAD
        a.race.arrival_time = timezone.now()
        a.race.save()
        print(a.race)
        race_id = a.race.id_race
        a.race = None
        a.save()            
        return {
            'delete': False, 
            'send': 'Рейс №{} завершён. Приступайте к следующему.'.format(str(race_id)), 
            'call': self.ready
        }
        
        
    # Запрос ввода данных выгруженного веса на ВЫГРУЗКЕ   
    @modal_input_decorator(confirm_text=u'Введенный вес: <b>{}</b> кг. Всё верно?', 
                           error_text=u'Вес введён с ошибкой. Введите выгруженный вес в килограммах:')
    def query_unload_weight(self, bot, update, keyboard=confirm_keyboard, callback_command=''):
        return keyboard

                       
    # Отправка данных по текущему рейсу
    @callback_decorator
    def race_callback(self, bot, update):
        update.callback_query.edit_message_text(text='РЕЙС: ')
#            race_accept_keyboard = [[InlineKeyboardButton(text='✅ Принято', callback_data='/race_accepted')]]
        reply_markup = InlineKeyboardMarkup(race_accept_keyboard)
        update.callback_query.edit_message_reply_markup(reply_markup=reply_markup)
                        

    @callback_decorator
    def from_callback(self, bot, update):
        pk = update.callback_query.data.split('|')[1]
        print('pk = ' + pk)
        race = Race.objects.get(pk=pk)
        for lk in load_keyboard[0]:
            lk.callback_data += '|' + pk
        bot.sendVenue(update.callback_query.from_user.id,
                      51.2875544, 58.4370285,
                      'Место погрузки',
                      race.get_load_place,
                      reply_markup=InlineKeyboardMarkup(load_keyboard))
    

    @callback_decorator
    def to_callback(self, bot, update):
        pk = update.callback_query.data.split('|')[1]
        print('pk = ' + pk)
        race = Race.objects.get(pk=pk)
        bot.sendVenue(update.callback_query.from_user.id,
                      51.6089419, 52.9732831,
                      'Место разгрузки',
                      race.get_unload_place,
                      reply_markup=InlineKeyboardMarkup(unload_keyboard))

                              
    @callback_decorator
    def no_callback(self, bot, update):
        a = self.abonent(update)

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
    
           
    @reply_callback_decorator      
    def current_race(self, bot, update):
        """ Sending info about current race """
        r = None
        abon = self.abonent(update)
        if abon.race_id is None:
            # Если рейс не привязан, значит выбираем все рейсы для авто в статусе "Создан" 
            # и не позднее RACE_DATE_RANGE от текущей даты
            all = Race.objects.filter(car_id=abon.car.id_car, 
                                      state=Race.CREATE, 
                                      race_date__gte=timezone.now()-timedelta(days=RACE_DATE_RANGE)).order_by('race_date')
            print(all)
            if len(all) > 0:
                r = all[0]
                r_id = r.id_race
        else:
            r = abon.race
        
        kb = None
        result = {'delete': True}
        if r is not None:
            text = u'Текущий рейс для: ' + abon.car.number + u'\n'
            text += u'<pre>___________________________</pre>\n'
            text += u'<pre>Рейс:\t\t\t' + str(r.id_race) + u'</pre>\n'
            text += u'<pre>Дата:\t\t\t' + r.race_date.strftime('%d.%m.%Y %H:%M') + u'</pre>\n'
            text += u'<pre>Водитель:\t' + r.driver.name + u'</pre>\n'                
            text += u'—————\n'
            text += u'<pre>Поставщик:\t' + r.supplier.name + u'</pre>\n'
            text += u'<pre>Откуда:\t' + r.get_load_place + u'</pre>\n'
            text += u'—————\n'
            text += u'<pre>Покупатель:\t' + r.customer.name + u'</pre>\n'                
            text += u'<pre>Куда:\t' + r.get_unload_place + u'</pre>\n'
            text += u'—————\n'
            text += u'<pre>Груз:\t' + r.product.name + u'</pre>\n'                
            text += u'<pre>Цена рейса:\t' + str(r.price) + u'</pre>\n'                
            kb = self.get_keyboard(abon)
            kb[0][0].callback_data += ':' + str(r.id_race)
            result.update({'reply_markup': InlineKeyboardMarkup(kb)})
        else:
            text = u'Текущие рейсы для ' + abon.car.number + ' отсутствуют.\n'

        result.update({'send': text})    
        print(result)
        return result
        
        
    def future_race(self, bot, update, send=False):
        """ Get future and current race for the abonent """ 
        print('future')
        abon = self.abonent(update)
        current_race_id = 0
        current_race = None
        
        if abon.race is not None:
            current_race_id = abon.race.id_race
            current_race = abon.race
        
        # Выбираем будущие рейсы в статусе "Создан" и с датой начала не ранее X (2/3/7 - сколько нужно) дней от текущего
        future_races = Race.objects.filter( car_id=abon.car.id_car, 
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
            text = u'Предстоящие рейсы для: ' + abon.car.number + u'\n'
            text += u'<pre>_____________________________________________</pre>\n'
            text += u'<pre>Номер | Дата             | Водитель</pre>\n'
            text += u'<pre>—————————————————————————————————————————————</pre>\n'
            for r in future_races:
                text += u'<pre>' + str(r.id_race).rjust(5, ' ') 
                text += u' | ' + r.race_date.strftime('%d.%m.%Y %H:%M')
                text += u' | ' + r.driver.name + u'</pre>\n'                
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
        print('myrace')
        self.future_race(bot, update, send=True)
        self.current_race(bot, update)
                            
    
    def get_tid(self, update):
        """ Get Telegram ID of user """
        upd = update
        if update.callback_query is not None:
            upd = update.callback_query
        return upd.message.chat_id, upd.message.chat.first_name
    
    def abonent(self, update):
        """ Create or get Abonent from DB by chat_id from message """
        tid, name = self.get_tid(update)
        a, created = Abonent.objects.get_or_create(telegram_id=tid)
        if created:
            a.telegram_nick = name
            a.secret = BaseUserManager.make_random_password(self, length=8, allowed_chars='0123456789')
            a.last_seen = timezone.now()
            a.save()
        return a
        
    def valid_int(self, pattern, text):
        return re.search(pattern, text, flags=re.IGNORECASE) is not None

    
        
            
    def main(self, bot, update):
        """ Main dispatcher of text messages from abonent """
        a = self.abonent(update)
        print(a.state, time())
        if a:                    
            if START in a.state:
                self.start(a, update)
            elif AUTH == a.state:
                self.auth(a, update)
            elif PASS == a.state:
                self.passw(a, update)
            elif READY == a.state:                    
                self.carcheck(a, update)
                self.ready(bot, update)
            elif ACCEPTED == a.state:
                self.accepted(bot, update)
            elif LOADING == a.state:                
                self.query_load_odometer(bot, update, callback_command=r'/load_odo')
            elif LOADED == a.state:
                self.query_load_weight(bot, update, callback_command=r'/load_weight')                
            elif RACE == a.state:
                self.race(bot, update)
            elif UNLOADING == a.state:                
                self.query_unload_odometer(bot, update, callback_command=r'/unload_odo')
            elif UNLOADED == a.state:
                self.query_unload_weight(bot, update, callback_command=r'/unload_weight')                
            elif BAN == a.state:
                pass
            else:
                a.state = START             # Сброс статуса на начальный
                a.save()
    
    def get_secret_command(self, bot, update):
        a = self.abonent(update)
        if a.admin:
            data = update.message.text.split(' ')
            abn = Abonent.objects.filter(telegram_nick__iexact=data[1])
            if abn.count() > 0:
                for ab in abn:
                    update.message.reply_text(ab.telegram_nick + ':' + ab.secret)

        
    
    @staticmethod
    @receiver(post_save, sender=Race)
    def race_save_notify(sender, instance, created, **kwargs):
        """ Notifier of Race model update """
        # Нужно добавить синхронизацию статусов модели Race и статуса абонента
        abonents = Abonent.objects.filter(car_id=int(instance.car_id))    
        bot = DjangoTelegramBot.getBot()
        if len(abonents) > 0:
            if created:
                for a in abonents:
                    print('created', bot.sendMessage(str(a.telegram_id), 'Вам назначен новый рейс №' + str(instance.id_race) + '. Приступайте к следующему рейсу после завершения текущего.'))
            else:
                for a in abonents:
                    print('context', a.context)
                    if instance.state == Race.UNLOAD and a.race == instance:
                        # Если рейс выгружен (статус Race.UNLOAD), то отвязываем этот текущий рейс от абонента
                        a.race = None
                        a.state = READY
                    if a.context is not None and len(a.context) > 12:
                        query_id, exp = a.context.split(':')
                        expire = float(exp)
                        a.context = None
                        if time() < expire:
                            print('updated', bot.answerCallbackQuery(query_id, 'Рейс №' + str(instance.id_race) + ' обновлён.'))
                    a.save()
            
            

    def decimal(self, bot, update):
        """ Decimal input dispatcher """
        a = self.abonent(update)
        if PASS == a.state:
            self.passw(a, update)
        if LOADING == a.state:
            print('decimal loading')
            self.query_load_odometer(bot, update, callback_command=r'/load_odo')
        if LOADED == a.state:
            print('decimal loaded')
            self.query_load_weight(bot, update, callback_command=r'/load_weight')
        if UNLOADING == a.state:
            print('decimal unloading')
            self.query_unload_odometer(bot, update, callback_command=r'/unload_odo')
        if UNLOADED == a.state:
            print('decimal unloaded')
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
        
        
logging.basicConfig(filename=u'bot.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("Loading handlers for telegram bot")

    bot = AvtrgnBot()
    bot.start_bot()            
    