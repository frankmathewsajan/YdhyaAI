import json
import os

import requests
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
def index(request):
    if request.user.is_authenticated:
        return render(request, 'index.html')
    return render(request, 'welcome.html')


def telemedicine(request):
    return render(request, 'arogya_ai/features/telemedicine.html')


def ai(request):
    return render(request, 'arogya_ai/ai.html')


def booking(request):
    return render(request, 'arogya_ai/features/booking.html')


def payment(request):
    return render(request, 'arogya_ai/features/payment.html')


def ocr(request):
    return render(request, 'arogya_ai/features/ocr.html')


def advice(request):
    return render(request, 'arogya_ai/features/advice.html')


def search(request):
    return render(request, 'arogya_ai/features/search.html')


def reminder(request):
    return render(request, 'arogya_ai/features/reminder.html')


@login_required
def setup(request):
    if request.method == 'POST':
        redirect('index')
    return render(request, 'user/setup.html')


@csrf_exempt
def get_generic_name(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            query = body.get("query", "").lower()
            # Fetch response using external API
            medicine_db = get_response(50,
                                       f"{query}, fix the spelling of the medicine, what is its generic name  in FDA "
                                       f"and RxNorm, give response in json format like, key = 'query', "
                                       f"value = 'generic name'",
                                       t='null')
            print(medicine_db)
            # Extract the generic name from the API response
            medicine_db = json.loads(medicine_db.replace("```json\n", "").replace("```", "")).trim()
            print(0, medicine_db)
            generic_name = medicine_db.get(query, "Unknown")
            print(generic_name)
            return JsonResponse({"generic_name": generic_name})

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)  # Catch any other unexpected errors
    return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt
def chat(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')

            # Generate a response
            bot_response = get_response(50, user_message)

            return JsonResponse({"response": bot_response})
        except Exception as e:
            # Convert exception to a string for JSON serialization
            return JsonResponse({"response": str(e)}, status=500)


start_text = """
You are a medical assistant AI designed to analyze detailed medical reports and provide a structured analysis, insights, and recommendations.

Here is a sample medical report:
"""

end_text = """
Using the provided data, please:

Summarize the patient’s condition, including significant symptoms, medical history, and abnormal findings.
Highlight abnormal test results or vitals and explain their clinical relevance.
Suggest possible diagnoses based on the patient's symptoms, history, and test results.
Recommend additional tests, procedures, or referrals required for further evaluation.
Propose treatment plans, including lifestyle changes, medication adjustments, or specialist consultations.
Ensure your response is structured, professional, and easy for healthcare providers to understand."

Sample Response Format:

Summary:
Brief overview of the patient's condition.

Key Abnormalities:
List of abnormal findings with explanations.

Possible Diagnoses:
Differential diagnoses with reasoning.

Recommended Actions:
Tests, procedures, or referrals.

Treatment Plan:
Specific recommendations, including medications and lifestyle changes.
"""


def get_response(length, prompt="", t='arogya_ai'):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"
    api_key = os.getenv("API_KEY")
    text = f"{start_text}\n {prompt} \n{end_text}" if t == 'arogya_ai' else f"{prompt}"
    # Define the payload
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": text
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
        resp = response.json()
        try:
            # Validate and extract the text from the response
            return resp['candidates'][0]['content']['parts'][0]['text']
        except (KeyError, IndexError) as e:
            # Log the malformed response
            print("Malformed response:", resp)
            raise KeyError("Malformed API response structure.") from e
    else:
        # Handle non-200 status codes
        print(f"Error: {response.status_code}")
        print("Message:", response.text)
        raise ValueError(f"API error: {response.status_code} - {response.text}")
