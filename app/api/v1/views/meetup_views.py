"""Meetups Views."""
from flask import Blueprint, request, jsonify
from ..models.meetups_model import MeetupsModel
from ..utils.utils import requires_token


v1_m = Blueprint('v1_m', __name__, url_prefix='/api/v1')
m = MeetupsModel()


@v1_m.route('/meetups', methods=['POST'])
@requires_token
def create_meetup(user):
    """Create a meetup route."""
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
            new_meetup = m.meetup(location=location,
                                  images=images, topic=topic,
                                  happeningOn=happeningOn, tags=tag)
            m.create(new_meetup)
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
            "error": "Please provide the following fields. \
             {}".format([item for item in required])
        }), 400


@v1_m.route('/meetups/upcoming', methods=['GET'])
def get_meetups():
    """Get all meetups route."""
    meetups = m.get_all()
    return jsonify({
        "status": 200,
        "data": meetups
    })


@v1_m.route('/meetups/<int:meetup_id>', methods=['GET'])
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


@v1_m.route('/meetups/<int:meetup_id>/rsvps', methods=['POST'])
@requires_token
def rsvp_a_meetup(user, meetup_id):
    """Rsvp to a meetup route."""
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
                    "error": "Please provide the following fields. \
                     {}".format('response')
                }), 400
            if value not in required:
                return jsonify({
                    "status": 400,
                    "error": "Only the following responses are allowed. \
                     {}".format([item for item in required])
                    }), 400
            new_rsvp = m.rsvp(meetup=meetup, user=user, response=resp)
            return m.create_rsvp(rsvp=new_rsvp)

    except Exception as e:
        raise e