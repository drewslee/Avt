from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Race


@receiver(post_save, sender=Race)
def my_handler(sender, **kwargs):
    print('Race ' + str(sender.id_race) + ' saved')