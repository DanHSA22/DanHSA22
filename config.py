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

# WhatsApp — Evolution API
EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL", "")     # ex: http://localhost:8080
EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY", "")
EVOLUTION_INSTANCE = os.getenv("EVOLUTION_INSTANCE", "")    # nome da instância
WHATSAPP_GROUP_ID = os.getenv("WHATSAPP_GROUP_ID", "")      # ex: 120363xxxxxxx@g.us

# Arquivo de controle de duplicatas
SENT_OFFERS_FILE = os.getenv("SENT_OFFERS_FILE", "sent_offers.json")
