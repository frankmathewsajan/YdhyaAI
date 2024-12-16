import requests

# Define the URL and API key
url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"
api_key = "AIzaSyAarh80ROw6uiSTAzqd7joDjaexdloTork"

start_text = """
You are a medical assistant AI designed to analyze detailed medical reports and provide a structured analysis, insights, and recommendations.

Here is a sample medical report:
"""
# Define the payload
payload = {
    "contents": [
        {
            "parts": [
                {
                    "text": f"Explain how AI works"
                }
            ]
        }
    ]
}

# Define the headers
headers = {
    "Content-Type": "application/json"
}

# Make the POST request
response = requests.post(f"{url}?key={api_key}", json=payload, headers=headers)

# Check the response
if response.status_code == 200:
    print("Response:", response.json())
else:
    print(f"Error: {response.status_code}")
    print("Message:", response.text)
