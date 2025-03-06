import os
import json
import requests

from dotenv import load_dotenv
load_dotenv(".env")


class WhatsappWrapper:

    API_URL = 'https://graph.facebook.com/v22.0/'
    WHATSAPP_API_TOKEN = os.getenv('WHATSAPP_API_TOKEN')
    WHATSAPP_CLOUD_NUMBER_ID = os.getenv('WHATSAPP_CLOUD_NUMBER_ID')

    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {self.WHATSAPP_API_TOKEN}",
            "Content-Type": "application/json"
        }
        self.API_URL = f"{self.API_URL}{self.WHATSAPP_CLOUD_NUMBER_ID}"

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
            f"{self.API_URL}/messages", 
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
            f"{self.API_URL}/messages", 
            headers=self.headers, 
            json=payload
        )

        assert response.status_code == 200, "Error sending message"
        return response.status_code

    def send_interactive_message(self, phone_number):
        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": "Choose an option:"
                },
                "action": {
                    "buttons": [
                        {"type": "reply", "reply": {"id": "button1", "title": "Option 1"}},
                        {"type": "reply", "reply": {"id": "button2", "title": "Option 2"}},
                    ]
                }
            }
        }

        response = requests.post(
            f"{self.API_URL}/messages", 
            headers=self.headers, 
            json=payload
        )

        assert response.status_code == 200, "Error sending message"
        return response.status_code
    
    def get_text_message(self, data):

        print("data: ", data)

        try:
            change = data["entry"][0]["changes"][0]["value"]

            if "messages" in change:
                message = change["messages"][0]
                if message["type"] == "text":
                    return {
                        "status_code": 200,
                        "from_no": message["from"],
                        "message": message["text"]["body"],
                        "isBase64Encoded": False
                    }
                else:
                    return {
                        "status_code": 200,
                        "message": json.dumps("Invalid message type"),
                        "isBase64Encoded": False
                    }
            elif "statuses" in change:
                status = change["statuses"][0]
                return {
                    "status_code": 200,
                    "message": json.dumps("status notification received"),
                    "isBase64Encoded": False
                }
            else:
                return {
                    "status_code": 200,
                    "message": json.dumps("Invalid message type"),
                    "isBase64Encoded": False
                }

        except (KeyError, IndexError) as e:
            return {
                "status_code": 500,
                "message": json.dumps(f"Error processing webhook data: {str(e)}"),
                "isBase64Encoded": False
            }

    
# if __name__ == "__main__":
#     client = WhatsappWrapper()
    # client.send_template_message("hello_world", "en_US", "6281918148130")
    # client.send_interactive_message("6281918148130")
    # client.send_text_message("halo", "6281918148130")
