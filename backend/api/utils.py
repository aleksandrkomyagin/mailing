from datetime import datetime, timedelta

from django.db.models import Q
from rest_framework import serializers, status

from .exeptions import CustomExeption
from .models import Client
from .tasks import send_email_task


def get_clients(mailing):
    if mailing.code_mobile_operator_filter:
        clients = Client.objects.filter(
            tag=mailing.tag_filter,
            code_mobile_operator=mailing.code_mobile_operator_filter
        )
    else:
        clients = Client.objects.filter(tag=mailing.tag_filter)
    if mailing.time_zone:
        clients = clients.filter(time_zone=mailing.time_zone)
    clients = clients.filter(Q(start_sending__lte=mailing.start_time)
                             & Q(end_sending__gte=mailing.start_time)
                             & Q(end_sending__lte=mailing.end_time))
    if len(clients) > 0:
        return clients
    raise CustomExeption()


def create_task_to_send_mailing(mailing):
    left = mailing.start_time.strftime('%Y-%m-%d %H:%M:%S')
    right = mailing.end_time.strftime('%Y-%m-%d %H:%M:%S')
    if left <= datetime.now().strftime('%Y-%m-%d %H:%M:%S') <= right:
        clients = get_clients(mailing)
        recipient_list = [client.email for client in clients]
        send_email_task.apply_async(args=[mailing.id, recipient_list])
    elif left > datetime.now().strftime('%Y-%m-%d %H:%M:%S'):
        clients = get_clients(mailing)
        recipient_list = [client.email for client in clients]
        eta = mailing.start_time
        expires = mailing.start_time + timedelta(minutes=10)
        send_email_task.apply_async(
            args=[mailing.id, recipient_list],
            eta=eta,
            expires=expires
        )
    else:
        raise serializers.ValidationError(
            'Начало рассылки не может быть в прошедшем времени!',
            code=status.HTTP_400_BAD_REQUEST
        )
    return clients
