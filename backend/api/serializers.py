import django.contrib.auth.password_validation as validator
from django.contrib.auth import get_user_model
from rest_framework import serializers

from mailing.settings import (CONFIRMATION_CODE_MAX_LENGHT, EMAIL_MAX_LENGHT,
                              USERNAME_MAX_LENGHT)
from .models import Client, Code, Mail, Mailing, Tag
from .utils import create_task_to_send_mailing
from users.validators import validate_username

User = get_user_model()


class UserConfirmationCodeSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=USERNAME_MAX_LENGHT,
        required=True,
        validators=[validate_username]
    )
    email = serializers.EmailField(
        max_length=EMAIL_MAX_LENGHT,
        required=True
    )


class UserTokenSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=USERNAME_MAX_LENGHT,
        required=True,
        validators=[validate_username]
    )
    confirmation_code = serializers.CharField(
        max_length=CONFIRMATION_CODE_MAX_LENGHT,
        required=True
    )


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id', 'first_name', 'last_name', 'username',
            'email', 'role'
        )


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField()
    new_password = serializers.CharField()

    def validate_new_password(self, new_password):
        validator.validate_password(new_password)
        return new_password

    def update(self, instance, validated_data):
        if not instance.check_password(validated_data['current_password']):
            raise serializers.ValidationError(
                'Неправильный текущий пароль.'
            )
        if (validated_data['current_password']
           == validated_data['new_password']):
            raise serializers.ValidationError(
                'Новый пароль должен отличаться от текущего.'
            )
        instance.set_password(validated_data['new_password'])
        return validated_data


class ClientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Client
        fields = '__all__'


class MailingSerializer(serializers.ModelSerializer):
    tag_filter = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
    )
    code_mobile_operator_filter = serializers.PrimaryKeyRelatedField(
        queryset=Code.objects.all(),
        required=False,
    )

    class Meta:
        model = Mailing
        fields = (
            'id', 'start_time', 'end_time',
            'tag_filter', 'text',
            'code_mobile_operator_filter',
            'time_zone',
        )

    @staticmethod
    def create_mail_function(mailing, clients):
        clients = [Mail(mailing=mailing, client=client) for client in clients]
        Mail.objects.bulk_create(clients)

    def create(self, validated_data):
        mailing = Mailing.objects.create(**validated_data)
        # create_task_to_send_mailing возвращает список отобранных клиентов
        clients = create_task_to_send_mailing(mailing)
        self.create_mail_function(mailing, clients)
        return mailing


class GetClientsIDSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = Client
        fields = ('id',)

    def to_representation(self, instance):
        return instance.id


class GetStatMailings(serializers.ModelSerializer):
    id = serializers.IntegerField()
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    tag_filter = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all())
    code_mobile_operator_filter = serializers.PrimaryKeyRelatedField(
        queryset=Code.objects.all()
    )
    time_zone = serializers.CharField()
    text = serializers.CharField()
    total_mail = serializers.IntegerField()
    total_sent_mail = serializers.IntegerField()
    clients = serializers.SerializerMethodField()

    class Meta:
        model = Mailing
        fields = (
            'id', 'start_time', 'end_time', 'tag_filter',
            'code_mobile_operator_filter', 'time_zone', 'text',
            'total_mail', 'total_sent_mail', 'clients'
        )

    def get_clients(self, obj):
        clients = Client.objects.filter(mail_client__mailing=obj)
        serializer = GetClientsIDSerializer(clients, many=True, read_only=True)
        return serializer.data
