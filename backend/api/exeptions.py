from rest_framework.exceptions import APIException


class CustomExeption(APIException):
    status_code = 400
    default_detail = 'Клиенты с подходящим интервалом не найдены!'
