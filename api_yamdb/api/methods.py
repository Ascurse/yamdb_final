import jwt

from api_yamdb.settings import SECRET_KEY


def get_user_role(token):
    """Извлекает роль из токена, без обращения к базе."""
    data = jwt.decode(
        jwt=str(token),
        key=SECRET_KEY,
        algorithms=['HS256']
    )
    role = data.get('role')
    return role


def decode(code):
    return jwt.decode(
        jwt=code,
        key=SECRET_KEY,
        algorithms=['HS256']
    )


def text_processor(text, length):
    """Оставляет указанное количество предложений текста."""
    processored_text = text.split('. ')
    if len(processored_text) <= length:
        return text
    else:
        post_text1 = '. '.join((processored_text)[:length])
        brief_text = post_text1 + '... <есть продолжение>'
        return brief_text
