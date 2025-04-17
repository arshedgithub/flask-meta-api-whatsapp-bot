from flask import Flask, request, jsonify
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

DIFY_API_KEY = os.getenv("DIFY_API_KEY")
DIFY_URL = os.getenv("DIFY_URL")

user_sessions = {}

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
        from_number = message['from']
        user_input = message['text']['body'].strip().lower()
        
        # DIFY integration
        conversation_id = user_sessions.get(from_number, "")

        dify_payload = {
            "inputs": {},
            "query": user_input,
            "response_mode": "blocking",
            "conversation_id": conversation_id,
            "user": from_number,
            "files": []
        }
        dify_headers = {
            "Authorization": f"Bearer {DIFY_API_KEY}",
            "Content-Type": "application/json"
        }

        # if text in ["hi", "hello"]:
        #     reply_text = "Hi there! 👋 How can I help you today?"
        #     send_whatsapp_message(from_number, reply_text)
        # else:
        #     send_whatsapp_message(from_number, "Hello! I am whastapp Bot. Ask any Question!")
            
        try:
            response = requests.post(DIFY_URL, headers=dify_headers, json=dify_payload)
            data = response.json()

            new_convo_id = data.get("conversation_id")
            if new_convo_id:
                user_sessions[from_number] = new_convo_id

            answer = data.get("answer", "Sorry! I didn't understand that.")
            send_whatsapp_message(from_number, answer)

        except Exception as e:
            print("Error:", e)
            send_whatsapp_message(from_number, "There was an error contacting the AI service.")
            
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
