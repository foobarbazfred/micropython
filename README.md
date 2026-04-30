# MicroPython Repository

This repository contains MicroPython drivers, libraries, and sample programs organized by hardware component type.

## Directory Structure

### 📷 [camera](./camera)
**Arducam camera drivers and test programs**

Contains drivers and sample code for Arducam camera modules. This directory includes hardware interface implementations and demonstration programs for camera functionality on MicroPython-enabled microcontrollers.

---

### 📺 [displays](./displays)
**Display driver libraries and examples**

Houses drivers and test programs for various display modules (LCD, OLED, e-ink, etc.). Includes implementations for common display protocols and sample applications demonstrating display usage.

---

### 📡 [mqtt-security-patterns](./mqtt-security-patterns)
**MQTT protocol implementations with security considerations**

Contains MQTT client libraries and secure communication patterns for MicroPython. Includes examples of encrypted connections, authentication methods, and best practices for IoT communication.

---

### 🌡️ [sensors](./sensors)
**Multi-sensor drivers and test programs**

Comprehensive collection of sensor drivers including:
- **AT42QT1011** - Touch Sensor
- **BME280** - Environmental Sensor (Pressure, Temperature, Humidity)
- **BME680** - Environmental Sensor with Gas Sensor
- **FSR402** - Pressure Sensor
- **GP2Y0A21YK** - Infrared Distance Sensor
- **HC-SR04** - Ultrasonic Distance Sensor
- **LSM9DS1** - 9-Axis IMU Sensor
- **MAX30100** - Pulse Oximeter Sensor
- **MAX31855** - Thermocouple Amplifier
- **S13683-03DT** - Photodiode
- **VL53L1X** - ToF Distance Sensor

Each sensor subdirectory contains driver code and example applications.

---

## Quick Navigation

| Directory | Type | Purpose |
|-----------|------|---------|
| [camera](./camera) | Hardware | Camera module drivers |
| [displays](./displays) | Hardware | Display interface libraries |
| [mqtt-security-patterns](./mqtt-security-patterns) | Protocol | IoT communication patterns |
| [sensors](./sensors) | Hardware | Multi-sensor collection |

---

## Getting Started

1. Navigate to the relevant component folder based on your hardware needs
2. Review the driver documentation in each subdirectory
3. Use the sample programs and test files as reference implementations
4. Adapt the code to your specific MicroPython board and application

## License

Please refer to individual component directories for specific licensing information.
