from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    # Optional fields
    mood = models.CharField(max_length=50, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    def __str__(self):
        return self.email
from django.db import models
from django.conf import settings
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

class Meeting(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    reminder_scheduled = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.title} ({self.start_time} - {self.end_time})"
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)  # Save to get ID if new

        if is_new or not self.reminder_scheduled:
            self.schedule_reminder()

    def schedule_reminder(self):
        from .tasks import send_meeting_reminder_email

        # Ensure start_time is timezone-aware
        start_time_aware = timezone.localtime(self.start_time)

        reminder_time = start_time_aware - timedelta(minutes=15)

        if reminder_time > timezone.localtime():
            send_meeting_reminder_email.apply_async(
                args=[self.id],
                eta=reminder_time  # ⬅️ exact scheduled time
            )
            self.reminder_scheduled = True
            Meeting.objects.filter(pk=self.pk).update(reminder_scheduled=True)
