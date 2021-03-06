from flask import Blueprint, request, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import jwt
import json
from app.api.v1.utils.validator import valid_email, email_exists, username_exists
from app.db import init_db, user_db
from app.api.v1.models.users_model import UsersModel
from app.api.v1.models.meetups_model import MeetupsModel
from app.api.v1.models.questions_model import QuestionModel
from app.api.v1.utils.utils import requires_token
from instance.config import key as enc_key


v1 = Blueprint('v1', __name__, url_prefix='/api/v1')
user = UsersModel()
m = MeetupsModel()
q = QuestionModel()
user_db = init_db(user_db)


@v1.route('/signup', methods=['POST'])
def signup():
    """Sign up route."""
    required = ["firstname", "lastname", "password", "email", "phoneNumber", "username", "isAdmin"]
    try:
        data = request.get_json()
        if data is None:
            return jsonify({
                "status": 400,
                "error": "Please provide the required fields. {}".format([field for field in required])
            })
    except Exception:
        return jsonify({
            "status": 400,
            "error": "Please provide the required fields. {}".format([field for field in required])
        })
    fname = data.get('firstname')
    lname = data.get("lastname")
    password = data.get("password")
    other_name = data.get("othername") or ''
    email = data.get("email")
    phone = data.get("phoneNumber")
    username = data.get("username")
    isAdmin = data.get("isAdmin")

    if not fname:
        return jsonify({"status": 400, "error": "{} is missing.".format("firstname")}), 400
    if not lname:
        return jsonify({"status": 400, "error": "{} is missing.".format("lastname")}), 400
    if not password:
        return jsonify({"status": 400, "error": "{} is missing.".format("password")}), 400
    if not email:
        return jsonify({"status": 400, "error": "{} is missing.".format("email")}), 400
    if not phone:
        return jsonify({"status": 400, "error": "{} is missing.".format("phoneNumber")}), 400
    if not username:
        return jsonify({"status": 400, "error": "{} is missing.".format("username")}), 400
    if not isAdmin:
        return jsonify({"status": 400, "error": "{} is missing.".format("isAdmin")}), 400

    new_user = user.user_obj(fname=fname, lname=lname, password=password, othername=other_name, email=email, phone_number=phone, username=username, isAdmin=isAdmin)
    return user.save(new_user)


@v1.route('/login', methods=['POST'])
def login():
    """Log in route."""
    data = request.json

    required = ["email", "password"]
    if data is None:
        return jsonify({"status": 400, "error": "Please provide the required fields. {}".format([field for field in required])})
    for key, value in data.items():
        if value is None or value == "":
            return jsonify({
                "status": 400,
                "error": "{} is missing.".format(key)
            })
        else:
            email = data.get('email')
            password = data.get('password')

            if valid_email(email):
                if email_exists(email, user_db):
                    cur_user = user.get_user(email)
                    if cur_user and check_password_hash(cur_user.get('password'), password):
                        data = {
                            "email": email,
                            "sub": email,
                            "exp": datetime.datetime.now() + datetime.timedelta(minutes=5)
                        }
                        token = jwt.encode(data, enc_key, algorithm='HS256')

                        if token:
                            return jsonify({
                                "status": 200,
                                "message": "Logged in successfully!",
                                "token": token.decode('utf-8')
                                })
                        else:
                            return jsonify({
                                "status": 401,
                                "error": "Could not verify token. Please sign in again!",
                                "token": token.decode('utf-8')
                                })

                else:
                    return jsonify({
                        "status": 400,
                        "error": "No user found with the given credentials"
                        }), 400
            else:
                return jsonify({
                    "status": 400,
                    "error": "Email invalid"
                })


