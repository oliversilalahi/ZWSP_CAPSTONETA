from typing import Any
from fastapi import FastAPI, APIRouter, WebSocket
from pydantic import BaseModel
import logging
from contextlib import asynccontextmanager
from gmqtt import Client as MQTTClient
from fastapi_mqtt import FastMQTT, MQTTConfig
from dotenv import load_dotenv
import os

import zwsp
from .websocket_manager import ConnectionManager

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

# Membuat instance ConnectionManager untuk mengelola koneksi WebSocket
ws_manager = ConnectionManager()


class CodedMessage(BaseModel):
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
        "message": "hello from receiver"
    }


@router.post("/receive")
async def receive_message(msg: CodedMessage):
    """
    Endpoint untuk menerima dan mendekode pesan yang diterima melalui API.

    Parameters:
    msg (CodedMessage): Object CodedMessage yang berisi pesan yang disandikan.

    Returns:
    dict: Status penerimaan dan data pesan yang telah didesandikan.
    """

    # Mendekode pesan
    decoded_msg, carrier_msg = zwsp.decode(msg.message, zwsp.MODE_ZWSP)

    # Log informasi pesan untuk debugging
    # fmt: off
    logger.debug(f'\n Original message: {msg.message}\n Decoded secret message: {decoded_msg}')

    # Mempersiapkan data untuk dikirimkan melalui WebSocket
    data = {
            "encoded_message": msg.message,
            "decoded_message": carrier_msg+decoded_msg,
            "hidden_message":decoded_msg,
            "carrier_message": carrier_msg,
    }

    # Mengirimkan data ke semua koneksi WebSocket yang terhubung
    await ws_manager.broadcast_json(data)

    return {
        "status" : "received",
        "data" : data,
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

@fast_mqtt.on_message()
async def receive_message_mqtt(client: MQTTClient, topic: str, payload: bytes, qos:int, properties: Any):
    """
    Callback yang dipanggil ketika pesan diterima dari broker MQTT.

    Parameters:
    client (MQTTClient): Object client MQTT.
    topic (str): Topik pesan.
    payload (bytes): Isi pesan.
    qos (int): Kualitas layanan pesan.
    properties (Any): Properti pesan.

    Returns:
    None
    """

    # Mendekode payload dari bytes ke string
    msg = payload.decode()
    logger.info(f"Received message: {topic} | {msg} | {qos} | {properties}")

    # Mendekode pesan yang dienkode menggunakan ZWSP
    hidden_msg, carrier_msg = zwsp.decode(msg, zwsp.MODE_ZWSP)
    decoded_msg = carrier_msg+hidden_msg

    # Mempersiapkan data untuk dikirimkan melalui WebSocket
    # fmt: off
    data = {
            "encoded_message": msg,
            "decoded_message":decoded_msg,
            "hidden_message":hidden_msg,
            "carrier_message": carrier_msg,
    }

    # Log informasi pesan untuk debugging
    logger.debug(f'\nencoded_message: {msg}\ndecoded_message: {decoded_msg}\nhidden_message: {hidden_msg}\ncarrier_message: {carrier_msg}')

    # Mengirimkan data (dalam bentuk json) ke semua koneksi WebSocket yang terhubung
    await ws_manager.broadcast_json(data)

@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    """
    Endpoint untuk menangani koneksi WebSocket.

    Parameters:
    ws (WebSocket): Koneksi WebSocket yang diterima.

    Returns:
    None
    """
    await ws_manager.connect(ws) # Menerima koneksi WebSocket
    try:
        # infinite loop diterapkan agar koneksi dua arah tetap terjaga
        while True:
            await ws.receive() # Menunggu pesan dari WebSocket
    except:
        ws_manager.disconnect(ws) # Menghapus koneksi WebSocket jika terjadi kesalahan atau koneksi ditutup

# Menyertakan router dalam aplikasi FastAPI
app.include_router(router)