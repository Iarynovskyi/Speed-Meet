from database_search_room.models.search_room import db, SearchRoom, RoomHistory, VipRoomHistory
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
    # Гендер як обов'язковий параметр
    if preferences['preferred_gender'] != other_profile['gender'] or other_preferences['preferred_gender'] != profile[
        'gender']:
        #return 0
        a = 1

    # Визначаємо ваги
    WEIGHT_AGE = 0.4
    WEIGHT_COUNTRY = 0.25
    WEIGHT_HOBBIES = 0.1

    # Перевіряємо вікову сумісність
    is_age_match = preferences['preferred_age_min'] <= other_profile['age'] <= preferences['preferred_age_max']
    is_age_match_reverse = other_preferences['preferred_age_min'] <= profile['age'] <= other_preferences[
        'preferred_age_max']
    age_score = WEIGHT_AGE if is_age_match and is_age_match_reverse else 0

    # Перевіряємо сумісність по країні
    is_country_match = preferences['preferred_country'] == other_profile['country']
    is_country_match_reverse = other_preferences['preferred_country'] == profile['country']
    country_score = WEIGHT_COUNTRY if is_country_match and is_country_match_reverse else 0

    # Перевіряємо сумісність по хобі
    common_hobbies = set(preferences['preferred_hobbies']) & set(other_profile['hobbies'])
    common_hobbies_reverse = set(other_preferences['preferred_hobbies']) & set(profile['hobbies'])
    hobbies_score = WEIGHT_HOBBIES * (len(common_hobbies) + len(
        common_hobbies_reverse)) / 2 if common_hobbies or common_hobbies_reverse else 0

    # Підрахунок загального коефіцієнта
    compatibility_score = age_score + country_score + hobbies_score
    return compatibility_score

import asyncio
from datetime import datetime, timedelta

async def create_room_with_waiting(user_id, user_data, max_wait_time=60):
    # Поточний користувач
    current_user = SearchRoom.query.filter_by(user_id_x=user_id).first()
    if not current_user or current_user.in_room:
        return None
    # Часовий інтервал для перевірки повторень
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    # Початковий час для ліміту очікування
    start_time = datetime.now()

    while (datetime.now() - start_time).total_seconds() < max_wait_time:
        # Знаходимо історію кімнат для поточного користувача за останню годину
        recent_partners = db.session.query(RoomHistory.user_id_y).filter(
            RoomHistory.user_id_x == user_id,
            RoomHistory.timestamp >= one_hour_ago
        ).union(
            db.session.query(RoomHistory.user_id_x).filter(
                RoomHistory.user_id_y == user_id,
                RoomHistory.timestamp >= one_hour_ago
            )
        ).all()

        recent_partner_ids = {partner[0] for partner in recent_partners}

        # Знаходимо кандидатів
        candidates = SearchRoom.query.filter(
            SearchRoom.status_x == True,
            SearchRoom.in_room == False,
            #SearchRoom.user_id_x != user_id,  # Виключаємо самого себе
            ~SearchRoom.user_id_x.in_(recent_partner_ids)  # Уникаємо повторень
        ).all()

        # Якщо знайдено кандидата
        for candidate in candidates:
            other_user_data = info_from_service(candidate.user_id_x)
            score = compare_profiles(
                user_data["preferences"],
                user_data["profile"],
                other_user_data["preferences"],
                other_user_data["profile"]
            )

            if score >= 0.4:  # Поріг сумісності
                # Створюємо кімнату
                set_user_in_room(candidate.user_id_x)
                set_user_in_room(current_user.user_id_x)
                # Додаємо в історію
                new_room_history = RoomHistory(user_id_x=user_id, user_id_y=candidate.user_id_x)
                db.session.add(new_room_history)
                db.session.commit()

                return {"room_id": new_room_history.id, "partner": candidate.user_id_x, "profile": other_user_data["profile"]}
        # Очікуємо 5 секунд перед повторною спробою
        await asyncio.sleep(5)
    # Якщо партнер не знайдений за час очікування
    return {"error": "No suitable partner found within the waiting time."}


def now_you_can_read_a_little_about_your_partner(partner_id, partner_profile):
    pass

def create_vip_room(user_1_id, user_2_id):
    vip_room = VipRoomHistory(user_id_x=user_1_id, user_id_y=user_2_id)
    db.session.add(vip_room)
    db.session.commit()
    set_user_offline(user_1_id)
    set_user_offline(user_2_id)
    set_user_out_of_room(user_1_id)
    set_user_out_of_room(user_2_id)

def leave_room(user_1_id, user_2_id):
    set_user_out_of_room(user_1_id)
    set_user_out_of_room(user_2_id)