import json
import requests

from app.core import settings


class WhatsappWrapper:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_API_TOKEN}",
            "Content-Type": "application/json"
        }

    def send_template_message(self, template_name, language_code, phone_number):
        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": language_code
                }
            }
        }

        response = requests.post(
            f"{settings.API_URL_WHATSAPP}/messages", 
            headers=self.headers, 
            json=payload
        )

        assert response.status_code == 200, "Error sending message"
        return response.status_code
    
    def send_text_message(self, message, phone_number):
        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": message
            }
        }

        response = requests.post(
            f"{settings.API_URL_WHATSAPP}/messages", 
            headers=self.headers, 
            json=payload
        )

        assert response.status_code == 200, "Error sending message"
        return response.status_code

    def send_interactive_message(self, text, phone_number):
        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": text
                },
                "action": {
                    "buttons": [
                        {"type": "reply", "reply": {"id": "button1", "title": "assessment"}},
                        {"type": "reply", "reply": {"id": "button2", "title": "konsultasi"}},
                    ]
                }
            }
        }

        response = requests.post(
            f"{settings.API_URL_WHATSAPP}/messages", 
            headers=self.headers, 
            json=payload
        )

        assert response.status_code == 200, "Error sending message"
        return response.status_code
    
    def get_text_message(self, data):

        # print("data: ", data)

        try:
            contacts = data["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
            message = data["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"]

            return {
                "status_code": 200,
                "from_no": contacts,
                "message": message,
                "isBase64Encoded": False
            }

        except (KeyError, IndexError) as e:
            return {
                "status_code": 500,
                "message": json.dumps(f"Error processing webhook data: {str(e)}"),
                "isBase64Encoded": False
            }
