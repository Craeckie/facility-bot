This project consists of 3 parts:

### Sensor
Sends measured temperature values to the server. Folder contains code for an ESP8266 (but should also run on an ESP32) using PlatformIO.

### Server
Provides a simple HTTP API for adding and retrieving measured temperatures. Stores the values in a Redis DB. Written in Python using Flask.

### Bot
A Telegram bot for plotting the temperature curve. Retrieves the values from the same Redis DB. Written in Python using [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
