from datetime import timedelta
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
from telegram.ext import Filters

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


BOT_REQUEST_KWARGS={
    'proxy_url': 'socks5://bliwu.tgvpnproxy.me',
    # Optional, if you need authentication:
    'urllib3_proxy_kwargs': {
        'username': 'telegram',
        'password': 'telegram',
    }
}

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
race_accept_keyboard = [[InlineKeyboardButton('Приступить', callback_data=r'/race_accepted')]]                 
loading_keyboard = [[InlineKeyboardButton('Погрузка', callback_data=r'/loading')]] 
unload_keyboard = [[InlineKeyboardButton('Выгрузка', callback_data=r'/unloaded')]]
confirm_keyboard = [[InlineKeyboardButton('Да', callback_data=r'/yes'), InlineKeyboardButton('Нет', callback_data=r'/no')]] 
close_kb = [[InlineKeyboardButton('Закрыть', callback_data=r'/close')]]
            
keyboards = {READY: race_accept_keyboard, ACCEPTED: loading_keyboard }            

# AvtrgnBot Телеграм-бот для коммуникации диспетчерской системы с водителями
# TO DO: Вынести строковые сообщения в константы

TELEGRAM = Updater(djangoSettings.TOKEN, request_kwargs=BOT_REQUEST_KWARGS)

class AvtrgnBot():
    #updater = TELEGRAM
    #bot = updater.bot
    #disp = updater.dispatcher
    #job_queue = updater.job_queue
    #me = bot.getMe()
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
        self.updater = TELEGRAM
        self.bot = self.updater.bot
        self.disp = self.updater.dispatcher
        self.job_queue = self.updater.job_queue
        self.me = self.bot.getMe()
        
    
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
    
    def status(self, abonent, state, context=None):
        #st = [s[0] for s in STATE]
        if context is not None:
            abonent.context = context
        abonent.state = state #st[st.index(abonent.state)-1]
        abonent.save()
            
    # Обработка начального статуса            
    def start(self, abon):
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
        self.bot.sendMessage(str(update.message.chat_id), 
                             'Ваши рейсы', 
                             reply_markup = ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True))        
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
            a = self.abonent(update)
            if a.context is not None and len(a.context):
                race = Race.objects.get(pk=int(a.context))
                a.race = race
            else:
                race = a.race
            a.state = ACCEPTED
            a.context = None
            a.save()
            race.race_date = timezone.now()
            race.save()
            kb = keyboards[a.state]
            #kb.callback_data += '|' + str(a.race_id)
            text = u'Направляйтесь к месту погрузки.'
            update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb))
        
    
    # Отправка данных по текущему рейсу
    def race_callback(self, bot, update):
        if update.callback_query.answer():
            update.callback_query.edit_message_text(text='РЕЙС: ')
