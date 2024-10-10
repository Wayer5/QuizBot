from http import HTTPStatus

HTTP_NOT_FOUND = HTTPStatus.NOT_FOUND
UNAUTHORIZED = HTTPStatus.UNAUTHORIZED
ONE_ANSWER_VARIANT = 'Должен быть хотя бы один вариант ответа.'
CAN_ONLY_BE_ONE_CORRECT_ANSWER = 'Может быть только один правильный ответ.'
ONE_CORRECT_ANSWER = 'Должен быть хотя бы один правильный ответ.'
UNIQUE_VARIANT = 'Варианты в вопросе должны быть уникальными.'
BAN_WARN_MESSAGE = (
    'Вы были заблокированы или или ваш профиль отсутствует. Если Вы удалили '
    'свой профиль, введите команду /start для регистрации.'
)
