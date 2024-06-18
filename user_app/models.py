from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import logging

logger = logging.getLogger(__name__)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)  # Replace CloudinaryField with ImageField
    about = models.TextField(blank=True)

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_or_update_profile(sender, instance, created, **kwargs):
    if created:
        try:
            Profile.objects.create(user=instance)
        except Exception as e:
            logger.error(f"Error creating profile for user {instance.username}: {e}")
    else:
        try:
            instance.profile.save()
        except Profile.DoesNotExist:
            try:
                Profile.objects.create(user=instance)
            except Exception as e:
                logger.error(f"Error creating profile for user {instance.username} after DoesNotExist exception: {e}")
        except Exception as e:
            logger.error(f"Error saving profile for user {instance.username}: {e}")

class Message(models.Model):
    user_message = models.CharField(max_length=200)
    bot_response = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_message} - {self.bot_response}"

class Subscription(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
