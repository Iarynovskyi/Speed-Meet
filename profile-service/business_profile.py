from database_profile.models.user_profiles import db, UserPreferenceHobby, UserProfileHobby, Hobby, UserPreference, Country, UserProfile
from flask import jsonify

def country_add(dto):
    country_name = dto.get("country")
    if country_name is not None:
        country = Country.query.filter_by(name=country_name).first()
        if not country:
            country = Country(name=country_name)
            db.session.add(country)
            db.session.commit()
    else:
        country = None
    return country


def user_profile(user_id, dto):
    country = country_add(dto)
    user = UserProfile.query.filter_by(user_id_x=user_id).first()

    if user:
        user.first_name = dto.get("first_name", None)
        user.last_name = dto.get("last_name", None)
        user.country = country
        user.age = dto.get("age", None)
        user.gender = dto.get("gender", None)
        msg = "User profile updated successfully"
    else:
        user = UserProfile(
            user_id_x=user_id,
            first_name=dto.get("first_name", None),
            last_name=dto.get("last_name", None),
            country=country,
            age=dto.get("age", None),
            gender=dto.get("gender", None)
        )
        db.session.add(user)
        msg = "New user profile created successfully"
    db.session.commit()

    return jsonify({"user_id": user.id, "msg": msg}), 201


def add_hobbies_to_profile(user_id, dto):
    user = UserProfile.query.filter_by(user_id_x=user_id).first()
    if not user:
        return jsonify({"user_id": user_id, "msg": "User profile does not exist"}), 404

    existing_hobby_ids = {hobby.hobby_id for hobby in user.hobbies}

    for hobby_name in dto.get('hobbies', []):
        hobby = Hobby.query.filter_by(name=hobby_name).first()
        if not hobby:
            hobby = Hobby(name=hobby_name)
            db.session.add(hobby)
            db.session.flush()  # Забезпечуємо доступ до hobby.id

        if hobby.id not in existing_hobby_ids:
            user_hobby = UserProfileHobby(user_profile_id=user.id, hobby_id=hobby.id)
            db.session.add(user_hobby)
    db.session.commit()
    return jsonify({"message": "Hobbies added successfully"}), 200



def create_user_preferences(user_id, dto):
    user = UserProfile.query.filter_by(user_id_x=user_id).first()
    if not user:
        return jsonify({"user_id": user_id, "msg": "User profile does not exist"}), 404

    country = country_add(dto)
    preferences = UserPreference.query.filter_by(user_id=user.id).first()
    if preferences:
        preferences.preferred_gender = dto.get('preferred_gender', None)
        preferences.preferred_age_min = dto.get('preferred_age_min', None)
        preferences.preferred_age_max = dto.get('preferred_age_max', None)
        preferences.preferred_country_id = country.id
    else:
        preferences = UserPreference(
            user_id=user.id,
            preferred_gender=dto.get('preferred_gender', None),
            preferred_age_min=dto.get('age_min', None),
            preferred_age_max=dto.get('age_max', None),
            preferred_country_id=country.id,
        )
        db.session.add(preferences)
    db.session.commit()

    existing_hobby_ids = {hobby.hobby_id for hobby in preferences.hobbies}

    for hobby_name in dto.get('preferred_hobbies', []):
        hobby = Hobby.query.filter_by(name=hobby_name).first()
        if not hobby:
            hobby = Hobby(name=hobby_name)
            db.session.add(hobby)
            db.session.flush()  # Забезпечуємо доступ до hobby.id

        if hobby.id not in existing_hobby_ids:
            preference_hobby = UserPreferenceHobby(user_preference_id=preferences.id, hobby_id=hobby.id)
            db.session.add(preference_hobby)


    db.session.commit()
    return jsonify({"user_id": user.id, "msg": "Create user preferences successfully"}), 201


def get_user_profile_with_hobbies(user_id):
    user = UserProfile.query.filter_by(user_id_x=user_id).first()
    if not user:
        return jsonify({"user_id": user_id, "msg": "User profile does not exist"}), 404

    hobbies = [relation.hobby.name for relation in user.hobbies]
    return {
        "first_name": user.first_name,
        "last_name": user.last_name,
        "country": user.country.name if user.country else None,
        "age": user.age,
        "gender": user.gender,
        "hobbies": hobbies
    }


def get_user_preferences(user_id):
    user = UserProfile.query.filter_by(user_id_x=user_id).first()
    if not user:
        return jsonify({"user_id": user_id, "msg": "User profile does not exist"}), 404

    preferences = UserPreference.query.filter_by(user_id=user.id).first()

    hobbies = [relation.hobby.name for relation in preferences.hobbies]
    return {
        "preferred_gender": preferences.preferred_gender,
        "preferred_age_min": preferences.preferred_age_min,
        "preferred_age_max": preferences.preferred_age_max,
        "preferred_country": preferences.country.name if preferences.country else None,
        "preferred_hobbies": hobbies
    }
