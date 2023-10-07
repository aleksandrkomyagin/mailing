from django.db import models

from mailing.settings import EMAIL_MAX_LENGHT, MAX_LENGHT
from .validators import validate_telephone


class Tag(models.Model):
    tag = models.CharField(
        max_length=20,
        verbose_name='Тег',
        unique=True
    )

    def __str__(self):
        return self.tag


class Code(models.Model):
    code = models.CharField(
        max_length=4,
        verbose_name='Код оператора',
        unique=True
    )

    def __str__(self):
        return self.code


class Client(models.Model):
    first_name = models.CharField(
        max_length=MAX_LENGHT,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=MAX_LENGHT,
        verbose_name='Фамилия'
    )
    telephone = models.CharField(
        max_length=15,
        verbose_name='Номер телефона',
        unique=True,
        validators=[validate_telephone],
    )
    email = models.EmailField(
        max_length=EMAIL_MAX_LENGHT,
        verbose_name='Почта'
    )
    tag = models.ForeignKey(
        Tag, on_delete=models.CASCADE,
        verbose_name='Тег'
    )
    code_mobile_operator = models.ForeignKey(
        Code,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name='Код мобильного оператора'
    )
    time_zone = models.CharField(
        max_length=2,
        verbose_name='Часовой пояс'
    )
    when_add = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Время добавления клиента')
    start_sending = models.TimeField()
    end_sending = models.TimeField()

    class Meta:
        ordering = ('last_name', 'first_name')

    def __str__(self):
        return f'Клиент {self.first_name} {self.last_name}'


class Mailing(models.Model):
    text = models.TextField(verbose_name='Текст письма')
    tag_filter = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='tag_filter',
        verbose_name='Фильтр по тегу'
    )
    code_mobile_operator_filter = models.ForeignKey(
        Code,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='code_filter',
        verbose_name='Фильтр по коду оператора'
    )
    start_time = models.DateTimeField(verbose_name='Старт рассылки')
    end_time = models.DateTimeField(verbose_name='Конец рассылки')
    time_zone = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        verbose_name='Часовой пояс'
    )

    def __str__(self):
        if self.tag_filter and self.code_mobile_operator_filter:
            return (
                f'Рассылка №{self.id} - '
                f'фильтр ({self.tag_filter} и '
                f'{self.code_mobile_operator_filter}) - '
                f'старт [{self.start_time}]')
        else:
            return (
                f'Рассылка №{self.id} - фильтр ({self.tag_filter} '
                f'и {self.code_mobile_operator_filter}) -'
                f' старт [{self.start_time}]') if self.tag_filter else (
                f'Рассылка №{self.id} - фильтр ({self.tag_filter} и'
                f' {self.code_mobile_operator_filter}) - '
                f'старт [{self.start_time}]')


class Mail(models.Model):
    create_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания письма'
    )
    status = models.BooleanField(
        default=False,
        verbose_name='Статус отправки'
    )
    mailing = models.ForeignKey(
        Mailing,
        on_delete=models.CASCADE,
        related_name='mail',
        related_query_name='mail_mailing',
        verbose_name='Рассылка, в которой отправляется письмо'
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='mail',
        related_query_name='mail_client',
        verbose_name='Клиент, которому отправилось письмо'
    )

    class Meta:
        ordering = ('create_date', 'status')
