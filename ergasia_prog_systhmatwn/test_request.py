import requests
import json

# API URL
url = "http://127.0.0.1:5000/recommend"

# Sample JSON request data
payload = {
    "user_id": 1234
}

# Send POST request
response = requests.post(url, json=payload)

# Print response status code and content
print("Status Code:", response.status_code)

# Attempt to print the response JSON
try:
    response_json = response.json()  # Attempt to parse JSON
    print("Response JSON:", json.dumps(response_json, indent=4))
except ValueError as e:
    print("Response content is not JSON:", response.text)  # Print raw response if it's not JSON
