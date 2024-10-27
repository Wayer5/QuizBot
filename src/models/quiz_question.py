from src import db

# Таблица для связи многие ко многим
quiz_questions = db.Table(
    'quiz_questions',
    db.Column(
        'quiz_id',
        db.Integer,
        db.ForeignKey('quizzes.id'),
        primary_key=True
    ),
    db.Column(
        'question_id',
        db.Integer,
        db.ForeignKey('questions.id'),
        primary_key=True
    ),
)
