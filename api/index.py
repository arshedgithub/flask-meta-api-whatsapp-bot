from flask import Flask, request, jsonify
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
RECIPIENT_PHONE_NUMBER = os.getenv("RECIPIENT_PHONE_NUMBER")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

@app.route('/')
def home():
    return 'Whatsapp Bot deployed Successfully!'

# webhook verification route 
@app.route('/webhooks', methods=['GET'])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("WEBHOOK_VERIFIED")
            return challenge, 200
        else:
            return "Forbidden", 403
        
# listening
@app.route('/webhooks', methods=['POST'])
def receive_message():
    data = request.get_json()
    print("Received webhook:", data)

    try:
        message = data['entry'][0]['changes'][0]['value']['messages'][0]
        phone_number = message['from']
        text = message['text']['body'].strip().lower()

        if text in ["hi", "hello"]:
            reply_text = "Hi there! 👋 How can I help you today?"
            send_whatsapp_message(phone_number, reply_text)
        else:
            send_whatsapp_message(phone_number, "Hello! I am whastapp Bot. Ask any Question!")
            
    except Exception as e:
        print("No text message or error:", e)

    return jsonify(success=True)


def send_whatsapp_message(to, message):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {
            "body": message
        }
    }
    
    response = requests.post(url, headers=headers, json=data)
    print(response.status_code, response.text)
        
        
if __name__ == "__main__":
    app.run(debug=True)
