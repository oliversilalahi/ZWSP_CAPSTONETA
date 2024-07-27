from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from typing import Any
from pydantic import BaseModel
import logging
from contextlib import asynccontextmanager
from gmqtt import Client as MQTTClient
from fastapi_mqtt import FastMQTT, MQTTConfig
from dotenv import load_dotenv
import os
import random
from firebase_admin import credentials, initialize_app, db
from pathlib import Path

import zwsp

# Load variabel environment dari file .env
load_dotenv(override=True)

# Mengatur logger untuk debugging
logger = logging.getLogger('uvicorn.error')
logger.setLevel(logging.DEBUG)

# Konfigurasi MQTT
mqtt_config = MQTTConfig(
    host=os.getenv("MQTT_HOST", "0.0.0.0"),
    port=int(os.getenv("MQTT_PORT", 1883)),
    keepalive=60,
    username=os.getenv("MQTT_USERNAME", "admin"),
    password=os.getenv("MQTT_PASSWORD", "hivemq"),
    ssl=False,
)

fast_mqtt = FastMQTT(config=mqtt_config)

fb_creds_loc = Path('firebase_service_account.json').resolve()
cred = credentials.Certificate(fb_creds_loc)
fb_default_app = initialize_app(cred, {
    'databaseURL': os.getenv('FIREBASE_DB_URL')
})
db_ref = db.reference('/Temp')


@asynccontextmanager
async def _lifespan(_app: FastAPI):
    """
    Mengelola life-cycle aplikasi FastAPI untuk memulai dan menghentikan koneksi MQTT.

    Parameters:
    _app (FastAPI): Aplikasi FastAPI.

    Yields:
    None
    """
    await fast_mqtt.mqtt_startup()
    yield
    await fast_mqtt.mqtt_shutdown()

# Membuat instance aplikasi FastAPI dengan pengelola life-cycle
app = FastAPI(lifespan=_lifespan)
router = APIRouter()


class Message(BaseModel):
    """
    Model data untuk pesan yang diterima melalui API.
    """
    message: str


@router.get("/")
def index():
    """
    Endpoint dasar untuk mengecek status API.

    Returns:
    dict: Pesan status server.
    """
    return {
        "message": "hello from sender"
    }


@router.post("/send")
def send_message(msg: Message):
    """
    Endpoint untuk mengirim pesan melalui MQTT dengan menyembunyikan pesan rahasia di dalamnya yang diencode menggunakan ZWSP.

    Parameters:
    msg (Message): Object Message yang berisi pesan asli.

    Returns:
    dict: Status pengiriman dan data pesan.
    """
    original_msg = msg.message

    data = db_ref.order_by_child('timestamp').limit_to_last(1).get()
    hidden_msg = ''
    for doc in data:
        hidden_msg = str(int(data[doc]['temperature']))
        break

    # fmt: off
    encoded_hidden_msg = zwsp.encode(hidden_msg, zwsp.MODE_ZWSP) # Mengenkripsi pesan rahasia
    assemble_msg = f'{original_msg}{encoded_hidden_msg}' # Menggabungkan pesan asli dengan pesan rahasia

    # fmt: off
    logger.debug(f'\n original: {original_msg} \n hidden: {hidden_msg} \n encoded: {assemble_msg} \n actual: {original_msg+hidden_msg}') # Log informasi pesan untuk debugging

    # Mengirimkan pesan yang telah disandikan melalui MQTT
    fast_mqtt.publish("zwsp", assemble_msg)

    return {
        "status" : "sent",
        "data" : {
            "original_message" : original_msg,
            "encoded_message" : assemble_msg,
        }
    }

@fast_mqtt.on_connect()
def connect(client: MQTTClient, flags: int, rc: int, properties: Any):
    """
    Callback yang dipanggil ketika terhubung ke broker MQTT.

    Parameters:
    client (MQTTClient): Object cliet MQTT.
    flags (int): Flag koneksi.
    rc (int): Kode hasil koneksi.
    properties (Any): Property koneksi.

    Returns:
    None
    """
    client.subscribe("zwsp") # Subscribe ke topik yg berjudul "zwsp"
    logger.info(f"Connected: {client} | {flags} | {rc}, | {properties}")

@fast_mqtt.on_disconnect()
def disconnect(client: MQTTClient, packet, exc=None):
    """
    Callback yang dipanggil ketika terputus dari broker MQTT.

    Parameters:
    client (MQTTClient): Object client MQTT.
    packet: Paket yang diterima saat terputus.

    Returns:
    None
    """
    logger.info("MQTT disconnected")


# Menambahkan middleware CORS untuk mengizinkan semua source dan metode HTPP
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Menyertakan router dalam aplikasi FastAPI
app.include_router(router)

