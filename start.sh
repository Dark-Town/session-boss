#!/bin/bash

# Start Node.js server
cd session-boss-main
nohup node index.js > ../node.log 2>&1 &

# Go back and start Telegram bot
cd ..
python3 telegram_bot.py
