from django.apps import AppConfig
from django.db.models.signals import post_save
from django.dispatch import receiver

class AvtoregionConfig(AppConfig):
    name = 'Avtoregion'
    verbose_name = 'Авторегион (Диспетчер)'
    
    def ready(self):
        from .models import Race
        #from .avtrgnbot import AvtrgnBot
        
        #bot = AvtrgnBot()
        #bot.start_bot()
        
        
        # Registering post_save signal for Race update and sending notification by AvtrgnBot
        #post_save.connect(bot.race_save_notify, sender=Race)
