import requests

from app.core import settings


class OpenAIWrapper:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }

    def get_openai_response(self, user_input):

        prompt = f"""
        # siapa anda
        Anda adalah seorang ai assistant yang bertugas untuk memahami emosi patient yang sedang mengalami permasalahan mental health. 
        Anda akan menggunakan metode Cognitive Behavioural Therapy untuk memberikan response.

        pesan chat dari user adalah: {user_input}

        # tugas
        identifikasi pesan tersebut menyampaikan emosi yang seperti apa, kemudian jawab dengan metode Cognitive Behavioural Therapy.

        # gaya bahasa response jawaban
        Gunakan bahasa yang friendly seperti teman dan jangan terlalu baku. Berikan response dengan gaya bahasa yang penuh rasa empati dan menanangkan. Jangan menggunakan bahasa yang terlalu berlebihan, usahakan untuk selalu netral dan tidak menghakimi.

        # batasan
        Jangan meresponse pesan yang tidak terkait dengan permasalahan mental health. Jawab dengan sopan dan jelaskan kenapa anda tidak bisa menjawab pesan tersebut.

        """

        payload = {
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_input}
            ]
        }

        response = requests.post(
            settings.API_URL_OPENAI, 
            headers=self.headers, 
            json=payload
        )

        if response.status_code == 200:
            ai_response = response.json()["choices"][0]["message"]["content"]
            return f"{ai_response}\n\n🔹 *Ketik 'SELESAI' untuk mengakhiri konsultasi.*"
        else:
            return "Maaf, ada masalah dalam mendapatkan jawaban. Silakan coba lagi nanti."