@v1.route('/meetups', methods=['POST'])
@requires_token
def create_meetup(user):
    if not user['isAdmin'] == "True":
        return jsonify({
            "status": 403,
            "error": "Action requires Admin Priviledges"
        }), 403
    required = ["topic", "location", "happeningOn", "tags"]
    try:
        data = request.get_json()

        topic = data.get('topic')
        location = data.get('location')
        images = data.get('images')
        happeningOn = data.get('happeningOn')
        tags = data.get('tags')
        tag = tags.split(',')

        if not topic:
            return jsonify({
                "status": 400,
                "message": "{} is missing.".format("topic")
            }), 400
        if not location:
            return jsonify({
                "status": 400,
                "message": "{} is missing.".format("location")
            }), 400
        if not happeningOn:
            return jsonify({
                "status": 400,
                "message": "{} is missing.".format("happeningOn")
            }), 400
        if not tags:
            return jsonify({
                "status": 400,
                "message": "{} is missing.".format("tags")
            }), 400
        else:
            new_meetup = m.meetup(location=location, images=images, topic=topic, happeningOn=happeningOn, tags=tag)
            meetup = m.create(new_meetup)
            return jsonify({
                "status": 201,
                "message": "Meetup created successfully!",
                "data": [
                        {
                            "topic": topic,
                            "location": location,
                            "happeningOn": happeningOn,
                            "tags": tag
                            }
                        ]
            }), 201
    except Exception:
        return jsonify({
            "status": 400,
            "error": "Please provide the following fields. {}".format([item for item in required])
        }), 400


@v1.route('/meetups/upcoming', methods=['GET'])
def get_meetups():
    """Get all meetups route."""
    meetups = m.get_all()
    return jsonify({
        "status": 200,
        "data": meetups
    })


@v1.route('/questions', methods=['POST'])
def post_question():
    """Post a question route."""
    required = ["title", "meetup", "body", "createdBy"]
    try:
        data = request.get_json()
    except Exception:
        return jsonify({
            "status": 400,
            "error": "Please provide the following fields. {}".format([items for items in required])
        })
    title = data.get("title")
    meetup = data.get("meetup")
    body = data.get("body")
    createdBy = data.get("createdBy")

    if not title:
        return jsonify({
            "status": 400,
            "error": "{} is missing.".format('title')
            })
    if not meetup:
        return jsonify({
            "status": 400,
            "error": "{} is missing.".format('meetup')
            })
    if not body:
        return jsonify({
            "status": 400,
            "error": "{} is missing.".format('body')
            })
    if not createdBy:
        return jsonify({
            "status": 400,
            "error": "{} is missing.".format('createdBy')
            })
    else:
        new_question = q.question(title=title, body=body, meetup=meetup, author=createdBy, votes=0)
        return q.save(new_question)


@v1.route('/meetups/<int:meetup_id>', methods=['GET'])
def get_one(meetup_id):
    """Get a specific meetup."""
    meetup = meetup_id
    if not int(meetup):
        return jsonify({
            "status": 400,
            "error": "Wrong parameters supplied for the request"
        }), 400
    else:
        resp = m.get_meetup(meetup)
        return jsonify({
            "status": 200,
            "data": resp
        }), 200


@v1.route('/questions/<int:question_id>/upvote', methods=['PATCH'])
def upvote(question_id):
    """Upvote a specific question."""
    query = q.get_question(question_id)
    updated_votes = q.upvote(query)
    return jsonify({
        "status": 200,
        "message": "Question upvoted successfully!",
        "question": updated_votes
    })


@v1.route('/questions/<int:question_id>/downvote', methods=['PATCH'])
def downvote(question_id):
    """Downvote a specific question."""
    query = q.get_question(question_id)
    downvoted_votes = q.downvote(query)
    return jsonify({
        "status": 200,
        "message": "Question downvoted successfully!",
        "question": downvoted_votes
    })


@v1.route('/meetups/<int:meetup_id>/rsvps', methods=['POST'])
@requires_token
def rsvp_a_meetup(user, meetup_id):
    meetup = meetup_id
    user = user['id']
    required = ["yes", "no", "maybe"]
    try:
        data = request.get_json()
        resp = data.get('response')

        for key, value in data.items():
            if key != "response":
                return jsonify({
                    "status": 400,
                    "error": "Please provide the following fields. {}".format('response')
                }), 400
            if value not in required:
                return jsonify({
                    "status": 400,
                    "error": "Only the following responses are allowed. {}".format([item for item in required])
                    }), 400
            new_rsvp = m.rsvp(meetup=meetup, user=user, response=resp)
            return m.create_rsvp(rsvp=new_rsvp)
    
    except Exception as e:
        raise e
    #     return jsonify({
    #         "status": 400,
    #         "error": "Please provide the following fields. {}".format('response')
    #     }), 400
