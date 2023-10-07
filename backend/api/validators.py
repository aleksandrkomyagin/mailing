import re

from rest_framework import serializers


def validate_telephone(value):
    if re.search(r'7\d{10}', value) is None:
        symbol = "".join(re.findall(r'[^0-9]', value))
        if symbol:
            raise serializers.ValidationError(
                f'Недопустимые символы <{symbol}> в номере.'
            )
