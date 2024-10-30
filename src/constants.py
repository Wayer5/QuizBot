from http import HTTPStatus

HTTP_NOT_FOUND = HTTPStatus.NOT_FOUND
UNAUTHORIZED = HTTPStatus.UNAUTHORIZED
PER_PAGE = 5
DEFAULT_PAGE_NUMBER = 1
ONE_ANSWER_VARIANT = 'Должен быть хотя бы один вариант ответа.'
CAN_ONLY_BE_ONE_CORRECT_ANSWER = 'Может быть только один правильный ответ.'
ONE_CORRECT_ANSWER = 'Должен быть хотя бы один правильный ответ.'
USER_NOT_FOUND_MESSAGE = 'Пользователь не найден'
DEFAULT_PAGE_NUMBER = 1
ITEMS_PER_PAGE = 5
UNIQUE_VARIANT = 'Варианты в вопросе должны быть уникальными.'
BAN_WARN_MESSAGE = (
    'Вы были заблокированы или или ваш профиль отсутствует. Если Вы удалили '
    'свой профиль, введите команду /start для регистрации.'
)
DELETE_ERROR_MESSAGE = (
    'Нельзя удалить запись, так как это нарушит целостность базы данных. '
    'Удаление возможно только если пользователь не оветил'
)
ERROR_FOR_CATEGORY = ' ни на один вопрос в этой рубрике.'
ERROR_FOR_QUIZ = ' ни на один вопрос в этой викторине.'
ERROR_FOR_QUESTION = ' на этот вопрос.'
AT_LEAST_ONE_QUESTION = 'Викторина должна содержать хотя бы один вопрос.'
