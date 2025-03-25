from datetime import datetime, timedelta
import random
from faker import Faker

fake = Faker()

# Define sports and bet types
SPORTS = ["soccer", "basketball", "tennis", "baseball", "hockey"]
BET_TYPES = {
    "soccer": ["Over 2.5 Goals", "Both Teams to Score", "First Half Winner", "Draw No Bet"],
    "basketball": ["Most 3-Pointers", "Total Points Over/Under", "Winning Margin"],
    "tennis": ["Win in Straight Sets", "Total Games Over/Under", "Player to Win First Set"],
    "baseball": ["Total Runs Over/Under", "Home Team Win", "Away Team Win"],
    "hockey": ["First Period Winner", "Total Goals Over/Under", "Both Teams to Score"],
}

# Generate dummy users with specific user IDs
def generate_dummy_users(n=10):
    users = []
    # Predefined user IDs to ensure they exist
    predefined_user_ids = [1001, 1002, 1234, 5678, 9101]  # You can specify any user IDs you want
    for user_id in predefined_user_ids[:n]:  # Limit to n users
        users.append({
            "user_id": user_id,
            "name": fake.name(),
            "favorite_sport": random.choice(SPORTS)
        })
    return users

# Generate betting events (some in the past, some in the future)
def generate_dummy_events():
    events = []
    for sport, bets in BET_TYPES.items():
        for bet in bets:
            event_date = fake.date_time_between(start_date="-10d", end_date="+10d")  # Some past, some future
            events.append({
                "sport": sport,
                "bet_type": bet,
                "event_date": event_date.strftime("%Y-%m-%d %H:%M:%S")  # Convert datetime to string
            })
    return events

# Generate data
dummy_users = generate_dummy_users(5)  # Adjust n as needed
dummy_events = generate_dummy_events()

# Optional: Print to verify generated data
print("Dummy Users:", dummy_users)
print("Dummy Events:", dummy_events[:5])  # Show only the first 5 events for preview
