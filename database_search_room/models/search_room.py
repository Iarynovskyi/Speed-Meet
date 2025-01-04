'''
Модель юзерів для SQlalchemy та роботи з цією таблицей в бд
'''
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class SearchRoom(db.Model):
    __tablename__ = 'search_room'
    id = db.Column(db.Integer, primary_key=True)
    user_id_x = db.Column(db.String(100), nullable=False)
    status_x = db.Column(db.Boolean, nullable=False)
    in_room = db.Column(db.Boolean, nullable=False)





