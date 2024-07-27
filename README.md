# ZWSP Steganography implementation in Python

## Persiapan environment

### `.env` file

1. Buat file `.env` kosong di root directory (contoh isi file `.env` terdapat di `.env.example`)
2. Isi file `.env` dengan variable-variable yang dibutuhkan, defaultnya seperti ini:
   ```
   MQTT_HOST=0.0.0.0
   MQTT_PORT=1883
   MQTT_USERNAME=admin
   MQTT_PASSWORD=hivemq
   ```

### Install Docker

1. Install docker pada link [ini](https://www.docker.com/products/docker-desktop/)
2. Ikuti instruksi penginstalannya

### Install HiveMQ MQTT Edge menggunakan docker

1. Ketikan Perintah berikut pada command line:
   ```
   docker run --name hivemq-edge -d -p 0.0.0.0:1883:1883 -p 8081:8080 hivemq/hivemq-edge
   ```
2. MQTT server akan berjalan di port `1883` dan MQTT Server Web UI akan berjalan di port `8081`
3. MQTT web UI bisa diakses pada [http://localhost:8081/app/](http://localhost:8081/app/)
4. Default username dan password MQTT Server Web UI adalah sebagai berikut:
   - username: admin
   - password: hivemq

### Python Dependency

1. Install library-library yang dibutuhkan untuk menjalakan sender/receiver API server dengan command berikut:

   ```
   pip install -r requirements.txt
   ```

   atau

   ```
   pip3 install -r requirements.txt
   ```

2. Jika perintah diatas terdapat error, anda dapat menginstall packagenya satu persatu, dengan perintah berikut:
   ```
   pip install fastapi uvicorn fastapi-mqtt python-dotenv
   ```
   atau
   ```
   pip3 install fastapi uvicorn fastapi-mqtt python-dotenv
   ```

## Menjalankan API server untuk Sender dan Receiver

### Sender API Server

1. Buka terminal baru (misal di integrated terminal VSCode)
2. Eksekusi perintah berikut:
   ```
   uvicorn app.sender.main:app --host 0.0.0.0 --port 8080
   ```
   atau
   ```
   python -m uvicorn app.sender.main:app --host 0.0.0.0 --port 8080
   ```
   jika terdapat error, coba dengan mengganti hostnya ke `localhost`, sehingga commandnya menjadi:
   ```
   python -m uvicorn app.sender.main:app --host localhost --port 8080
   ```
3. Server akan berjalan di port `8080`
4. server bisa diakses di [`http://0.0.0.0:8080`](http://0.0.0.0:8080) atau [`http://localhost:8080`](http://localhost:8080)
5. Penjalanan sender API diindikasikan oleh `app.sender.main:app`, yang menyatakan untuk menjalan aplikasi bernama `sender.main` dan akan mengekesekusi file `main.py` di folder `sender` pada package (folder) `app`. Full path dimana program yang akan di eksekusi adalah (`app/sender/main.py`)

### Receiver API Server

untuk menjalankan Recevier API server kurang lebih sama, ada beberapa perbedaan pada port dan module program yang dijalakan

1. Buka terminal baru (misal di integrated terminal VSCode)
2. Eksekusi perintah berikut:
   ```
   uvicorn app.receiver.main:app --host 0.0.0.0 --port 8000
   ```
   atau
   ```
   python -m uvicorn app.receiver.main:app --host 0.0.0.0 --port 8000
   ```
   jika terdapat error, coba dengan mengganti hostnya ke `localhost`, sehingga commandnya menjadi:
   ```
   python -m uvicorn app.receiver.main:app --host localhost --port 8000
   ```
3. Server akan berjalan di port `8000`
4. server bisa diakses di [`http://0.0.0.0:8000`](http://0.0.0.0:8000) atau [`http://localhost:8000`](http://localhost:8000)
5. Penjalanan receiver API diindikasikan oleh `app.receiver.main:app`, yang menyatakan untuk menjalan aplikasi bernama `receiver.main` dan akan mengekesekusi file `main.py` di folder `receiver` pada package (folder) `app`. Full path dimana program yang akan di eksekusi adalah (`app/receiver/main.py`)

## Module ZWSP

Module inti dari program ini berada di package `zwsp` yang berlokasi di `zwsp/zwsp.py` yang berisikan logika untuk encode dan decode pesan

## Menjalankan Web UI Sender/Receiver ZWSP

1. Buka folder project zwsp_code_ui yang berisikan file html, css, dan javascript menggunakan VSCode.
2. Pada pojok kanan bawah terdapat tombol `Go Live`, klik tombol tersebut untuk menjalankan live server.
3. Live server akan berjalan di port 5500
4. Kunjungi [http://127.0.0.1:5500](http://127.0.0.1:5500/) atau [http://localhost:5500/](http://localhost:5500/).
5. Sebagai informasi tambahan, sejatinya `127.0.0.1` sama dengan `localhost`, dengan kata lain `localhost` = `127.0.0.1`.

## Wireshark untuk capturing komunikasi MQTT

1. Jalankan aplikasi Wireshark
2. Capture interface `Loopback` (e.g `Loopback: Io0`)
3. Pada kolom filter, ketikan `mqtt` untuk memfilter komunikasi mqtt saja yang dicapture
4. Atau untuk lebih spesifik, bisa menyertakan portnya juga, dengan mengetikan `tcp.port == 1883 && mqtt`, filter tersebut akan mencapture komunikasi mqtt yang berjalan pada port 1883
