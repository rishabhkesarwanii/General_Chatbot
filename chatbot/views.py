from django.shortcuts import render, redirect
from django.http import JsonResponse
from openai import OpenAI


from django.contrib import auth
from django.contrib.auth.models import User
from .models import Chat

from django.utils import timezone
import os
import json
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .script import extract_details_from_image

API_KEY = str(settings.OPENAI_API_KEY)

client = OpenAI(api_key=API_KEY)

@csrf_exempt
def process_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        
        # Save the uploaded image temporarily
        temp_image_path = os.path.join(settings.MEDIA_ROOT, 'temp_image.png')
        with open(temp_image_path, 'wb+') as destination:
            for chunk in image.chunks():
                destination.write(chunk)
        
        # Process the image using your script
        details = extract_details_from_image(temp_image_path)
        print(details)
        formatted_details = f"Extracted Data:\nName: {details['Name']}\nDOB: {details['DOB']}\nAadhar Number: {details['Aadhar_Number']}"

        chat = Chat(user=request.user, message="Processed Aadhar Card", response=formatted_details, created_at=timezone.now())
        chat.save()
        
        # Delete the temporary image
        os.remove(temp_image_path)
        
        return JsonResponse({'message': 'Processed Aadhar Card', 'response': formatted_details})
    return JsonResponse({'error': 'No image uploaded'}, status=400)

# context = "Instruction :You are Recipe master you know everything and all about the recipes, You are a helpful assistant. Explicitly give [protein,fat,carbs,kcals,ingredients] dont give extra response give exact number only, EXACT NUMBERS ONLY when you give result protein,fat,carbs,kcals please give only number nothing else no units no keywords please like ""Approximately"" or ""nearly"" etc, in response You are a human. Instruction :You are Recipe master you know everything and all about the recipes Instruction: give response in only that schema nothing more, give ingredients properly like quantity  and whole output should be json hence containing key and value"
context = "You are a genral chatbot, always respond in proper hindi langauge"
def ask_openai(message):
    response = client.chat.completions.create(model = "gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": context},
        {"role": "user", "content": message},
    ])
    print(response)
    answer = response.choices[0].message.content.strip()
    return answer


def chatbot(request):
    chats = Chat.objects.filter(user=request.user)

    if request.method == 'POST':
        message = request.POST.get('message')
        response_data = ask_openai(message)

        chat = Chat(user=request.user, message=message, response=response_data, created_at=timezone.now())
        chat.save()

        # Return the response as JSON and also structure_response should also be a json in it self
        # return JsonResponse({'message': message, 'response': json.dumps(structured_response)})

        return JsonResponse({'message': message, 'response': response_data})
    return render(request, 'chatbot.html', {'chats': chats})


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('chatbot')
        else:
            error_message = 'Invalid username or password'
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            try:
                user = User.objects.create_user(username, email, password1)
                user.save()
                auth.login(request, user)
                return redirect('chatbot')
            except:
                error_message = 'Error creating account'
                return render(request, 'register.html', {'error_message': error_message})
        else:
            error_message = 'Password dont match'
            return render(request, 'register.html', {'error_message': error_message})
    return render(request, 'register.html')

def logout(request):
    auth.logout(request)
    return redirect('login')