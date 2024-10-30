# from flask import (
#     render_template,
#     request,
# )

# from src import app, cache
# from src.constants import DEFAULT_PAGE_NUMBER, HTTP_NOT_FOUND, PER_PAGE
# from src.crud.category import category_crud


# @app.route('/', methods=['GET'])
# @cache.cached(timeout=30, key_prefix='categories_view_cache')
# async def categories() -> str:
#     """Вывод страницы рубрик."""
#     page = request.args.get('page', DEFAULT_PAGE_NUMBER, type=int)
#     per_page = PER_PAGE
#     categories_paginated = (await category_crud.get_active()).paginate(
#         page=page,
#         per_page=per_page,
#         error_out=False,
#     )
#     if not categories_paginated.items:
#         return render_template('errors/404.html'), HTTP_NOT_FOUND
#     return render_template(
#         'categories.html',
#         categories=categories_paginated.items,
#         pagination=categories_paginated,
#     )
