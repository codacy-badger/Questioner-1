"""Question Model."""
import datetime
from flask import jsonify
from .base_model import BaseModel
from app.db import init_db, question_db


class QuestionModel(BaseModel):
    """Question model Tests class."""

    def __init__(self):
        """Initialize the Meetup model."""
        self.db = init_db(question_db)

    def question(self, title, body, meetup, author, votes=0):
        """Question object."""
        query = {
            "id": len(self.db) + 1,
            "title": title,
            "body": body,
            "meetup": meetup,
            "createdOn": datetime.datetime.now().strftime("%I:%M:%S%P %d %b %Y"),
            "createdBy": author,
            "votes": votes,
        }
        return query

    def save(self, question):
        """Store a question method."""
        db = self.db
        db.append(question)
        return jsonify({
            "status": 201,
            "message": "Question posted successfully!"
        })

    def get_question(self, question_id):
        """Get a question method."""
        query = self.db[question_id - 1]
        return query

    def upvote(self, question):
        """Upvote a question method."""
        query = question
        query['votes'] += 1
        return query

    def downvote(self, question):
        """Downvote a question method."""
        query = question
        query['votes'] -= 1
        return query
