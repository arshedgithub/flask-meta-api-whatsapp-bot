from flask import Flask, request
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
RECIPIENT_PHONE_NUMBER = os.getenv("RECIPIENT_PHONE_NUMBER")
# VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

@app.route('/')
def home():
    return 'Whatsapp Bot deployed Successfully!'

url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}
message = "Hello! Whatsapp Bot was build..."
data = {
    "messaging_product": "whatsapp",
    "to": RECIPIENT_PHONE_NUMBER,
    "type": "text",
    "text": {
        "body": message
    }
}

response = requests.post(url, headers=headers, json=data)
print(response.status_code, response.text)

