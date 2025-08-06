import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Token
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

# Dota 2 API (Steam Web API - бесплатный)
STEAM_API_KEY = os.getenv('STEAM_API_KEY', '')  # Опционально для дополнительных данных

# Настройки бота
BOT_NAME = "Dota 2 Group Bot"
BOT_DESCRIPTION = "Бот для группы игроков Dota 2" 