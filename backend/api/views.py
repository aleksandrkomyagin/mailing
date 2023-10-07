from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from rest_framework import mixins, permissions, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from .models import Client, Mailing
from .pagination import LimitPagePagination
from .serializers import (ChangePasswordSerializer, ClientSerializer,
                          GetStatMailings, MailingSerializer,
                          UserConfirmationCodeSerializer, UserSerializer,
                          UserTokenSerializer)
from .tasks import send_report_task

User = get_user_model()


class GetConfirmationCodeView(views.APIView):
    serializer_class = UserConfirmationCodeSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializers = UserConfirmationCodeSerializer(data=request.data)
        serializers.is_valid(raise_exception=True)
        username = serializers.validated_data.get('username')
        email = serializers.validated_data.get('email')
        user_by_username = User.objects.filter(username=username).first()
        user_by_email = User.objects.filter(email=email).first()
        if user_by_username != user_by_email:
            field_name = 'username' if user_by_username else 'email'
            return Response(
                {'Ошибка': f'Пользователь с '
                 f'введенным {field_name} существует!'},
                status=status.HTTP_400_BAD_REQUEST)
        target_user, _ = User.objects.get_or_create(
            username=username, email=email
        )
        return Response(serializers.data)


class GetTokenView(views.APIView):
    serializer_class = UserTokenSerializer
    permission_classes = (permissions.AllowAny, )

    def post(self, request):
        serializer = UserTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        user = get_object_or_404(User, username=username)
        code = user.confirmation_code
        if serializer.validated_data.get('confirmation_code') == str(code):
            token = AccessToken.for_user(user)
            return Response({'token': str(token)},
                            status=status.HTTP_200_OK)
        return Response(
            {'confirmation_code': 'Неверный код подтверждения!'},
            status=status.HTTP_400_BAD_REQUEST
        )


class UserViewSet(mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    search_fields = ('username', 'email')
    pagination_class = LimitPagePagination

    @action(
        detail=False, methods=['get'],
        permission_classes=(permissions.IsAuthenticated,),
        url_path='me'
    )
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'],
            permission_classes=(permissions.IsAuthenticated,),
            url_path='set_password')
    def set_password(self, request):
        serializer = ChangePasswordSerializer(request.user, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response('Пароль успешно изменен!',
                        status=status.HTTP_204_NO_CONTENT)


class ClientViewset(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    search_fields = ('email', )
    pagination_class = LimitPagePagination
    permission_classes = (permissions.IsAuthenticated, )


class MailingViewset(viewsets.ModelViewSet):
    queryset = Mailing.objects.all()
    serializer_class = MailingSerializer
    permission_classes = (permissions.IsAuthenticated, )

    @action(
        detail=False,
        methods=['get'],
        pagination_class=LimitPagePagination,
        permission_classes=(permissions.IsAuthenticated, )
    )
    def get_stat_all_mailings(self, request):
        mail = Mailing.objects.annotate(
            total_mail=Count('mail_mailing'),
            total_sent_mail=Count('mail_mailing__status',
                                  filter=Q(mail_mailing__status=True)))
        pages = self.paginate_queryset(mail)
        serializer = GetStatMailings(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['get'],
        pagination_class=LimitPagePagination,
        permission_classes=(permissions.IsAuthenticated, )
    )
    def get_stat_mailing(self, request, pk):
        mail = Mailing.objects.annotate(
            total_mail=Count('mail_mailing'),
            total_sent_mail=Count('mail_mailing__status',
                                  filter=Q(mail_mailing__status=True))
        ).get(id=pk)
        serializer = GetStatMailings(
            mail,
            context={'request': request}
        )
        send_report_task()
        return Response(serializer.data, status=status.HTTP_200_OK)
