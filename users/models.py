from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField('شماره تلفن', max_length=15, blank=True)
    address = models.TextField('آدرس', blank=True)
    postal_code = models.CharField('کد پستی', max_length=10, blank=True)
    city = models.CharField('شهر', max_length=100, blank=True)
    state = models.CharField('استان', max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"پروفایل {self.user.username}"

# ایجاد و ذخیره خودکار پروفایل
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()