#            race_accept_keyboard = [[InlineKeyboardButton(text='✅ Принято', callback_data='/race_accepted')]]
            reply_markup = InlineKeyboardMarkup(race_accept_keyboard)
            update.callback_query.edit_message_reply_markup(reply_markup=reply_markup)
            
    def from_callback(self, bot, update):
        if update.callback_query.answer():            
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
    
    def to_callback(self, bot, update):
        if update.callback_query.answer():            
            pk = update.callback_query.data.split('|')[1]
            print('pk = ' + pk)
            race = Race.objects.get(pk=pk)
            bot.sendVenue(update.callback_query.from_user.id, 
                          51.6089419, 52.9732831, 
                          'Место разгрузки', 
                          race.get_unload_place, 
                          reply_markup=InlineKeyboardMarkup(unload_keyboard)) 
        
    def loading_callback(self, bot, update):
        if update.callback_query.answer():
            a = self.abonent(update)
            a.state = LOADING
            a.save()
            bot.delete_message(chat_id=update.callback_query.message.chat.id, 
                               message_id=update.callback_query.message.message_id)
            bot.sendMessage(update.callback_query.from_user.id, 
                            'Ваш рейс в состоянии погрузки. Введите показания одометра авто ' + a.race.car.number + ' на момент погрузки:', 
                            reply_markup=ForceReply(force_reply=True))    
    
    def yes_callback(self, bot, update):
        if update.callback_query.answer():
            a = self.abonent(update)
            a.race.s_milage = int()
        pass
        
    def no_callback(self, bot, update):
        if update.callback_query.answer():
            a = self.abonent(update)
            if LOADING in a.state:
                self.status(a, ACCEPTED, a.context)
            self.main(bot, update)
            bot.delete_message(chat_id=update.callback_query.message.chat.id, 
                               message_id=update.callback_query.message.message_id)
    
    def confirmation_load_callback(self, bot, update):
        """ Confirmation of loaded amount input """
        
        pass
        
    def close_callback(self, bot, update):
        if update.callback_query.answer():
            print(update)
            bot.delete_message( chat_id=update.callback_query.message.chat.id, 
                                message_id=update.callback_query.message.message_id)
    
    def get_keyboard(self, abon):
        return keyboards[abon.state]
    
    def get_race_context(self, abon):
        """ Get current race id and race object from abonent context """
        current_race_id = 0        
        current_race = None
        context = []
        
        # Если контекст содержит номер текущего рейса, то получаем его из контекста
        if abon.context:
            context = abon.context.split()            
            if len(context):
                current_race_id = int(context[0])        
                if current_race_id:
                    current_race = Race.objects.get(pk=current_race_id)
            
        return (current_race_id, current_race)    
        
    
    def current_race(self, abon, update):
        """ Sending info about current race """
        if abon.race_id is None:
            # Если рейс не привязан, значит получаем его из контекста
            r_id, r = self.get_race_context(abon)
        else:
            r = abon.race
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
        
        self.bot.sendMessage(str(abon.telegram_id), 
                             text,
                             parse_mode='HTML',
                             reply_markup=InlineKeyboardMarkup(kb))       
        
    def future_race(self, abon, update, send=False):
        """ Get future and current race for the abonent """ 
        # Получаем номер теекущего рейса и его объект из контекста
        current_race_id, current_race = self.get_race_context(abon)
        
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
            text += u'<pre>Номер | Дата             | Водитель</pre>'
            text += u'<pre>—————————————————————————————————————————————</pre>'
            for r in future_races:
                text += u'<pre>' + str(r.id_race).rjust(5, ' ') 
                text += u' | ' + r.race_date.strftime('%d.%m.%Y %H:%M')
                text += u' | ' + r.driver.name + u'</pre>\n'                
            text += u'<pre>‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾</pre>\n'
            self.bot.sendMessage(str(abon.telegram_id), text, parse_mode='HTML')
                
        if current_race is None and current_race_id != 0:
            current_race = Race.objects.get(pk=current_race_id)
        
        if current_race_id != 0:
            # Сохраняем номер текущего рейса в контекст
            if abon.context is None:
                abon.context = str(current_race_id)
                abon.save()
        else:
            self.bot.sendMessage(str(abon.telegram_id), u'У вас нет назначенных рейсов.', reply_markup = ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True))            
        
    
    def myrace(self, abon, update):
        self.future_race(abon, update)
        self.current_race(abon, update)
        pass
                            
    
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
    
    def odometer(self, abon, update):
        """ Process odometer value """
        tid, name = self.get_tid(update)
        if re.search(r'^\d+$', update.message.text.strip(), flags=re.IGNORECASE) is not None:
            self.bot.sendMessage(tid, r'Введенное показание одометра: <b>'+update.message.text+'</b> км. Всё верно?', parse_mode='HTML', reply_markup=InlineKeyboardMarkup(confirm_keyboard))
        else:
            self.bot.sendMessage(tid, 'Показания одометра введены с ошибкой. Введите правильно:', reply_markup=ForceReply(force_reply=True))    
    
        pass
        
    def loaded(self, abon, update):
        """ Process loaded amount """
        tid, name = self.get_tid(update)
        if re.search(r'^\d+$', update.message.text.strip(), flags=re.IGNORECASE) is not None:
            print(int(update.message.text))
            self.bot.sendMessage(tid, r'Введенный вес: <b>'+update.message.text+'</b> кг. Всё верно?', parse_mode='HTML', reply_markup=InlineKeyboardMarkup(confirm_keyboard))
        else:
            self.bot.sendMessage(tid, 'Вес введён с ошибкой. Введите загруженный вес в килограммах:', reply_markup=ForceReply(force_reply=True))    
    
    def main(self, bot, update):
        """ Main dispatcher of text messages from abonent """
        a = self.abonent(update)
        if a:
            if START in a.state:
                self.start(a)
            elif AUTH in a.state:
                self.auth(a, update)
            elif PASS in a.state:
                self.passw(a, update)
            elif READY in a.state:
                abn = Abonent.objects.filter(telegram_nick__iexact=update.message.text)
                if abn.count() == 1:
                    self.bot.sendMessage(int(update.message.chat_id), abn[0].secret)
                    
                self.carcheck(a, update)
                self.ready(a, update)
            elif ACCEPTED in a.state:
                self.myrace(a, update)
            elif RACE in a.state:
                self.myrace(a, update)
            elif LOADING in a.state:                
                self.odometer(a, update)
            elif LOADED in a.state:
                self.loaded(a, update)
            elif BAN in a.state:
                pass
            else:
                a.state = START             # Сброс статуса на начальный
                a.save()
    
    
    def __str__(self):
        return '{}:{}'.format(self.me['id'], self.me['username'])
    
    
    @staticmethod
    @receiver(post_save, sender=Race)
    def race_save_notify(sender, instance, created, **kwargs):
        # get the instance of AvtrgnBot to use bot property ...
        a = Abonent.objects.get(car_id=int(instance.car_id))
        TELEGRAM.bot.sendMessage(int(a.telegram_id), 'Race ' + str(instance.id_race) + ' updated')
        print('Race ' + str(instance.id_race) + ' updated')
        pass

    def decimal(self, bot, update):
        a = self.abonent(update)
        if LOADING in a.state:
            self.odometer(a, update)
        print('decimal = ', update.message.text)
    
    def start_bot(self):
        #disp = TELEGRAM.dispatcher
        #print(self.disp)
        if not self.updater.running:
            self.disp.add_handler(CommandHandler('start', self.start_callback))
            self.disp.add_handler(CallbackQueryHandler(self.race_callback, pattern=r'/race$'))
            self.disp.add_handler(CallbackQueryHandler(self.from_callback, pattern=r'/from'))
            self.disp.add_handler(CallbackQueryHandler(self.to_callback, pattern=r'/to'))
            self.disp.add_handler(CallbackQueryHandler(self.loading_callback, pattern=r'/loading'))
            self.disp.add_handler(CallbackQueryHandler(self.race_accepted_callback, pattern=r'/race_accepted'))
            self.disp.add_handler(CallbackQueryHandler(self.confirmation_load_callback, pattern=r'/confirmation$'))
            self.disp.add_handler(CallbackQueryHandler(self.close_callback, pattern=r'/close$'))
            self.disp.add_handler(CallbackQueryHandler(self.yes_callback, pattern=r'/yes$'))
            self.disp.add_handler(CallbackQueryHandler(self.no_callback, pattern=r'/no$'))
            self.disp.add_handler(MessageHandler(Filters.regex(r'^\d+$'), self.decimal))
            self.disp.add_handler(MessageHandler(Filters.text, self.main))
            self.updater.start_polling()
        return 'ok'

        
if __name__ == '__main__':
    logging.basicConfig(filename=u'bot.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    # b = AvtrgnBot()    
    # b.start_bot()