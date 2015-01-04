from django.db import models
from django.utils import timezone
from django.utils.http import urlquote
from django.core.mail import send_mail
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class UserManager(BaseUserManager):

    def _create_user(self, email, password,
                     is_staff, is_superuser, **extra_fields):

        now = timezone.now()

        if not email:
            raise ValueError('The given email must be set')

        email = self.normalize_email(email)

        user = self.model(email=email,
                          is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser, last_login=now,
                          date_joined=now, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, False, False,
                                 **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, True,
                                 **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(max_length=254, unique=True)
    is_staff = models.BooleanField(default=False, help_text='Designates whether the app_user can log into this admin site.')
    is_active = models.BooleanField(default=True, help_text='Designates whether this app_user should be treated as active. Unselect this instead of deleting accounts.')
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = 'app_user'
        verbose_name_plural = 'app_user'

    def get_absolute_url(self):
        return "/app_user/%s/" % urlquote(self.email)

    def get_full_name(self):
        full_name = '%s %s' % (self.userprofile.first_name, self.userprofile.last_name)
        return full_name.strip()

    def get_short_name(self):
        return self.userprofile.first_name

    def email_user(self, subject, message, from_email=None):
        send_mail(subject, message, from_email, [self.email])

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    title = models.CharField(max_length=30, blank=True)
    first_name = models.CharField(max_length=30, default="")
    last_name = models.CharField(max_length=30, default="")

    def __str__(self):
        return self.first_name+' '+self.last_name+' [User Profile]'
