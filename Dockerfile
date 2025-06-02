FROM node:18-bullseye

# Install Python & pip
RUN apt update && \
    apt install -y python3 python3-pip

# Set work directory
WORKDIR /app

# Copy all project files
COPY . .

# Install Node.js dependencies
WORKDIR /app/session-boss-main
RUN npm install

# Install Python dependencies
WORKDIR /app
RUN pip3 install --no-cache-dir -r requirements.txt

# Expose Node server port
EXPOSE 7860

# Run both services
CMD ["bash", "-c", "node session-boss-main/index.js & python3 telegram_bot.py"]
