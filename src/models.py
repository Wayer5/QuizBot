from datetime import datetime

from sqlalchemy import UniqueConstraint

from . import db


class User(db.Model):

    """Модель пользователя.

    Хранит информацию о пользователях.

    """

    __tablename__ = 'users'
    id = db.Column(db.Integer, unique=True, primary_key=True)
    name = db.Column(db.String)
    username = db.Column(db.String, unique=True)
    telegram_id = db.Column(db.BigInteger)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    updated_on = db.Column(
        db.DateTime(),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    is_active = db.Column(db.Boolean(), default=True)
    is_admin = db.Column(db.Boolean(), default=False)

    # Связь с таблицей QuizResult
    quizzes_results = db.relationship(
        'QuizResult',
        backref='result',
        cascade='all,delete',
        lazy=True,
    )


class Category(db.Model):

    """Модель категории викторины.

    Хранит информацию о различных категориях викторин.

    """

    __tablename__ = 'categories'
    id = db.Column(
        db.Integer,
        primary_key=True,
        comment='Уникальный идентификатор категории.',
    )
    name = db.Column(
        db.String(50),
        nullable=False,
        unique=True,
        comment='Название категории викторины.',
    )
    is_active = db.Column(
        db.Boolean,
        default=True,
        comment='Флаг активности категории.',
    )

    # Связь с таблицей quizzes
    quizzes = db.relationship(
        'Quiz',
        back_populates='category',
        cascade='all,delete',
        lazy=True,
    )

    def __str__(self) -> str:
        """Отображение названия объекта в админ зоне."""
        return self.name


class Quiz(db.Model):

    """Модель викторины.

    Содержит основную информацию о викторине, такую как название и категория.

    """

    __tablename__ = 'quizzes'
    id = db.Column(
        db.Integer,
        primary_key=True,
        comment='Уникальный идентификатор викторины.',
    )
    title = db.Column(
        db.String(150),
        nullable=False,
        comment='Название викторины.',
        unique=True,
    )
    category_id = db.Column(
        db.Integer,
        db.ForeignKey('categories.id'),
        nullable=False,
        comment='Идентификатор категории, к которой относится викторина.',
    )
    category = db.relationship('Category', back_populates='quizzes')
    is_active = db.Column(
        db.Boolean,
        default=True,
        comment='Флаг активности викторины.',
    )

    # Связь с таблицей questions
    questions = db.relationship(
        'Question',
        back_populates='quiz',
        lazy=True,
        cascade='all,delete',
    )

    # Связь с таблицей результатов викторины
    results = db.relationship(
        'QuizResult',
        backref='quiz',
    )

    def __str__(self) -> str:
        """Отображение названия объекта в админ зоне."""
        return self.title


class Question(db.Model):

    """Модель вопроса.

    Содержит информацию о вопросах, относящихся к викторине.

    """

    __tablename__ = 'questions'
    id = db.Column(
        db.Integer,
        primary_key=True,
        comment='Уникальный идентификатор вопроса.',
        index=True,
    )
    title = db.Column(
        db.String(150),
        nullable=False,
        comment='Текст вопроса.',
        unique=True,
    )
    quiz_id = db.Column(
        db.Integer,
        db.ForeignKey('quizzes.id'),
        nullable=False,
        comment='Идентификатор викторины, к которой относится вопрос.',
        index=True,
    )
    quiz = db.relationship(
        'Quiz',
        back_populates='questions',
    )
    is_active = db.Column(
        db.Boolean,
        default=True,
        comment='Флаг активности вопроса.',
        index=True,
    )

    # Связь с таблицей variants
    variants = db.relationship(
        'Variant',
        backref='variants',
        lazy=True,
        cascade='all,delete',
    )


class Variant(db.Model):

    """Модель варианта ответа.

    Содержит информацию о вариантах ответа на вопрос.

    """

    __tablename__ = 'variants'
    id = db.Column(
        db.Integer,
        primary_key=True,
        comment='Уникальный идентификатор варианта ответа.',
    )
    question_id = db.Column(
        db.Integer,
        db.ForeignKey('questions.id'),
        nullable=False,
        comment='Идентификатор вопроса, к которому относится данный ответ.',
    )
    title = db.Column(
        db.String(150),
        nullable=False,
        comment='Текст варианта ответа.',
    )
    description = db.Column(
        db.Text,
        nullable=True,
        comment='Дополнительное описание или пояснение для варианта ответа.',
    )
    is_right_choice = db.Column(
        db.Boolean,
        default=False,
        comment='Флаг, указывающий, является ли данный ответ правильным.',
    )


class QuizResult(db.Model):

    """Модель результатов викторины.

    Хранит информацию о прохождении пользователем викторины.
    Такие как количество правильных ответов и статус завершения.

    """

    __tablename__ = 'quiz_results'
    id = db.Column(
        db.Integer,
        primary_key=True,
        comment='Уникальный идентификатор результата викторины.',
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=True,
        comment='Идентификатор пользователя, прошедшего викторину.',
    )
    quiz_id = db.Column(
        db.Integer,
        db.ForeignKey('quizzes.id'),
        nullable=False,
        comment='Идентификатор викторины.',
    )
    total_questions = db.Column(
        db.Integer,
        nullable=False,
        comment='Общее количество вопросов в викторине.',
    )
    correct_answers_count = db.Column(
        db.Integer,
        nullable=False,
        comment='Количество правильных ответов, данных пользователем.',
    )
    is_complete = db.Column(
        db.Boolean,
        default=False,
        comment='Флаг завершения викторины.',
    )

    # Связь с таблицей questions
    question_id = db.Column(
        db.Integer,
        db.ForeignKey('questions.id'),
        nullable=False,
        comment='Идентификатор последнего отвеченного вопроса.',
    )
    __table_args__ = (
        UniqueConstraint(
            'user_id',
            'quiz_id',
            name='_person_quiz_uc',
        ),
    )


class UserAnswer(db.Model):

    """Модель ответов пользователей на вопросы.

    Хранит информацию о каждом ответе пользователя на вопросы викторины.

    """

    __tablename__ = 'user_answers'
    id = db.Column(
        db.Integer,
        primary_key=True,
        comment='Уникальный идентификатор ответа пользователя.',
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False,
        comment='Идентификатор пользователя.',
        index=True,
    )
    question_id = db.Column(
        db.Integer,
        db.ForeignKey('questions.id'),
        nullable=False,
        comment='Идентификатор вопроса, на который ответил пользователь.',
        index=True,
    )
    answer_id = db.Column(
        db.Integer,
        db.ForeignKey('variants.id'),
        nullable=False,
        comment='Идентификатор выбранного варианта ответа.',
    )
    is_right = db.Column(
        db.Boolean,
        default=False,
        comment='Флаг, указывающий, является ли ответ правильным.',
    )
    __table_args__ = (
        UniqueConstraint(
            'user_id',
            'question_id',
            name='_person_question_uc',
        ),
    )


class TelegramUser(db.Model):

    """Модель для хранения информации о пользователях Telegram."""

    __tablename__ = 'telegram_users'
    id = db.Column(
        db.Integer,
        primary_key=True,
        comment='Уникальный идентификатор записи в таблице.',
    )
    telegram_id = db.Column(
        db.BigInteger,
        unique=True,
        nullable=False,
        comment='Уникальный идентификатор пользователя в Telegram.',
    )
    first_name = db.Column(
        db.String(100),
        nullable=False,
        comment='Имя пользователя в Telegram.',
    )
    last_name = db.Column(
        db.String(100),
        nullable=True,
        comment='Фамилия пользователя в Telegram.',
    )
    username = db.Column(
        db.String(100),
        nullable=True,
        unique=True,
        comment='Имя пользователя в Telegram (username).',
    )
    language_code = db.Column(
        db.String(10),
        nullable=True,
        comment='Язык пользователя в формате IETF.',
    )
    is_premium = db.Column(
        db.Boolean,
        default=False,
        comment='Указывает, есть ли у пользователя премиум в Telegram.',
    )
    added_to_attachment_menu = db.Column(
        db.Boolean,
        default=False,
        comment='Указывает, добавил ли пользователь бота в меню вложений.',
    )
    created_on = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        comment='Дата и время создания записи.',
    )

    def __repr__(self) -> str:
        return f'<TelegramUser id={self.telegram_id}'
