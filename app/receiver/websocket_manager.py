from fastapi import WebSocket
from typing import List


class ConnectionManager:
    """
    Kelas untuk mengelola koneksi WebSocket.
    """

    def __init__(self):
        """
        Inisialisasi objek ConnectionManager.
        """

        # Konstruktor `__init__` menginisialisasi active_connections sebagai daftar kosong untuk menyimpan koneksi WebSocket yang aktif.
        self.active_connections: List[WebSocket] = []

    async def connect(self, ws: WebSocket):
        """
        Menerima dan menambahkan koneksi WebSocket baru.

        Parameters:
        ws (WebSocket): Koneksi WebSocket yang diterima.

        Returns:
        None
        """

        # await `ws.accept()` digunakan untuk menerima koneksi WebSocket.
        await ws.accept()
        # Koneksi yang diterima ditambahkan ke daftar `active_connections`
        self.active_connections.append(ws)

    async def send_text(self, ws: WebSocket, msg: str):
        """
        Mengirim pesan teks melalui WebSocket.

        Parameters:
        ws (WebSocket): Koneksi WebSocket.
        msg (str): Pesan teks yang akan dikirim.

        Returns:
        None
        """

        # `await ws.send_text(msg)` digunakan untuk mengirim pesan teks.
        await ws.send_text(msg)

    async def send_json(self, ws: WebSocket, json_str_msg: str):
        """
        Mengirim pesan JSON melalui WebSocket.

        Parameters:
        ws (WebSocket): Koneksi WebSocket.
        json_str_msg (str): Pesan berbentuk data JSON yang akan dikirim.

        Returns:
        None
        """

        # await` ws.send_json(json_str_msg)` digunakan untuk mengirim pesan berformat JSON.
        await ws.send_json(json_str_msg)

    async def broadcast_text(self, msg: str):
        """
        Menyiarkan pesan teks ke semua koneksi WebSocket yang aktif.

        Parameters:
        msg (str): Pesan teks yang akan disiarkan.

        Returns:
        None
        """

        #  Bagian ini mengiterasi semua koneksi dalam `active_connections` dan mengirim pesan teks ke setiap koneksi menggunakan `await self.send_text(conn, msg)`.
        for conn in self.active_connections:
            await self.send_text(conn, msg)

    async def broadcast_json(self, json_str_msg: str):
        """
        Menyiarkan pesan berbentuk data JSON ke semua koneksi WebSocket yang aktif.

        Parameters:
        json_str_msg (str): Pesan JSON yang akan disiarkan.

        Returns:
        None
        """

        # Bagian ini mengiterasi semua koneksi dalam active_connections dan mengirim pesan berformat JSON ke setiap koneksi menggunakan `await self.send_json(conn, json_str_msg)`.
        for conn in self.active_connections:
            await self.send_json(conn, json_str_msg)

    def disconnect(self, ws: WebSocket):
        """
        Menghapus koneksi WebSocket dari daftar koneksi aktif.

        Parameters:
        ws (WebSocket): Koneksi WebSocket yang akan dihapus.

        Returns:
        None
        """

        # `self.active_connections.remove(ws)` digunakan untuk menghapus koneksi yang diberikan dari daftar koneksi aktif
        self.active_connections.remove(ws)
