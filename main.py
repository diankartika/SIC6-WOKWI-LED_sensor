import network
import random
import json
from machine import Pin
from umqtt.simple import MQTTClient
from utime import sleep, localtime

# Konfigurasi WiFi
WIFI_SSID = "Wokwi-GUEST"
WIFI_PASSWORD = ""

# Konfigurasi MQTT
MQTT_CLIENT_ID = "mqttx_e6decbc0"
MQTT_BROKER = "test.mosquitto.org"
TOPIC_SENSOR = "/UNI193/MutiaraSetyaRini/aktuasi_led"

# Inisialisasi LED
led = Pin(15, Pin.OUT)

# Fungsi untuk menghubungkan ke WiFi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)

    print("Menghubungkan ke WiFi...", end="")
    while not wlan.isconnected():
        sleep(1)
        print(".", end="")
    print("\nTerhubung ke WiFi")
    print("IP Address:", wlan.ifconfig()[0])

# Fungsi untuk memvalidasi koneksi MQTT
def reconnect_mqtt(client):
    try:
        client.connect()
        print("Berhasil menyambung ulang ke broker MQTT")
    except Exception as e:
        print(f"Gagal menyambung ulang ke broker MQTT: {e}")

# Fungsi callback untuk pesan MQTT
def mqtt_callback(topic, msg):
    print(f"DEBUG: Pesan diterima - Topic: {topic.decode()}, Message: {msg.decode()}")
    if msg.decode().strip() == "ON":
        led.on()
        print("LED menyala")
    elif msg.decode().strip() == "OFF":
        led.off()
        print("LED mati")
    else:
        print(f"Pesan tidak dikenali: {msg.decode()}")

# Fungsi utama
def main():
    connect_wifi()

    # Inisialisasi MQTT Client
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER)
    client.set_callback(mqtt_callback)

    try:
        client.connect()
        print("Terhubung ke broker MQTT")
    except Exception as e:
        print(f"Gagal terhubung ke broker MQTT: {e}")
        return

    # Subscribe ke topic untuk kontrol LED
    try:
        client.subscribe(TOPIC_SENSOR)
        print(f"Berlangganan ke topic: {TOPIC_SENSOR}")
    except Exception as e:
        print(f"Gagal subscribe ke topic: {e}")
        return

    try:
        while True:
            # Simulasi data sensor
            temperature = random.uniform(20.0, 30.0)
            humidity = random.uniform(30, 60)
            light = random.randint(0, 1023)
            timestamp = localtime()

            # Buat data JSON
            sensor_data = {
                "temperature": round(temperature, 2),
                "humidity": round(humidity, 2),
                "light": light,
                "time": f"{timestamp[3]:02}:{timestamp[4]:02}:{timestamp[5]:02}"
            }

            # Publish data sensor
            try:
                client.publish(TOPIC_SENSOR, json.dumps(sensor_data))
                print(f"Data dipublish: {sensor_data}")
            except Exception as e:
                print(f"Gagal mempublish data: {e}")
                reconnect_mqtt(client)

            # Periksa pesan untuk kontrol LED
            try:
                client.check_msg()
            except Exception as e:
                print(f"Kesalahan saat memeriksa pesan: {e}")

            sleep(5)  # Delay 5 detik sebelum loop berikutnya

    except KeyboardInterrupt:
        print("Program dihentikan")
    finally:
        try:
            client.disconnect()
            print("Terputus dari broker MQTT")
        except Exception as e:
            print(f"Gagal memutuskan koneksi dari broker MQTT: {e}")

# Jalankan program
if __name__ == "__main__":
    main()
