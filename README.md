# project
Kill me quick

# Telegram OTP Caller Bot

This repo contains a Telegram bot and backend that can automate customer calls, collect DTMF/OTP input, and record interactions.

## Features

- `/start` & `/cancel` session management
- Call customer from company number, indicate all call states
- Display customer keypresses and OTPs instantly in Telegram
- Call recording links sent when processing is complete

## Setup

- Fill out `.env` with your credentials (copy from `.env.example`)
- Install dependencies:
    ```sh
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
- Deploy Flask backend somewhere public (Render, Railway, Heroku, DigitalOcean, etc.)
- Update both bot and backend `.env` files with your settings
- Run the backend:
    ```sh
    cd backend; python app.py
    ```
- Run the bot:
    ```sh
    cd bot; python telegram_bot.py
    ```
- DM your bot on Telegram, use `/start` to begin

## Legal

- Always inform users of call recording
- Secure all private information in `.env`
