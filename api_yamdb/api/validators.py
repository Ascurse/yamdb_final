from datetime import datetime

from django.core.exceptions import ValidationError


def validate_year(year):
    current_year = datetime.now().year
    if year > current_year:
        raise ValidationError(
            'Год создания произведения не должен быть больше,'
            f'чем {current_year}!'
        )
