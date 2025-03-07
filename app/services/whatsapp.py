import json
import requests

from app.services.openai import OpenAIWrapper
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


class WhatsappGAD:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_API_TOKEN}",
            "Content-Type": "application/json"
        }

        self.list_questions_gad = [
            "Merasa gugup, cemas, atau sangat tegang?",
            "Tidak dapat menghentikan atau mengendalikan rasa khawatir?",
            "Khawatir terlalu banyak mengenai berbagai hal?",
            "Sulit untuk rileks?",
            "Sangat gelisah sehingga sulit untuk duduk diam?",
            "Mudah marah atau mudah terganggu?",
            "Merasa takut seakan-akan sesuatu yang buruk akan terjadi?"
        ]

        self.sessions = {}
        self.chatgpt = OpenAIWrapper()

    def send_message(self, payload):
        response = requests.post(
            f"{settings.API_URL_WHATSAPP}/messages",
            headers=self.headers,
            json=payload
        )
        assert response.status_code == 200, "Error sending message"
        return response.json()
    
    def send_main_menu(self, phone_number, user="User"):
        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "header": {"type": "text", "text": f"Halo... {user}"},
                "body": {
                    "text": "Ada yang bisa saya bantu?\nPilih salah satu opsi berikut:"
                },
                "action": {
                    "button": "Select",
                    "sections": [{
                        "title": "Options",
                        "rows": [
                            {"id": "assessment", "title": "Assessment"},
                            {"id": "consultation", "title": "Konsultasi"},
                        ]
                    }]
                }
            }
        }
        return self.send_message(payload)

    def send_interactive_message(self, text, phone_number):

        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "header": {"type": "text", "text": "Assessment"},
                "body": {
                    "text": f"Selama 2 minggu terakhir, seberapa sering Anda mengalami gejala berikut:\n\n*{text}*"
                },
                "action": {
                    "button": "Select",
                    "sections": [{
                        "title": "Options",
                        "rows": [
                            {"id": "0", "title": "Tidak Pernah"},
                            {"id": "1", "title": "Beberapa Hari"},
                            {"id": "2", "title": "Seminggu Lebih"},
                            {"id": "3", "title": "Hampir Setiap Hari"}
                        ]
                    }]
                }
            }
        }
        return self.send_message(payload)

    def start_assessment(self, phone_number):
        """Initialize assessment session and send the first question"""
        self.sessions[phone_number] = {
            "current_question": 0,
            "total_score": 0,
            "mode": "assessment"
        }
        self.send_interactive_message(self.list_questions_gad[0], phone_number)

    def process_response(self, phone_number, button_id):
        """Process the user’s answer and send the next question"""
        if phone_number not in self.sessions:
            return self.send_main_menu(phone_number)  # Restart if session lost

        session = self.sessions[phone_number]

        # Store user score
        session["total_score"] += int(button_id)

        # Move to the next question
        session["current_question"] += 1

        if session["current_question"] < len(self.list_questions_gad):
            # Send next question
            next_question = self.list_questions_gad[session["current_question"]]
            self.send_interactive_message(next_question, phone_number)
        else:
            # Assessment Completed - Send Final Score
            final_score = session["total_score"]
            self.send_message({
                "messaging_product": "whatsapp",
                "to": phone_number,
                "type": "text",
                "text": {
                    "body": f"Tes selesai! Skor akhir Anda: {final_score}\n"
                            "Interpretasi:\n"
                            "0-4: Tidak ada kecemasan\n"
                            "5-9: Kecemasan ringan\n"
                            "10-14: Kecemasan sedang\n"
                            "15-21: Kecemasan berat"
                }
            })
            del self.sessions[phone_number]  # Remove session after completion

    def start_consultation(self, phone_number):
        self.sessions[phone_number] = {
            "mode": "consultation"
        }
        self.send_message({
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "text",
            "text": {
                "body": "Hai!, saya adalah teman kamu yang siap mendengar perasaanmu hari ini. Bagaimana perasaanmu sekarang? Saya sangat tertarik mendengar-nya."
            }
        })

    def process_consultation(self, phone_number, user_input):
        if phone_number in self.sessions and self.sessions[phone_number]["mode"] == "consultation":
            if user_input.strip().lower() == "selesai":
                del self.sessions[phone_number]
                self.send_message({
                    "messaging_product": "whatsapp",
                    "to": phone_number,
                    "type": "text",
                    "text": {
                        "body": "Terima kasih telah berkonsultasi dengan saya. Semoga perasaanmu menjadi lebih baik."
                    }
                })
            else:
                response = self.chatgpt.get_openai_response(user_input)
                self.send_message({
                    "messaging_product": "whatsapp",
                    "to": phone_number,
                    "type": "text",
                    "text": {
                        "body": response
                    }
                })
    