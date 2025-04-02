# test_request.py
import unittest
from datetime import datetime, timedelta
from betting_recommendation import app, db, User, Event, BettingRecommendation  # Changed from app
from unittest.mock import patch


class TestBettingRecommendation(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        self.client = app.test_client()

        with app.app_context():
            db.create_all()
            test_user = User(user_id=1001, name="Test User", favorite_sport="soccer")
            db.session.add(test_user)

            now = datetime.now()
            events = [
                Event(sport="soccer", bet_type="Over 2.5 Goals",
                      event_date=now + timedelta(days=1)),
                Event(sport="soccer", bet_type="Both Teams to Score",
                      event_date=now + timedelta(hours=2)),
                Event(sport="soccer", bet_type="Correct Score",
                      event_date=now - timedelta(days=1)),
                Event(sport="basketball", bet_type="Most 3-Pointers",
                      event_date=now + timedelta(days=1)),
            ]
            db.session.add_all(events)
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    # Changed the patch target here
    @patch('betting_recommendation.datetime')
    def test_event_date_filtering(self, mock_datetime):
        fixed_time = datetime(2024, 1, 1, 12, 0, 0)
        mock_datetime.now.return_value = fixed_time

        with app.app_context():
            # Clear existing data from setUp
            db.session.query(Event).delete()
            db.session.query(User).delete()

            # Create fresh test data using mocked time
            user = User(user_id=1001, name="Test User", favorite_sport="soccer")
            db.session.add(user)

            # Create events relative to fixed_time
            valid_event = Event(
                sport="soccer",
                bet_type="Valid Bet",
                event_date=fixed_time + timedelta(hours=1)
            )
            past_event = Event(
                sport="soccer",
                bet_type="Past Bet",
                event_date=fixed_time - timedelta(hours=1)
            )
            db.session.add_all([valid_event, past_event])
            db.session.commit()

        response = self.client.post('/recommend', json={'user_id': 1001})
        data = response.get_json()

        self.assertEqual(len(data['recommendations']), 1)
        self.assertEqual(data['recommendations'][0]['bet_type'], "Valid Bet")

    def test_database_initialization(self):
        with app.app_context():
            db.drop_all()
            db.create_all()

            from betting_recommendation import initialize_database  # Fixed import
            initialize_database()

            users = User.query.all()
            self.assertGreaterEqual(len(users), 3)
            events = Event.query.all()
            self.assertGreaterEqual(len(events), 5)

    def test_invalid_input(self):
        response = self.client.post('/recommend', json={'user_id': 'invalid'})
        self.assertEqual(response.status_code, 400)

    def test_user_not_found(self):
        response = self.client.post('/recommend', json={'user_id': 9999})
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.get_json())

    def test_valid_user_recommendations(self):
        response = self.client.post('/recommend', json={'user_id': 1001})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data['recommendations']), 2)
if __name__ == '__main__':
    unittest.main()
