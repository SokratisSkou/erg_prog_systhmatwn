from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from pydantic import BaseModel, ValidationError
from datetime import datetime, timedelta
from flask_restful import Api, Resource
import random

app = Flask(__name__)
api = Api(app)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///betting.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Define Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    favorite_sport = db.Column(db.String(50), nullable=False)


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sport = db.Column(db.String(50), nullable=False)
    bet_type = db.Column(db.String(100), nullable=False)
    event_date = db.Column(db.DateTime, nullable=False)


# Initialize database explicitly
def initialize_database():
    with app.app_context():
        db.create_all()
        if User.query.count() == 0:
            users = [
                User(user_id=1234, name="Test User", favorite_sport="soccer"),
                User(user_id=5678, name="Alice", favorite_sport="basketball"),
                User(user_id=9101, name="Bob", favorite_sport="tennis")
            ]
            db.session.add_all(users)
            db.session.commit()

        if Event.query.count() == 0:
            generate_dummy_events(5)
            db.session.commit()


def generate_dummy_users(count=10):
    sports = ["soccer", "basketball", "tennis", "baseball", "football"]
    for i in range(count):
        new_user = User(
            user_id=random.randint(1000, 9999),
            name=f"User_{i}",
            favorite_sport=random.choice(sports)
        )
        db.session.add(new_user)
    db.session.commit()


def generate_dummy_events(count=10):
    sports = ["soccer", "basketball", "tennis", "baseball", "football"]
    bet_types = ["Over 2.5 Goals", "Both Teams to Score", "Most 3-Pointers", "Match Winner", "Total Points"]
    for _ in range(count):
        new_event = Event(
            sport=random.choice(sports),
            bet_type=random.choice(bet_types),
            event_date=datetime.now() + timedelta(days=random.randint(-5, 5))
        )
        db.session.add(new_event)
    db.session.commit()


class RecommendationRequest(BaseModel):
    user_id: int

    class Config:
        extra = 'forbid'


class BettingRecommendation(Resource):
    def post(self):
        try:
            data = request.get_json()
            request_data = RecommendationRequest(**data)

            # Get user's favorite sport
            user = User.query.filter_by(user_id=request_data.user_id).first()
            if not user:
                return {"error": "User not found"}, 404

            # Find upcoming events matching favorite sport
            current_time = datetime.now()
            recommendations = Event.query.filter(
                Event.sport == user.favorite_sport,
                Event.event_date > current_time
            ).order_by(Event.event_date).all()

            # Format response
            recommendations_data = [{
                "sport": event.sport,
                "bet_type": event.bet_type,
                "event_date": event.event_date.isoformat()
            } for event in recommendations]

            return {
                "user_id": user.user_id,
                "favorite_sport": user.favorite_sport,
                "recommendations": recommendations_data
            }, 200

        except ValidationError as e:
            return {"error": e.errors()}, 400
        except Exception as e:
            return {"error": str(e)}, 500


api.add_resource(BettingRecommendation, "/recommend")

if __name__ == '__main__':
    initialize_database()
    app.run(debug=True)
