from flask import Flask, request
from pydantic import BaseModel, ValidationError
from datetime import datetime
from flask_restful import Api, Resource
import dummy_data

app = Flask(__name__)
api = Api(app)

class RecommendationRequest(BaseModel):
    user_id: int

    class Config:
        extra = 'forbid'  # Prevent extra fields

class BettingRecommendation(Resource):
    def post(self):
        try:
            data = request.get_json()
            print("Received data:", data)

            if not data:
                return {"error": "No data provided"}, 400

            validated_data = RecommendationRequest(**data)
            user = next((u for u in dummy_data.dummy_users if u["user_id"] == validated_data.user_id), None)

            if not user:
                return {"error": "User not found"}, 404

            now = datetime.now()
            favorite_sport = user["favorite_sport"]
            future_events = [
                event for event in dummy_data.dummy_events
                if event["sport"] == favorite_sport
                and datetime.strptime(event["event_date"], "%Y-%m-%d %H:%M:%S") > now
            ]

            if not future_events:
                return {
                    "user_id": validated_data.user_id,
                    "recommendations": [],
                    "message": "No upcoming events found"
                }, 200

            return {
                "user_id": validated_data.user_id,
                "recommendations": future_events
            }, 200

        except ValidationError as e:
            print("Validation error:", e.errors())
            return {"error": e.errors()}, 400
        except Exception as e:
            print("Unexpected error:", str(e))
            return {"error": "An unexpected error occurred."}, 500

api.add_resource(BettingRecommendation, "/recommend")

if __name__ == "__main__":
    app.run(debug=True)