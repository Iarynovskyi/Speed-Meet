from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Таблиця країн
class Country(db.Model):
    __tablename__ = 'countries'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False, unique=True)


# Таблиця хобі
class Hobby(db.Model):
    __tablename__ = 'hobbies'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)


# Профіль користувача
class UserProfile(db.Model):
    __tablename__ = 'user_profile'
    id = db.Column(db.Integer, primary_key=True)
    user_id_x = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'))
    country = db.relationship('Country', backref='users')
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)

    hobbies = db.relationship('UserProfileHobby', backref='profile', cascade='all, delete-orphan')


# Таблиця для зв'язку хобі з профілем
class UserProfileHobby(db.Model):
    __tablename__ = 'user_profile_hobby'
    id = db.Column(db.Integer, primary_key=True)
    user_profile_id = db.Column(db.Integer, db.ForeignKey('user_profile.id'))
    hobby_id = db.Column(db.Integer, db.ForeignKey('hobbies.id'))
    hobby = db.relationship('Hobby', backref='profile_hobbies')


# Таблиця вподобань користувача
class UserPreference(db.Model):
    __tablename__ = 'user_preferences'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_profile.id'))
    user = db.relationship('UserProfile', backref='preferences')
    preferred_gender = db.Column(db.String(10))
    preferred_age_min = db.Column(db.Integer)
    preferred_age_max = db.Column(db.Integer)
    preferred_country_id = db.Column(db.Integer, db.ForeignKey('countries.id'))
    country = db.relationship('Country', backref='preferred_by_users')

    hobbies = db.relationship('UserPreferenceHobby', backref='preference', cascade='all, delete-orphan')


# Таблиця для зв'язку хобі з вподобаннями
class UserPreferenceHobby(db.Model):
    __tablename__ = 'user_preference_hobby'
    id = db.Column(db.Integer, primary_key=True)
    user_preference_id = db.Column(db.Integer, db.ForeignKey('user_preferences.id'))
    hobby_id = db.Column(db.Integer, db.ForeignKey('hobbies.id'))
    hobby = db.relationship('Hobby', backref='preference_hobbies')
