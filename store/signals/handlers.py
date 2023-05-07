from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from store.models import Customer


User = get_user_model()

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Customer.objects.create(user=instance)