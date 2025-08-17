# MQTT Publish Security Patterns (MicroPython)

This directory contains a collection of **MQTT Publish** examples using MicroPython, organized by security level and certificate format.  
Designed for boards like the ESP32-S3, the samples cover scenarios from plain MQTT to TLS with client certificate authentication.

---

## 📂 File Structure

| Filename           | Description |
|--------------------|-------------|
| `boot.py`          | Initializes Wi‑Fi connection and common settings |
| `receive.py`       | Example for MQTT subscribe (receive) side |
| `sample01.py`      | Minimal plain MQTT publish example |
| `sample02.py`      | Publish with TLS (*1) |
| `sample03.py`      | Publish with TLS and username/password authentication (*1) |
| `sample04.py`      | Publish with TLS and client certificate authentication (mutual TLS)|
| `sample05.py`      | Publish with TLS and username/password authentication|

*1;  The server's certificate is not being validated.

---

## 🚀 Environment

- MicroPython v1.25.0 or later (tested on Raspberry Pi Pico 2 W)
- `umqtt.simple` v1.6.0 
- Wi‑Fi network
- CA certificate, client certificate, and private key files if required

---


## 🛠 How to Run

1. Set your Wi‑Fi SSID and password in `boot.py`
2. Place required certificate files in  `/`
3. Run from REPL or `main.py`:
```python
import sample02  # Example: Publish with TLS (PEM)
