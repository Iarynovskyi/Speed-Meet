from database_search_room.models.search_room import db, SearchRoom
from flask import jsonify
from jwt import get_user_profile, get_user_preferences

def set_user_online(user_id):
    existing_record = SearchRoom.query.filter_by(user_id_x=user_id).first()

    if existing_record:
        existing_record.status_x = True
        existing_record.in_room = False
    else:
        new_record = SearchRoom(
            user_id_x=user_id,
            status_x=True,
            in_room=False
        )
        db.session.add(new_record)

    db.session.commit()

def set_user_in_room(user_id):
    existing_record = SearchRoom.query.filter_by(user_id_x=user_id).first()

    if existing_record:
        existing_record.in_room = True
    else:
        new_record = SearchRoom(
            user_id_x=user_id,
            status_x=True,
            in_room=True
        )
        db.session.add(new_record)

    db.session.commit()

def set_user_out_of_room(user_id):
    existing_record = SearchRoom.query.filter_by(user_id_x=user_id).first()

    if existing_record:
        existing_record.in_room = False
    else:
        new_record = SearchRoom(
            user_id_x=user_id,
            status_x=True,
            in_room=False
        )
        db.session.add(new_record)

    db.session.commit()

def set_user_offline(user_id):
    existing_record = SearchRoom.query.filter_by(user_id_x=user_id).first()

    if existing_record:
        existing_record.status_x = False
    else:
        new_record = SearchRoom(
            user_id_x=user_id,
            status_x=False,
            in_room=False
        )
        db.session.add(new_record)

    db.session.commit()


def recommendation_people_for_you(user_data):
    online_users = SearchRoom.query.filter_by(status_x=True).all()

    matching_users = []

    for user in online_users:
        other_user_data = info_from_service(user.user_id_x)
        if other_user_data:

            if compare_profiles(user_data['preferences'], user_data['profile'], other_user_data['preferences'], other_user_data['profile']):
                matching_users.append(user.user_id_x)

    return matching_users

def info_from_service(user_id):
    profile, error = get_user_profile(user_id)
    if error:
        return jsonify({"error": error}), 500

    preferences, error = get_user_preferences(user_id)
    if error:
        return jsonify({"error": error}), 500

    return  {"profile": profile, "preferences": preferences}


def compare_profiles(preferences, profile, other_preferences, other_profile):
    is_gender_match = preferences['preferred_gender'] == other_profile['gender']
    is_age_match = preferences['preferred_age_min']  <= other_profile['age'] <= preferences['preferred_age_max']
    is_country_match = preferences['country'] == other_profile['country']
    is_hobbies_match = bool(set(preferences['hobbies']) & set(other_profile['hobbies']))

    if not (is_gender_match and is_age_match and is_country_match and is_hobbies_match):
        return False

    is_gender_match_reverse = other_preferences['preferred_gender'] == profile['gender']
    is_age_match_reverse = other_preferences['preferred_age_min'] <= profile['age'] <= other_preferences['preferred_age_max']
    is_country_match_reverse = other_preferences['preferred_country'] == profile['country']
    is_hobbies_match_reverse = bool(set(other_preferences['preferred_hobbies']) & set(profile['hobbies']))

    return is_gender_match_reverse and is_age_match_reverse and is_country_match_reverse and is_hobbies_match_reverse

