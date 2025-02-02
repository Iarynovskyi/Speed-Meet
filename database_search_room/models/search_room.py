'''
Модель юзерів для SQlalchemy та роботи з цією таблицей в бд
'''
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
db = SQLAlchemy()

class SearchRoom(db.Model):
    __tablename__ = 'search_room'
    id = db.Column(db.Integer, primary_key=True)
    user_id_x = db.Column(db.String(100), nullable=False)
    status_x = db.Column(db.Boolean, nullable=False)
    in_room = db.Column(db.Boolean, nullable=False)

class RoomHistory(db.Model):
    __tablename__ = 'room_history'
    id = db.Column(db.Integer, primary_key=True)
    user_id_x = db.Column(db.String(100), nullable=False)
    user_id_y = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.now())
    room_status = db.Column(db.String(50), default="active")
    start_time = db.Column(db.DateTime, default=db.func.now())
    end_time = db.Column(db.DateTime, nullable=True)

class VipRoomHistory(db.Model):
    __tablename__ = 'vip_room_history'
    id = db.Column(db.Integer, primary_key=True)
    user_id_x = db.Column(db.String(100), nullable=False)
    user_id_y = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.DateTime, default=db.func.now())
    end_time = db.Column(db.DateTime, nullable=True)


