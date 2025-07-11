# app.py - Complete WhatsApp Meta API Bot
from flask import Flask, request, jsonify
import google.generativeai as genai
import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Replace with actual key
META_VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN")
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
META_PHONE_NUMBER_ID = os.getenv("META_PHONE_NUMBER_ID")

# Base URL for Meta API
META_BASE_URL = f"https://graph.facebook.com/v19.0/{META_PHONE_NUMBER_ID}"

# Gemini Setup
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')  # Updated model name

# Agent Classes
class RestaurantAgent:
    def process(self, message):
        prompt = f"""
        You are a Pakistani restaurant assistant. Keep response under 100 words.
        Help with: food recommendations, restaurant suggestions, menu questions.
        
        User: {message}
        Reply in Roman Urdu, be helpful and friendly.
        """
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Restaurant agent error: {str(e)}"

class WeatherAgent:
    def process(self, message):
        prompt = f"""
        You are a Pakistani weather assistant. Keep response under 100 words.
        Help with: weather info, temperature, forecasts.
        
        User: {message}
        Reply in Roman Urdu, be helpful and friendly.
        """
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Weather agent error: {str(e)}"

class GeneralAgent:
    def process(self, message):
        prompt = f"""
        You are a helpful Pakistani assistant. Keep response under 100 words.
        Answer general questions in a friendly way.
        
        User: {message}
        Reply in Roman Urdu, be helpful and friendly.
        """
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"General agent error: {str(e)}"

# Agent Router
def get_agent(message):
    if not message:
        return GeneralAgent()
    
    message_lower = message.lower()
    
    # Restaurant keywords
    restaurant_words = ['food', 'khana', 'restaurant', 'menu', 'order', 'pizza', 'biryani', 'karahi', 'nihari', 'chai']
    if any(word in message_lower for word in restaurant_words):
        return RestaurantAgent()
    
    # Weather keywords  
    weather_words = ['weather', 'mausam', 'temperature', 'garmi', 'sardi', 'barish', 'dhoop', 'thanda']
    if any(word in message_lower for word in weather_words):
        return WeatherAgent()
    
    return GeneralAgent()

# Send WhatsApp Message Function
def send_whatsapp_message(phone_number, message):
    url = f"{META_BASE_URL}/messages"
    
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "text",
        "text": {
            "body": message
        }
    }
    
    headers = {
        "Authorization": f"Bearer {META_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        print(f"Sending message to {phone_number}: {message}")
        response = requests.post(url, json=payload, headers=headers)
        
        print(f"API Response Status: {response.status_code}")
        print(f"API Response Body: {response.text}")
        
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": response.text}
            
    except Exception as e:
        print(f"Exception sending message: {e}")
        return {"success": False, "error": str(e)}

# Webhook Verification (GET)
@app.route('/webhook', methods=['GET'])
def verify_webhook():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    print(f"Webhook verification - Mode: {mode}, Token: {token}")
    
    if mode == 'subscribe' and token == META_VERIFY_TOKEN:
        print("✅ Webhook verified successfully!")
        return challenge, 200
    else:
        print("❌ Webhook verification failed")
        return "Forbidden", 403

# Main Webhook Handler (POST)
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # Get the raw JSON data
        data = request.get_json()
        
        # Log the entire webhook payload
        print("=" * 50)
        print("📨 WEBHOOK RECEIVED:")
        print(json.dumps(data, indent=2))
        print("=" * 50)
        
        # Check if data exists
        if not data:
            print("❌ No data received")
            return jsonify({"status": "no_data"}), 400
        
        # Process webhook data
        if 'entry' in data:
            for entry in data['entry']:
                if 'changes' in entry:
                    for change in entry['changes']:
                        field = change.get('field')
                        value = change.get('value', {})
                        
                        print(f"📋 Processing field: {field}")
                        
                        # Handle messages
                        if field == 'messages' and 'messages' in value:
                            contacts = value.get('contacts', [])
                            messages = value.get('messages', [])
                            
                            for message in messages:
                                # Extract message details
                                message_id = message.get('id')
                                from_number = message.get('from')
                                message_type = message.get('type')
                                timestamp = message.get('timestamp')
                                
                                print(f"📱 Message from: {from_number}")
                                print(f"📝 Message type: {message_type}")
                                print(f"🆔 Message ID: {message_id}")
                                
                                # Process text messages only
                                if message_type == 'text':
                                    text_data = message.get('text', {})
                                    message_body = text_data.get('body', '')
                                    
                                    print(f"💬 Message content: {message_body}")
                                    
                                    # Skip empty messages
                                    if not message_body.strip():
                                        continue
                                    
                                    # Get appropriate agent
                                    agent = get_agent(message_body)
                                    agent_name = agent.__class__.__name__
                                    
                                    print(f"🤖 Using agent: {agent_name}")
                                    
                                    # Process with agent
                                    bot_response = agent.process(message_body)
                                    print(f"💭 Bot response: {bot_response}")
                                    
                                    # Send reply
                                    send_result = send_whatsapp_message(from_number, bot_response)
                                    
                                    if send_result['success']:
                                        print("✅ Message sent successfully!")
                                    else:
                                        print(f"❌ Failed to send message: {send_result['error']}")
                        
                        # Handle status updates
                        elif field == 'messages' and 'statuses' in value:
                            statuses = value.get('statuses', [])
                            for status in statuses:
                                print(f"📊 Status update: {status}")
        
        print("=" * 50)
        return jsonify({"status": "received"}), 200
        
    except Exception as e:
        print(f"💥 WEBHOOK ERROR: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "WhatsApp Meta + Gemini Bot",
        "phone_id": META_PHONE_NUMBER_ID,
        "version": "1.0"
    })

# Test webhook manually
@app.route('/test-webhook', methods=['POST'])
def test_webhook():
    """Test webhook with manual data"""
    test_data = {
        "entry": [{
            "changes": [{
                "field": "messages",
                "value": {
                    "messages": [{
                        "from": "1234567890",
                        "text": {"body": "test message"},
                        "type": "text",
                        "id": "test123"
                    }]
                }
            }]
        }]
    }
    
    print("🧪 Testing webhook with manual data...")
    
    # Process the test data through webhook function
    original_request = request
    
    class MockRequest:
        def get_json(self):
            return test_data
    
    # Temporarily replace request
    import flask
    flask.request = MockRequest()
    
    try:
        result = webhook()
        print("✅ Webhook test successful!")
        return jsonify({"status": "test_success", "result": "Webhook working"})
    except Exception as e:
        print(f"❌ Webhook test failed: {e}")
        return jsonify({"status": "test_failed", "error": str(e)})
    finally:
        # Restore original request
        flask.request = original_request

if __name__ == '__main__':
    print("🚀 Starting WhatsApp Bot Server...")
    print(f"📱 Phone Number ID: {META_PHONE_NUMBER_ID}")
    print(f"🔑 Verify Token: {META_VERIFY_TOKEN}")
    print("🌐 Server starting on port 5000...")
    print("📡 Use ngrok to expose: ngrok http 5000")
    app.run(debug=True, port=5000, host='0.0.0.0')

