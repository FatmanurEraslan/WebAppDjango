from django.db import models
import hashlib
from datetime import datetime, timedelta
from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, UserManager, PermissionsMixin
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError('User must have an email')

        user = self.model(
            email=self.normalize_email(email),

        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None):
        user = self.create_user(
            email=email,
            username=username,
            password=password,
            is_superuser=True,

        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=200, unique=True, verbose_name='Email')
    username = models.CharField(max_length=150, verbose_name='Username')
    first_name = models.CharField(max_length=150, verbose_name='First Name')
    last_name = models.CharField(max_length=150, verbose_name='Last Name')
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now=True)
    date_joined = models.DateTimeField(auto_now=True)
    email_confirmed = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'email_confirmed']
    objects = UserManager()

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def is_email_confirmed(self):
        # The user is identified by their email address
        return self.email_confirmed

    def __str__(self):
        return self.email

    # this methods are require to login super user from admin pan<el
    def has_perm(self, perm, obj=None):
        return self.is_admin

    # this methods are require to login super user from admin panel
    def has_module_perms(self, app_label):
        return self.is_admin

    class Meta:
        verbose_name = ('user')
        verbose_name_plural = ('users')


class EmailConfirmed(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    activation_key = models.CharField(max_length=500)
    date_created = models.DateTimeField(auto_now_add=True)
    email_confirmed = models.BooleanField(default=False)
    date_confirmed = models.DateTimeField(null=True, auto_now=True)

    def __str__(self):
        return self.user.email

    class Meta:
        verbose_name_plural = 'User Email Confirmed'


@receiver(post_save, sender=CustomUser)
def create_user_email_confirmation(sender, instance, created, **kwargs):
    if created:
        dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        email_confirmed_instance = EmailConfirmed(user=instance)
        user_encoded = f'{instance.email}-{dt}'.encode()
        activation_key = hashlib.sha224(user_encoded).hexdigest()
        email_confirmed_instance.activation_key = activation_key
        email_confirmed_instance.save()
