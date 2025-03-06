import os
import logging

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from app.wa_wrapper import WhatsappWrapper

from dotenv import load_dotenv
load_dotenv(".env")


app = FastAPI()


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/webhook")
def subscribe(request: Request):
    
    logging.info("subscribe is being called")

    if request.query_params.get("hub.verify_token") == os.getenv("VERIFY_TOKEN"):
        return int(request.query_params.get("hub.challenge"))
    
    # logging.error("subscribe is being called with invalid token")
    return {"error": "Invalid token"}


@app.post("/webhook")
async def send_response(request: Request):
    client = WhatsappWrapper()

    data = await request.json()
    logging.info("receive data")

    response = client.get_text_message(data)
    if response["status_code"] == 200:
        # if response["from_no"] and response["message"]:
        client.send_text_message(response["message"].upper(), response["from_no"])

        logging.info(f"Message sent to {response['from_no']} with message {response['message']}")

    return jsonable_encoder(content={"status": "success"}, status_code=200)
