'''
Модель юзерів для SQlalchemy та роботи з цією таблицей в бд
'''
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email

    @classmethod
    def add_user(cls, username, password, email):
        hashed_password = generate_password_hash(password)
        user = User(username=username, password=hashed_password, email=email)
        db.session.add(user)
        db.session.commit()
        return user

    @classmethod
    def get_user_by_username(cls, email, username):
        return User.query.filter(
            or_(
                User.username == username,
                User.email == email
            )
        ).first()

    def check_password(self, password_input):
        return check_password_hash(self.password, password_input)