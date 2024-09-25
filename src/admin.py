from flask_admin import Admin

from . import app

# Создания экземпляра админ панели
admin = Admin(app, name='MedStat_Solutions', template_mode='bootstrap4')
