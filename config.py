import os
from dotenv import load_dotenv

load_dotenv()

# Mercado Livre
ML_SITE_ID = os.getenv("ML_SITE_ID", "MLB")  # MLB = Brasil
ML_API_BASE = "https://api.mercadolibre.com"
ML_APP_ID = os.getenv("ML_APP_ID", "")        # opcional, aumenta rate limit
ML_SECRET_KEY = os.getenv("ML_SECRET_KEY", "")

# Filtros de oferta
MIN_DISCOUNT_PERCENT = int(os.getenv("MIN_DISCOUNT_PERCENT", "15"))
MAX_PRICE = float(os.getenv("MAX_PRICE", "0")) or None  # 0 = sem limite
KEYWORDS = [k.strip() for k in os.getenv("KEYWORDS", "").split(",") if k.strip()]
CATEGORIES = [c.strip() for c in os.getenv("CATEGORIES", "").split(",") if c.strip()]
MAX_OFFERS_PER_RUN = int(os.getenv("MAX_OFFERS_PER_RUN", "5"))

# Agendamento (em minutos)
SCHEDULE_INTERVAL_MINUTES = int(os.getenv("SCHEDULE_INTERVAL_MINUTES", "30"))

# WhatsApp — Green API
GREEN_API_ID_INSTANCE = os.getenv("GREEN_API_ID_INSTANCE", "")       # ex: 1101xxxxxxx
GREEN_API_TOKEN = os.getenv("GREEN_API_TOKEN", "")                    # token da instância
WHATSAPP_GROUP_ID = os.getenv("WHATSAPP_GROUP_ID", "")                # ex: 120363xxxxxxx@g.us

# Arquivo de controle de duplicatas
SENT_OFFERS_FILE = os.getenv("SENT_OFFERS_FILE", "sent_offers.json")
