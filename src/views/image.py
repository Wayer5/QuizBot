import base64
from io import BytesIO

from flask import Response, send_file

from src import app
from src.crud.question import question_crud


@app.route('/question/image/<int:question_id>')
async def get_question_image(question_id: int) -> Response:
    """Выдает изображение."""
    question = await question_crud.get(question_id)
    if question and question.image:
        image_data = base64.b64decode(question.image)
        return send_file(BytesIO(image_data), mimetype='image/jpeg')
    return 'Изображение не найдено', 404
