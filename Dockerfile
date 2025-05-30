FROM node:lts-buster

# Install dependencies (ffmpeg, imagemagick, webp)
RUN apt-get update && apt-get install -y \
  ffmpeg \
  imagemagick \
  webp \
  && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /usr/src/app

# Copy and install dependencies
COPY package*.json ./
RUN npm install && npm install -g qrcode-terminal pm2

# Copy the rest of your application code
COPY . .

# Expose the desired port
EXPOSE 5000

# Start the app using PM2 for process management
CMD ["pm2-runtime", "index.js"]
