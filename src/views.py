import logging
from flask import render_template, request

from . import app


@app.route('/', methods=['GET'])
async def index():
    logging.info(f'Куки: {request.cookies.get('tg_id'), request.cookies.get("tg_username")}')
    return render_template('question.html')
