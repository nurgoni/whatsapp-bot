import logging

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.services.whatsapp import WhatsappGAD
from app.core import settings


router = APIRouter(
    prefix="/webhook",
    tags=["webhook"],
)
client = WhatsappGAD()

@router.get("/webhook")
def subscribe(request: Request):

    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    
    if mode and token:
        if mode == "subscribe" and token == settings.VERIFY_TOKEN:
            logging.info("WEBHOOK VERIFIED")
            return JSONResponse(content={"status": "success"}, status_code=200)
        else:
            logging.info("WEBHOOK NOT VERIFIED")
            return JSONResponse(content={
                "status": "error", 
                "message": "Verfication Failed"
            }, status_code=403)
    else:
        logging.info("MISSING PARAMETERS")
        return JSONResponse(content={
            "status": "error", 
            "message": "Missing Parameters"
        }, status_code=400)


@router.post("/webhook")
async def send_response(request: Request):

    data = await request.json()
    logging.info(f"Received Payload: {data}")

    # user = data["entry"][0]["changes"][0]["value"]["contacts"][0][]
    # print(user)

    for entry in data.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})

            user = value["contacts"][0]["profile"]["name"]
            print("nama: ", user)

            if "messages" in value:
                message = value["messages"][0]
                sender = message["from"]

                if message["type"] == "text":
                    if sender in client.sessions:
                        client.send_message({
                            "messaging_product": "whatsapp",
                            "to": sender,
                            "type": "text",
                            "text": {"body": "Anda sedang dalam proses assessment. Silakan pilih opsi dari daftar untuk melanjutkan."}
                        })
                    else:
                        client.send_main_menu(sender, user)

                elif message["type"] == "interactive":
                    button_id = message["interactive"]["list_reply"]["id"]

                    if button_id == "assessment":
                        client.start_assessment(sender)
                    elif button_id == "consultation":
                        client.send_message({
                            "messaging_product": "whatsapp",
                            "to": sender,
                            "type": "text",
                            "text": {"body": "MAAF! Fitur konsultasi masih dalam pengembangan."}
                        })
                    else:
                        client.process_response(sender, button_id)
    
    return {"status": "received"}
