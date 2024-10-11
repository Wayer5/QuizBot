from sqlalchemy.sql import text

# Запрос для получения статистики по категориям
CATEGORY_STATS_QUERY = text("""
    SELECT
        c.name AS category_name,
        COUNT(ua.id) AS total_answers,
        SUM(CASE WHEN ua.is_right = TRUE THEN 1 ELSE 0 END) AS correct_answers,
        ROUND(SUM(CASE WHEN ua.is_right = TRUE THEN 1 ELSE 0 END) * 100.0 / COUNT(ua.id), 2) AS correct_percentage
    FROM categories c
    LEFT JOIN quizzes q ON q.category_id = c.id
    LEFT JOIN questions qu ON qu.quiz_id = q.id
    LEFT JOIN user_answers ua ON ua.question_id = qu.id
    GROUP BY c.name
""")

# Запрос для получения статистики по викторинам
QUIZ_STATS_QUERY = text("""
    SELECT
        q.title AS quiz_name,
        COUNT(ua.id) AS total_answers,
        SUM(CASE WHEN ua.is_right = TRUE THEN 1 ELSE 0 END) AS correct_answers,
        ROUND(SUM(CASE WHEN ua.is_right = TRUE THEN 1 ELSE 0 END) * 100.0 / COUNT(ua.id), 2) AS correct_percentage
    FROM quizzes q
    LEFT JOIN questions qu ON qu.quiz_id = q.id
    LEFT JOIN user_answers ua ON ua.question_id = qu.id
    GROUP BY q.title
""")

# Запрос для получения статистики по вопросам
QUESTION_STATS_QUERY = text("""
    SELECT
        qu.title AS question_text,
        COUNT(ua.id) AS total_answers,
        SUM(CASE WHEN ua.is_right = TRUE THEN 1 ELSE 0 END) AS correct_answers,
        ROUND(SUM(CASE WHEN ua.is_right = TRUE THEN 1 ELSE 0 END) * 100.0 / COUNT(ua.id), 2) AS correct_percentage
    FROM questions qu
    LEFT JOIN user_answers ua ON ua.question_id = qu.id
    GROUP BY qu.title
""")
