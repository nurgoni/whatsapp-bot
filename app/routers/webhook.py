import logging

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from app.services.whatsapp import WhatsappWrapper
from app.core import settings


router = APIRouter(
    prefix="/webhook",
    tags=["webhook"],
)


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
    client = WhatsappWrapper()

    data = await request.json()
    logging.info("receive data")

    response = client.get_text_message(data)
    if response["status_code"] == 200:
        # if response["from_no"] and response["message"]:
        client.send_interactive_message(response["message"].upper(), response["from_no"])

        logging.info(f"Message sent to {response['from_no']} with message {response['message']}")

    return JSONResponse(content={"status": "success"}, status_code=200)
