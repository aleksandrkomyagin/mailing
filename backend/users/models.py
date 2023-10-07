import uuid
import random
import string

from django.contrib.auth.models import AbstractUser
from django.db import models

from mailing.settings import (CONFIRMATION_CODE_MAX_LENGHT, EMAIL_MAX_LENGHT,
                              MAX_LENGHT, USERNAME_MAX_LENGHT)
from .validators import validate_username

USER = 'user'
ADMIN = 'admin'
MODERATOR = 'moderator'

ROLE_CHOICES = [
    (USER, USER),
    (ADMIN, ADMIN),
    (MODERATOR, MODERATOR)
]


class User(AbstractUser):
    first_name = models.CharField(
        max_length=MAX_LENGHT,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=MAX_LENGHT,
        verbose_name='Фамилия'
    )
    username = models.CharField(
        validators=(validate_username,),
        max_length=USERNAME_MAX_LENGHT,
        unique=True,
        verbose_name='Юзернейм'
    )
    email = models.EmailField(
        max_length=EMAIL_MAX_LENGHT,
        unique=True,
        verbose_name='Почта'
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=USER,
        verbose_name='Роль'
    )

    confirmation_code = models.UUIDField(
        unique=True,
        max_length=CONFIRMATION_CODE_MAX_LENGHT,
        null=False,
        blank=False,
        verbose_name='Код подтверждения'
    )

    def save(self, *args, **kwargs):
        self.confirmation_code = uuid.uuid4()
        password = self.set_password()
        super(User, self).save(*args, **kwargs)
        self.send_password_and_confirmation_code(
            password, self.confirmation_code)

    def set_password(self, raw_password=None):
        if raw_password is None:
            raw_password = ''.join(random.choices(
                string.ascii_letters + string.digits, k=8))
        super().set_password(raw_password)
        return raw_password

    def send_password_and_confirmation_code(self, password, confirmaton_code):
        from api.tasks import send_password_task
        send_password_task.apply_async(
            args=[self.email, password, confirmaton_code])

    @property
    def is_admin(self):
        return bool(
            self.is_superuser
            or self.role == ADMIN
            or self.is_staff
        )

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
