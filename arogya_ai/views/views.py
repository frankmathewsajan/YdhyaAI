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
    query = request.GET.get('q', '')  # Get the 'q' parameter with empty string as default
    context = {'query': query}  # Create context dictionary with the query
    return render(request, 'arogya_ai/ai.html', context)


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
You are Arogya Medicine Assistant, a helpful AI chatbot specialized in providing information about medications, treatments, and general medical advice. 

As a medicine assistant, you can:
1. Provide information about medications, including dosages, side effects, and interactions
2. Explain differences between generic and brand-name drugs
3. Offer general guidance on common health conditions and treatments
4. Help users understand their prescriptions
5. Provide information about drug classifications and uses
"""

end_text = """
When responding to questions:
- Offer clear, concise information about medications and treatments
- Provide factual, evidence-based medical information
- Include relevant details about dosage, side effects, and drug interactions when applicable
- Explain medical terminology in simple language
- Always acknowledge your limitations as an AI assistant
- Recommend consulting healthcare professionals for personalized medical advice, diagnoses, or emergencies
- Format your responses in an easy-to-read way with clear sections when appropriate

When analyzing prescriptions:
- Identify medication names, dosages, and instructions
- Explain what each medication is used for in simple terms
- Highlight important information about timing and administration
- Note potential side effects or interactions patients should be aware of
- Organize information in a clear, structured format


Remember to maintain a helpful, conversational tone while providing accurate information about medicines and treatments.
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
