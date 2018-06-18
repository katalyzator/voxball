# -*- coding: utf-8 -*-
BAD_REQUEST = u'Bad request'
MISSING_REQUIRED_PARAMS = u'Отсутсвуют обязательные поля: {0}'
BAD_EMAIL = u'Неправильный формат email адреса, email: {0}'
PASSWORD_LENGTH_ERROR = u'Длина пароля должна быть не меньше 6, найдено: {0}'
USERNAME_USED = u'Пользователь с таким email-ом уже существует'
USER_NOT_FOUND_EMAIL = u'Пользователь с таким email отсутсвует'
INCORRECT_USERNAME_OR_PASSWORD = u'Имя или пароль неверные'
USER_NOT_VERIFIED = u'Пользователь должен авторизоваться перед входом'
INCORRECT_HTTP_METHOD = u'Неправильный метод http'
INCORRECT_CURRENT_PASSWORD = u'Введен неправильный пароль'
WRONG_AVATAR_FORMAT = u'Неправильный формат изображения'
EMAIL_ACTIVATED = u'Данный пользователь уже активировал свой email'
PERMISSION_DENIED = u'Отказано в доступе'
TOKEN_INVALID = u'Неправильный токен'
ANSWERED_POLL = u'Данный пользователь уже проголосовал на этот опрос'
RESET_CODE_NOT_FOUND = u'Код деактивации неактивен'
POLL_NOT_FOUND = u"Опрос не найден"
PHONE_INCORRECT = u'Неправильный номер телефона'
ACTIVATION_CODE_NOT_FOUND = u'Код активации не найден'
ACTIVATION_TIME_EXPIRED = u'Время активации истекло'
CATEGORY_NOT_FOUND = u'Категория не найдена'
USER_ALREADY_HAS_PASSWORD = u'У пользователя уже есть пароль'
CATEGORIES_DOESNT_MATCH = u'Категории не найдены'
INVALID_PARAMETERS = u"Неправильные данные в параметрах"
INVALID_POLL_TYPE = u"Неправильный тип опроса"
INVALID_DATES = u"Неправильные даты"
SC_COUNT_INVALID = u"Количество ответов должно быть минимум 1"
REGISTRATION_COMPLETION = u"Пожалуйста завершите регистрацию"
EMAIL_ACTIVATION = u'Пожалуйста завершите активацию email-а'
POLL_CHOICE_NOT_FOUND = u'Ошибка сервера. Ответ не найден'
FB_OAUTH_TOKEN_INVALID = u'Неправильный facebook token'
EMAIL_SERVICE_ERROR = u'Ошибка сервера. Email не отправлен'
SUCCESFULLY_SEND_RESET_LINK = u'Ссылка на сброс пароля успешно отправлена на почту'
SUCCESFULLY_CHANGED_PASSWORD = u'Пароль успешно изменен'
FACEBOOK_AVATAR_URL_MESSAGE = u'Ошибка сервера. Не удалось загрузить изображение с facebook'
SUCCESFULLY_UPDATED_PROFILE = u'Данные пользователя успешно изменены. Измененные поля: {0}'
INVALID_POLL_ANSWER_COUNT = (u'Неправильное количество ответов на опрос, '
    u'только multiple_choice может иметь более одного ответа')
PASSWORD_CHANGE_TITLE = u'Change password, Votem'
WRONG_POLL_CHOICES = u'Ощибка сервера. Ошибка при обработке выранных ответов на опрос.'
INVALID_CITY = u'Город не существует'
TOKEN_NOT_FOUND = u'Отсутсвует токен'
ARTICLE_POLL_NONE = u'У статьи нет опросов'
ARTICLE_NOT_FOUND = u'Ссылка не найдена'
POLL_COUNT_DONT_MATCH = u'Кол-во опросов не совпадает'
ALREADY_EXISTS = u'Такой объект уже существует'
INVALID_URL = u'Неправильный URL'
INVALID_POLL_STATUS = u'Несуществующий статус опроса'
RESET_EMAIL_ACTIVATION = u'Пожалуйста активируйте новый email'
RESET_EMAIL_DEACTIVATION = u'Ваш прежний email деактивирован'
PHONE_USED = u'Пользователь с таким номером уже существует'
USER_NOT_FOUND = u'Пользователь с таким email или phone отсутсвует'
INVALID_USERNAME = u'Неправильное имя пользователя'
SHARE_DESCRIPTION = u"Я проголосовал(-а) на Voxball. Со мной согласны {}%"
SHARE_DESCRIPTION_2 = u'Участвуйте в опросах Voxball. Голосуйте и создавайте опросы сами!'
CSRF_INVALID = u'Неправильный csrf token'
TEMPLATE_NOT_FOUND = u'Шаблон не найден'
USER_NOT_FOUND_2 = u"Пользователь не найден"