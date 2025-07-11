# META AI AGENT

This project is a Flask-based WhatsApp chatbot that uses Google Gemini AI to generate intelligent replies for restaurant-related queries. It integrates with the WhatsApp Cloud API to send and receive messages.

---

## Features
- WhatsApp webhook for receiving and sending messages
- Google Gemini AI integration for smart replies
- Environment-based configuration
- Modular code structure

---

## Folder Structure
```
META AI AGENT/
├── agents/
│   └── restaurant_agent.py
├── app.py
├── requirements.txt
├── utils/
│   └── verify.py
└── README.md
```

---

## Setup Instructions

### 1. Clone the Repository
```sh
git clone <your-repo-url>
cd "META AI AGENT"
```

### 2. Create and Activate Virtual Environment (Recommended)
```sh
python -m venv venv
venv\Scripts\activate  # On Windows
# Or
source venv/bin/activate  # On Mac/Linux
```

### 3. Install Dependencies
```sh
pip install -r requirements.txt
```

### 4. Environment Variables
Create a `.env` file in the project root with the following variables:
```
META_VERIFY_TOKEN=your_webhook_verify_token
META_ACCESS_TOKEN=your_whatsapp_cloud_api_access_token
META_PHONE_NUMBER_ID=your_whatsapp_phone_number_id
GEMINI_API_KEY=your_google_gemini_api_key
```

- **META_VERIFY_TOKEN:** Used for webhook verification with WhatsApp.
- **META_ACCESS_TOKEN:** WhatsApp Cloud API access token.
- **META_PHONE_NUMBER_ID:** Your WhatsApp business phone number ID.
- **GEMINI_API_KEY:** Google Gemini API key for AI responses.

### 5. WhatsApp Cloud API Setup
- Go to [Meta for Developers](https://developers.facebook.com/).
- Set up a WhatsApp Cloud API app.
- Add your phone number to the "recipient list" in the WhatsApp Cloud API dashboard (sandbox mode only allows sending to verified numbers).
- Use the provided access token and phone number ID in your `.env` file.

### 6. Google Gemini API Setup
- Go to [Google Cloud Console](https://console.cloud.google.com/).
- Enable the Gemini API and create an API key.
- Add the API key to your `.env` file as `GEMINI_API_KEY`.

---

## Running the App

**Always run from the project root directory:**

```sh
python -m app
```

If you get import errors, try adding this to the top of `app.py`:
```python
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
```

---

## Webhook Endpoint
- **GET /webhook**: For WhatsApp webhook verification.
- **POST /webhook**: Receives messages from WhatsApp, processes them, and sends replies.

---

## Troubleshooting

### Gemini API Error: `API key not valid. Please pass a valid API key.`
- Make sure your `.env` file has the correct `GEMINI_API_KEY`.
- Ensure your Google Cloud project has the Gemini API enabled.

### WhatsApp API Error: `Recipient phone number not in allowed list`
- Add your test phone number to the recipient list in the WhatsApp Cloud API dashboard and verify it.

---

## License
This project is for educational/demo purposes. Please check the licenses of the APIs you use. 