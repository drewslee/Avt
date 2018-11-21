from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Race


@receiver(post_save, sender=Race)
def race_handler(sender, **kwargs):
    print(Race(sender))
    print('Race saved')