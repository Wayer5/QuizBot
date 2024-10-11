from flask import (
    Response,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_jwt_extended import (
    create_access_token,
    current_user,
    jwt_required,
    set_access_cookies,
    unset_jwt_cookies,
)
from sqlalchemy.sql import text

from . import app, cache, db
from src.crud.category import category_crud
from src.crud.question import question_crud
from src.crud.quiz import quiz_crud
from src.crud.quiz_result import quiz_result_crud
from src.crud.user import user_crud
from src.crud.user_answer import user_answer_crud
from src.crud.variant import variant_crud
from src.utils import Dotdict, obj_to_dict


@app.route('/login', methods=['POST'])
async def login() -> Response:
    """Производит выдачу токена в куки пользователя.

    Keyword Arguments:
    -----------------
    tgUsername -- имя пользователя в телеграме (после знака @).
    tgId -- айди пользователя.
    Return: Строку.

    """
    username = request.json.get('tgUsername', None)
    user_id = request.json.get('tgId', None)
    app.logger.info(f'User {username} with id {user_id} is trying to login')
    user = await user_crud.get_by_telegram_id(user_id)
    if user and user.telegram_id == user_id:
        access_token = create_access_token(identity=user)
        app.logger.info(
            f'User {username} with id {user_id} logged in successfully',
        )
        response = jsonify({'msg': 'login successful'})
        set_access_cookies(response, access_token)
        return response
    app.logger.info(f'User {username} with id {user_id} failed to login')
    return jsonify({'msg': 'Bad username or password'}), 401


@app.route('/logout', methods=['POST'])
def logout() -> Response:
    """Удаляет токен пользователя.

    Keyword Arguments:
    -----------------
    Return: строку.

    """
    response = jsonify({'msg': 'logout successful'})
    unset_jwt_cookies(response)
    return response


@app.route('/auth', methods=['GET'])
@cache.cached(timeout=50)
async def auntification() -> str:
    """Вывод страницы аунтификации."""
    return render_template('auth.html')


@app.route('/me', methods=['GET'])
@cache.cached(timeout=50)
@jwt_required()
def profile() -> Response:
    """Отображаем профиль пользователя."""
    user = current_user
    quiz_results = quiz_result_crud.get_results_by_user(user.id)

    total_questions = sum(result.total_questions for result in quiz_results)
    correct_answers_count = sum(
        result.correct_answers_count for result in quiz_results
    )

    # Добавляем вопросы к каждому результату
    for result in quiz_results:
        result.questions = []
        user_answers = user_answer_crud.get_results_by_user(user.id)

        # Получаем все вопросы по викторине
        questions = question_crud.get_all_by_quiz_id(result.quiz_id)

        for question in questions:
            user_answer = next(
                (ua for ua in user_answers if ua.question_id == question.id),
                None,
            )
            correct_answer_text = next(
                (v.title for v in question.variants if v.is_right_choice),
                None,
            )

            # Получаем текст ответа пользователя
            user_answer_text = next(
                (
                    v.title
                    for v in question.variants
                    if v.id == (user_answer.answer_id if user_answer else None)
                ),
                'Не отвечено',
            )

            result.questions.append(
                {
                    # Текст вопроса
                    'title': question.title,
                    # Текст ответа
                    'user_answer': user_answer_text,
                    # Правильный ответ
                    'correct_answer': correct_answer_text,
                    # Пояснение
                    'explanation': question.explanation
                    if hasattr(question, 'explanation')
                    else None,
                },
            )

    return render_template(
        'user_profile.html',
        user=user,
        quiz_results=quiz_results,
        total_questions=total_questions,
        correct_answers_count=correct_answers_count,
    )


@app.route('/me', methods=['POST'])
@jwt_required()
def delete_profile() -> Response:
    """Удаляет профиль пользователя, сохраняя результаты викторин."""
    user = current_user
    quiz_results = quiz_result_crud.get_results_by_user(user.id)

    # Обновляем результаты викторин, чтобы убрать связь с пользователем
    for result in quiz_results:
        result.user_id = None
        user_crud.update(result, {'user_id': None})

    user_answers = user_answer_crud.get_results_by_user(user.id)

    # Обновляем ответы пользователя, убирая связь с таблицей пользователи
    for answer in user_answers:
        answer.user_id = None
        user_crud.update(answer, {'user_id': None})

    user_crud.remove(current_user)

    return render_template('categories.html')


@app.route('/', methods=['GET'])
@cache.cached(timeout=50)
async def categories() -> str:
    """Вывод страницы категорий."""
    categories = category_crud.get_active()
    return render_template('categories.html', categories=categories)


@app.route('/<int:category_id>/', methods=['GET'])
@cache.cached(timeout=50)
async def quizzes(category_id: int) -> str:
    """Вывод страницы викторин."""
    quizzes = quiz_crud.get_by_category_id(category_id)
    return render_template('quizzes.html', quizzes=quizzes)


@app.route(
    '/<int:category_id>/<int:quiz_id>/',
    methods=['GET', 'POST'],
    defaults={'test': None},
)
@app.route('/<int:category_id>/<int:quiz_id>/<test>', methods=['GET', 'POST'])
@jwt_required()
def question(category_id: int, quiz_id: int, test: str) -> str:
    """Переключаем вопросы после ответов на них."""
    if test and session.get('test_answers') is None:
        session['test_answers'] = []

    if request.method == 'POST':
        question_id = int(request.form.get('question_id'))
        answer_id = int(request.form.get('answer'))

        # Получаем текущий вопрос по его ID
        current_question = question_crud.get(question_id)

        # Получаем выбранный ответ по его ID
        chosen_answer = variant_crud.get(answer_id)
        if test:
            # Сохраняем ответы в сессии пользователя
            temp = session['test_answers']
            temp.append(
                Dotdict(
                    {
                        'question': Dotdict(obj_to_dict(current_question)),
                        'answer': Dotdict(obj_to_dict(chosen_answer)),
                    },
                ),
            )
            session['test_answers'] = temp
        else:
            # Обновить результаты викторины
            quiz_result = quiz_result_crud.get_by_user_and_quiz(
                user_id=current_user.id,
                quiz_id=quiz_id,
            )
            if quiz_result is None:
                quiz_result = quiz_result_crud.create(
                    {
                        'user_id': current_user.id,
                        'quiz_id': quiz_id,
                        'question_id': question_id,
                        'total_questions': 0,
                        'correct_answers_count': 0,
                        'is_complete': False,
                    },
                )
            if chosen_answer.is_right_choice:
                quiz_result.correct_answers_count += 1
            quiz_result.total_questions += 1
            quiz_result.question_id = question_id
            quiz_result_crud.update_with_obj(quiz_result)
            user_answer_crud.create(
                {
                    'user_id': current_user.id,
                    'question_id': current_question.id,
                    'answer_id': chosen_answer.id,
                    'is_right': chosen_answer.is_right_choice,
                },
            )
        return render_template(
            'question_result.html',
            category_id=category_id,
            quiz_id=quiz_id,
            answer=chosen_answer.title,
            description=chosen_answer.description,
            user_answer=chosen_answer.is_right_choice,
            test=test,
        )
    if not test:
        # Вывод последней викторины пользователя.
        question = question_crud.get_new(
            quiz_id=quiz_id,
            user_id=current_user.id,
        )
    else:
        completed: list[int] = [
            qst.get('question').get('id')
            for qst in session.get('test_answers')
        ]
        question = question_crud.get_all_by_quiz_id(quiz_id)
        question = [qst for qst in question if qst.id not in completed]
        question = question[0] if question else None

    if question is None:
        if test:
            return redirect(url_for('results', quiz_id=quiz_id, test=True))
        quiz_result = quiz_result_crud.get_by_user_and_quiz(
            user_id=current_user.id,
            quiz_id=quiz_id,
        )
        if quiz_result is not None and not quiz_result.is_complete:
            quiz_result.is_complete = True
            quiz_result_crud.update_with_obj(quiz_result)
        return redirect(url_for('results', quiz_id=quiz_id))

    # Получаем варианты ответов
    answers = question.variants

    return render_template(
        'question.html',
        question=question,
        answers=answers,
        test=test,
    )


@app.route(
    '/results/<int:quiz_id>/',
    defaults={'test': False},
)
@app.route('/results/<int:quiz_id>/<test>')
@jwt_required()
def results(quiz_id: int, test: str) -> str:
    """Результаты викторины."""
    user = current_user

    if not test:
        # Получаем результат викторины для конкретного пользователя и викторины
        quiz_result = quiz_result_crud.get_by_user_and_quiz(user.id, quiz_id)
    else:
        test_answers = obj_to_dict(session.get('test_answers', []))
        session['test_answers'] = []
        correct_answers = sum(
            1
            for answer in test_answers
            if answer.get('answer').get('is_right_choice')
        )
        total_questions = len(test_answers)
        quiz_result = Dotdict(
            {
                'user_id': user.id,
                'quiz_id': quiz_id,
                'total_questions': total_questions,
                'correct_answers_count': correct_answers,
                'all_questions': [qr.question for qr in test_answers],
                'user_answers': [qr.answer for qr in test_answers],
            },
        )

    if not quiz_result:
        return 'Результаты викторины не найдены', 404

    # Получаем название викторины
    quiz = quiz_crud.get_by_id(quiz_id)
    quiz_title = quiz.title if quiz else 'Неизвестная викторина'

    # Считаем общее количество вопросов и количество правильных ответов
    total_questions = quiz_result.total_questions
    correct_answers_count = quiz_result.correct_answers_count

    # Добавляем вопросы к результату
    quiz_result.questions = []
    if not test:
        user_answers = user_answer_crud.get_results_by_user_and_quiz(
            user.id,
            quiz_id,
        )
        # Получаем все вопросы по викторине
        questions = question_crud.get_all_by_quiz_id(quiz_result.quiz_id)
    else:
        user_answers = quiz_result.get('user_answers')
        questions = quiz_result.get('all_questions')

    for question in questions:
        user_answer = next(
            (ua for ua in user_answers if ua.question_id == question.id),
            None,
        )
        correct_answer_text = next(
            (v.title for v in question.variants if v.is_right_choice),
            None,
        )
        # Получаем текст ответа пользователя
        # Так как из сессии получаем модель variant
        # а тут из модели user_answer
        # то условие будет разным
        user_answer = (
            user_answer
            if test
            else next(
                v for v in question.variants if v.id == user_answer.answer_id
            )
        )
        # Собираем все возможные ответы
        possible_answers = [v.title for v in question.variants]
        # Собираем информацию о вопросе
        quiz_result.questions.append(
            {
                'title': question.title,
                'user_answer': user_answer.title,
                'correct_answer': correct_answer_text,
                'possible_answers': possible_answers,
                # Описание
                'description': user_answer.description
                if user_answer
                else None,
            },
        )

    return render_template(
        'full_results.html',
        user=user,
        quiz_results=[quiz_result],
        total_questions=total_questions,
        correct_answers_count=correct_answers_count,
        quiz_title=quiz_title,
        test=test,
    )


# Статистика по конкретному вопросу
@app.route('/question/<int:question_id>/stats')
def question_stats(question_id: int) -> Response:
    """Выполняем запрос статистики для конкретного вопроса."""
    stats_query = text("""
        SELECT
            qu.title AS question_text,
            COUNT(ua.id) AS total_answers,
            SUM(CASE WHEN ua.is_right = TRUE THEN 1 ELSE 0 END) AS correct_ans,
            ROUND(SUM(CASE WHEN ua.is_right = TRUE THEN 1 ELSE 0 END) * 100.0 /
                COUNT(ua.id), 2) AS correct_percentage
        FROM questions qu
        LEFT JOIN user_answers ua ON ua.question_id = qu.id
        WHERE qu.id = :question_id
        GROUP BY qu.title
    """)

    result = db.session.execute(
        stats_query, {'question_id': question_id},
    ).fetchone()

    if result:
        question_text = result[0]  # Доступ к вопросу по индексу
        total_answers = result[1]
        correct_ans = result[2]
        correct_percentage = result[3]
    else:
        question_text = "Нет данных"
        total_answers = correct_answers = correct_percentage = 0

    correct_answers = correct_ans

    return render_template('admin/question_stats.html',
                           question_text=question_text,
                           total_answers=total_answers,
                           correct_answers=correct_answers,
                           correct_percentage=correct_percentage)


@app.route('/quiz/<int:quiz_id>/stats')
def quiz_stats(quiz_id: int) -> Response:
    """Выполняем запрос статистики для конкретной викторины."""
    stats_query = text("""
        SELECT
            q.title AS quiz_title,
            COUNT(ua.id) AS total_answers,
            SUM(CASE WHEN ua.is_right = TRUE THEN 1 ELSE 0 END) AS correct_ans,
            ROUND(SUM(CASE WHEN ua.is_right = TRUE THEN 1 ELSE 0 END) * 100.0 /
                COUNT(ua.id), 2) AS correct_percentage
        FROM quizzes q
        LEFT JOIN questions qu ON q.id = qu.quiz_id
        LEFT JOIN user_answers ua ON ua.question_id = qu.id
        WHERE q.id = :quiz_id
        GROUP BY q.title
    """)

    result = db.session.execute(stats_query, {'quiz_id': quiz_id}).fetchone()

    if result:
        quiz_title = result[0]  # Название викторины
        total_answers = result[1]
        correct_ans = result[2]
        correct_percentage = result[3]
    else:
        quiz_title = "Нет данных"
        total_answers = correct_answers = correct_percentage = 0

    correct_answers = correct_ans

    return render_template('admin/quiz_stats.html', quiz_title=quiz_title,
                           total_answers=total_answers,
                           correct_answers=correct_answers,
                           correct_percentage=correct_percentage)


@app.route('/category/<int:category_id>/stats')
def category_stats(category_id: int) -> Response:
    """Выполняем запрос статистики для конкретной категории."""
    stats_query = text("""
        SELECT
            c.name AS category_name,
            COUNT(ua.id) AS total_answers,
            SUM(CASE WHEN ua.is_right = TRUE THEN 1 ELSE 0 END) AS correct_ans,
            ROUND(SUM(CASE WHEN ua.is_right = TRUE THEN 1 ELSE 0 END) * 100.0 /
                COUNT(ua.id), 2) AS correct_percentage
        FROM categories c
        LEFT JOIN quizzes q ON q.category_id = c.id
        LEFT JOIN questions qu ON qu.quiz_id = q.id
        LEFT JOIN user_answers ua ON ua.question_id = qu.id
        WHERE c.id = :category_id
        GROUP BY c.name
    """)

    result = db.session.execute(
        stats_query, {'category_id': category_id},
    ).fetchone()

    if result:
        category_name = result[0]  # Название категории
        total_answers = result[1]
        correct_ans = result[2]
        correct_percentage = result[3]
    else:
        category_name = "Нет данных"
        total_answers = correct_answers = correct_percentage = 0

    correct_answers = correct_ans

    return render_template('admin/category_stats.html',
                           category_name=category_name,
                           total_answers=total_answers,
                           correct_answers=correct_answers,
                           correct_percentage=correct_percentage)
