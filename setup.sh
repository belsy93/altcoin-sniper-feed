
#!/bin/bash

# Update packages and install dependencies
echo "🔧 Updating system and installing dependencies..."
sudo apt update && sudo apt install -y python3-pip python3-venv git

# Clone or confirm repo exists
if [ ! -d "/home/pi/sniper-bot" ]; then
  git clone https://github.com/belsy93/altcoin-sniper-feed.git /home/pi/sniper-bot
fi

cd /home/pi/sniper-bot

# Set up Python virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv sniper-env
source sniper-env/bin/activate

# Install Python packages
echo "📦 Installing Python requirements..."
pip install python-binance python-dotenv requests

# Create crontab entry to run the bot at boot
echo "🕓 Setting up auto-start with crontab..."
(crontab -l 2>/dev/null; echo "@reboot /home/pi/sniper-bot/sniper-env/bin/python /home/pi/sniper-bot/altcoin_sniper_final.py") | crontab -

echo "✅ Setup complete. The bot will auto-start on boot."
