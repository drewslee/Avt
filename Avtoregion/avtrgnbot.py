from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import BaseUserManager
import re
import telegram
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, Location
from telegram.ext import Updater, JobQueue, MessageHandler, CommandHandler, CallbackQueryHandler, Filters
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


# Telegram token for our bot
TOKEN = '756109523:AAGA26Apy_txLlQw7WJL9fg_YWWySEx6OkQ'
BOT_REQUEST_KWARGS={
    'proxy_url': 'socks5://bliwu.tgvpnproxy.me',
    # Optional, if you need authentication:
    'urllib3_proxy_kwargs': {
        'username': 'telegram',
        'password': 'telegram',
    }
}

# Bot status list
START, AUTH, PASS, READY, RACE, ACCEPTED, BAN = 'start', 'auth', 'pass', 'ready', 'race', 'race_accepted', 'ban'
STATE = (
    (START, 'Начало'),
    (AUTH, 'Аутентификация'),
    (PASS, 'Запрос ключа'),
    (READY, 'Готов'),
    (RACE, 'Рейс'),
    (ACCEPTED, 'Принято'),
    (BAN, 'Заблокирован'),
)

main_keyboard = [['Мои рейсы']]
race_keyboard = [[InlineKeyboardButton('Откуда', callback_data=r'/from'), 
                  InlineKeyboardButton('Куда', callback_data=r'/to')]]
                 
load_keyboard = [[InlineKeyboardButton('Загружено', callback_data=r'/loaded')]] 
unload_keyboard = [[InlineKeyboardButton('Выгружено', callback_data=r'/unloaded')]]
                  

# AvtrgnBot Телеграм-бот для коммуникации диспетчерской системы с водителями
# TO DO: Вынести строковые сообщения в константы

class AvtrgnBot():
    updater = Updater(TOKEN, request_kwargs=BOT_REQUEST_KWARGS)
    bot = updater.bot
    disp = updater.dispatcher
    job_queue = updater.job_queue
    me = bot.getMe()
    states = dict(STATE)
    number_mask = r'^[ABCEHKMOPTYXАВСЕНКМОРТУХ]\s*\d{3}\s*[ABCEHKMOPTYXАВСЕНКМОРТУХ]{2}\s*(\d{2})?$'
    number_sub_mask = r'^([ABCEHKMOPTYXАВСЕНКМОРТУХ])\s*(\d{3})\s*([ABCEHKMOPTYXАВСЕНКМОРТУХ]{2})\s*(\d{2})?$'
    messages = {
        'hello' : 'Автоматический бот-диспетчер ООО "Авторегион" приветствует Вас. Для дальнейшей работы Вам нужно авторизоваться.',
        'auth' : 'Для регистрации в системе пришлите госномер автомобиля в формате x123xy.',
        'pass'  : 'Теперь пришлите секретный ключ для подтверждения полномочий. Если он вам неизвестен, обратитесь к диспетчеру.',
        'errauth' : 'Неверный номер автомобиля. Пробуйте ещё.',
        'errpass' : 'Неверный секретный ключ. Попробуйте ещё.',
        'authok' : 'Вы авторизованы.',
        'tryout' : 'Количество попыток авторизации исчерано.',
        'banned' : 'Вам отказано в доступе.',
        'select' : 'Выберите команду',
    }

    def __init__(self):
        pass
    
    # Процедура отправки типового сообщения
    def send(self, uid, m = 'hello', **kwargs):
            self.bot.sendMessage(uid, self.messages[m])

    # Процедура движения по статусам авторизации
    def move_auth(self, abonent, msg='auth', next_state=AUTH, try_increment=1, reset_auth_car=True):
        self.send(str(abonent.telegram_id), msg)    # Отправляем сообщение
        abonent.state = next_state                  # Присваиваем следующий статус
        abonent.auth_try += try_increment
        abonent.last_seen = timezone.now()
        if reset_auth_car:
            abonent.context = None          # Сбрасываем номер автомобиля времени авторизации
        abonent.save()
        
            
    # Обработка начального статуса            
    def start(self, abon):
#        self.bot.sendMessage(str(abon.telegram_id), 'Добро пожаловать! Вам нужно авторизоваться. Для регистрации пришлите госномер автомобиля в формате x123xy (буквы латинницей)', reply_markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Auth', callback_data='/auth')]]))
#        self.move(abon, 'hello', AUTH, try_increment=0, reset_auth_car=False)
        self.send(str(abon.telegram_id))
        self.send(str(abon.telegram_id), 'auth')
        abon.state = AUTH
        abon.save()

    # Обработка запроса авторизации        --- Подумать над вопросом использования имени в телеграм в качестве номера авто при авторизации
    def auth(self, abon, upd):
        auth_fail = True
        # Проверить доступное количество попыток авторизации и при исчерпании этого лимита отправить клиента восвояси    
        if abon.auth_try < 3 and BAN not in abon.state and abon.active:     
            print('try < 3 and not banned and active')
            number = re.sub(self.number_sub_mask, r'\1 \2 \3 \4', upd.message.text.strip().upper())
            print(number)
            if re.search(self.number_mask, number, flags=re.IGNORECASE) is not None:
                # Далее нужно проверить наличие автомобиля в базе данных                 
                try:
                    print('search car by number ' + number)
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
            abon.state = STATE[0]
            abon.auth_try = 0
            abon.last_seen = timezone.now()
            abon.save()
            self.move_auth(abon)

    def callback_halfmin(self, bot, job):
        bot.sendMessage(chat_id=job.context, text='BEEP_OK')
    
    # Обработка начальной команды /start
    def start_callback(self, bot, update):
        self.bot.sendMessage(str(update.message.chat_id), 'Ваши рейсы', reply_markup = ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True))        
        self.main(bot, update)
        
            
    # Обработка статуса готовности
    def ready(self, abon, upd):
        # Отправить все текущие рейсы закрепленными сообщениями
        #race_message = self.bot.sendMessage(upd.message.chat.id, text = 'Закрепленное сообщение с информацией о рейсе')
        #self.bot.pinChatMessage(upd.message.chat.id, race_message.id)
        # Отправить inline-клавиатуру с кнопкой "Рейс"
        self.myrace(abon, upd)
#        race_keyboard = [[InlineKeyboardButton(text='🚚 '+self.states[RACE], callback_data='/' + RACE)]]
#        reply_markup = InlineKeyboardMarkup(race_keyboard)
#        self.bot.sendMessage(upd.message.chat.id, self.messages['select'], reply_markup=reply_markup)
        
    
    def race_accepted_callback(self, bot, update):
        if update.callback_query.answer():
            update.callback_query.edit_message_text(text='А теперь в путь! 🛣')
        
    
    # Отправка данных по текущему рейсу
    def race_callback(self, bot, update):
        if update.callback_query.answer():
            update.callback_query.edit_message_text(text='РЕЙС: ')
            race_accept_keyboard = [[InlineKeyboardButton(text='✅ Принято', callback_data='/race_accepted')]]
            reply_markup = InlineKeyboardMarkup(race_accept_keyboard)
            update.callback_query.edit_message_reply_markup(reply_markup=reply_markup)
            
    def from_callback(self, bot, update):
        if update.callback_query.answer():            
            pk = update.callback_query.data.split('|')[1]
            print('pk = ' + pk)
            race = Race.objects.get(pk=pk)
            bot.sendVenue(update.callback_query.from_user.id, 51.2875544, 58.4370285, 'Место погрузки', race.get_load_place, reply_markup=InlineKeyboardMarkup(load_keyboard))
    
    def to_callback(self, bot, update):
        if update.callback_query.answer():            
            pk = update.callback_query.data.split('|')[1]
            print('pk = ' + pk)
            race = Race.objects.get(pk=pk)
            bot.sendVenue(update.callback_query.from_user.id, 51.6089419,52.9732831, 'Место разгрузки', race.get_unload_place, reply_markup=InlineKeyboardMarkup(unload_keyboard)) 
        
    
    def myrace(self, abon, update):
        races = Race.objects.filter(car_id=abon.car.id_car).order_by('race_date').reverse()
        text = ''
        if races.count() == 0:            
            self.bot.sendMessage(str(abon.telegram_id), 'Активные рейсы отсутствуют.', reply_markup = ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True))
        else:
            r = races[:1][0]
            print(r)
            text += u'<b>Номер рейса:</b> ' + str(r.id_race) + u'\n' + \
                    u'<b>Дата рейса:</b> ' + str(r.race_date) + u'\n' + \
                    u'<b>Откуда:</b> ' + r.get_load_place + u'\n'  + \
                    u'<b>Куда:</b> ' + r.get_unload_place + u'\n'
            for rk in race_keyboard[0]:
                rk.callback_data += '|' + str(r.id_race)
#            [0].callback_data += '|' + str(r.id_race)
#            race_keyboard[0][1].callback_data += '|' + str(r.id_race)
            self.bot.sendMessage(str(abon.telegram_id), text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(race_keyboard))
    
    # Главный обработчик сообщений от абонента
    def main(self, bot, update):
        msg = update.message
        print(msg.text)
        abonents = Abonent.objects.filter(telegram_id=int(msg.chat_id))  # Выборка абонентов из базы по telegram_id. 
        if abonents.count() == 0:
            # Абонент не найден, добавляем в базу
            a = Abonent(telegram_id=int(msg.chat_id), 
                        telegram_nick=msg.chat.first_name, 
                        secret=BaseUserManager.make_random_password(self, length=8, allowed_chars='0123456789'), 
                        last_seen=timezone.now())
            a.save()
        elif abonents.count() == 1:
            # Абонент найден, далее работаем с ним
            a = abonents[0]
        else:
            # Абонентов с указанным telegram_id найдено более одного -> непорядок!
            logging.critical(u'Более одного абонента с telegram_id: ' + str(msg.chat_id))
        
        if START in a.state:
            self.start(a)
        elif AUTH in a.state:
            self.auth(a, update)
        elif PASS in a.state:
            self.passw(a, update)
        elif READY in a.state:
            self.carcheck(a, update)
            self.ready(a, update)
        elif RACE in a.state:
            self.myrace(a, update)
        elif BAN in a.state:
            pass
        else:
            a.state = STATE[0]             # Сброс статуса на начальный
            a.last_seen = timezone.now()   # Записываем время последнего соединения с абонентом
            a.save()

    
    
    def __str__(self):
        return '{}:{}'.format(self.me['id'], self.me['username'])
        
    def start_bot(self):
#        a = Abonent.objects.get(telegram_id=0)  # Выборка абонента из базы по telegram_id 
        self.disp.add_handler(CommandHandler('start', self.start_callback))
        self.disp.add_handler(CallbackQueryHandler(self.race_callback, pattern=r'/race$'))
        self.disp.add_handler(CallbackQueryHandler(self.from_callback, pattern=r'/from'))
        self.disp.add_handler(CallbackQueryHandler(self.to_callback, pattern=r'/to'))
        self.disp.add_handler(CallbackQueryHandler(self.race_accepted_callback, pattern=r'/race_accepted$'))
        self.disp.add_handler(MessageHandler(Filters.text, self.main))
        self.updater.start_polling()
#        self.updater.idle()
        return 'ok'

        
if __name__ == '__main__':
    logging.basicConfig(filename=u'bot.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    b = AvtrgnBot()    
    b.start_bot()