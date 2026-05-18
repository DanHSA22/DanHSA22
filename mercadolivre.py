import requests
import logging
from dataclasses import dataclass, field
from typing import Optional
import config

logger = logging.getLogger(__name__)

SEARCH_URL = f"{config.ML_API_BASE}/sites/{config.ML_SITE_ID}/search"
TOKEN_URL = f"{config.ML_API_BASE}/oauth/token"

_access_token: Optional[str] = None


def _get_access_token() -> Optional[str]:
    global _access_token
    if _access_token:
        return _access_token
    if not config.ML_APP_ID or not config.ML_SECRET_KEY:
        return None
    try:
        resp = requests.post(TOKEN_URL, data={
            "grant_type": "client_credentials",
            "client_id": config.ML_APP_ID,
            "client_secret": config.ML_SECRET_KEY,
        }, timeout=15)
        resp.raise_for_status()
        _access_token = resp.json().get("access_token")
        logger.info("Token Mercado Livre obtido com sucesso")
        return _access_token
    except requests.RequestException as e:
        logger.error("Erro ao obter token ML: %s", e)
        return None


@dataclass
class Offer:
    id: str
    title: str
    price: float
    original_price: Optional[float]
    discount_percent: float
    url: str
    thumbnail: str
    category_id: str
    seller: str
    available_quantity: int
    tags: list = field(default_factory=list)

    def format_message(self) -> str:
        discount_line = ""
        if self.original_price and self.discount_percent > 0:
            discount_line = (
                f"~~R$ {self.original_price:,.2f}~~  ➡️  *R$ {self.price:,.2f}*\n"
                f"📉 *{self.discount_percent:.0f}% de desconto!*\n"
            )
        else:
            discount_line = f"💰 *R$ {self.price:,.2f}*\n"

        return (
            f"🔥 *OFERTA ENCONTRADA!*\n\n"
            f"📦 {self.title}\n\n"
            f"{discount_line}\n"
            f"🏪 Vendedor: {self.seller}\n"
            f"📦 Estoque: {self.available_quantity} unidades\n\n"
            f"🔗 {self.url}"
        )


def _build_params(keyword: str = "", category: str = "") -> dict:
    params: dict = {
        "limit": 50,
        "sort": "best_match",
    }
    if keyword:
        params["q"] = keyword
    if category:
        params["category"] = category
    if config.ML_APP_ID:
        params["app_id"] = config.ML_APP_ID
    return params


def _parse_item(item: dict) -> Optional[Offer]:
    try:
        price = float(item["price"])
        original_price = item.get("original_price")
        if original_price:
            original_price = float(original_price)
            discount = round((1 - price / original_price) * 100, 1)
        else:
            discount = 0.0

        seller_info = item.get("seller", {})
        seller_name = seller_info.get("nickname", "Desconhecido")

        permalink = item.get("permalink", "")
        # garante link sem tracker desnecessário
        if not permalink:
            permalink = f"https://www.mercadolivre.com.br/p/{item['id']}"

        return Offer(
            id=item["id"],
            title=item["title"],
            price=price,
            original_price=original_price,
            discount_percent=discount,
            url=permalink,
            thumbnail=item.get("thumbnail", ""),
            category_id=item.get("category_id", ""),
            seller=seller_name,
            available_quantity=item.get("available_quantity", 0),
            tags=item.get("tags", []),
        )
    except (KeyError, ValueError, TypeError) as e:
        logger.debug("Erro ao parsear item %s: %s", item.get("id"), e)
        return None


def _fetch_page(params: dict) -> list[dict]:
    headers = {"Accept": "application/json"}
    token = _get_access_token()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        resp = requests.get(SEARCH_URL, params=params, headers=headers, timeout=15)
        resp.raise_for_status()
        return resp.json().get("results", [])
    except requests.RequestException as e:
        logger.error("Erro ao buscar ofertas no Mercado Livre: %s", e)
        return []


def fetch_offers(keyword: str = "", category: str = "") -> list[Offer]:
    params = _build_params(keyword, category)
    raw_items = _fetch_page(params)

    offers = []
    for item in raw_items:
        offer = _parse_item(item)
        if offer is None:
            continue

        if config.MIN_DISCOUNT_PERCENT > 0 and offer.discount_percent < config.MIN_DISCOUNT_PERCENT:
            continue

        if config.MAX_PRICE and offer.price > config.MAX_PRICE:
            continue

        offers.append(offer)

    logger.info(
        "Busca '%s' categoria '%s': %d resultados, %d aprovados",
        keyword, category, len(raw_items), len(offers),
    )
    return offers


def fetch_all_offers() -> list[Offer]:
    """Agrega ofertas de todas as combinações de keywords e categorias configuradas."""
    seen_ids: set[str] = set()
    all_offers: list[Offer] = []

    combos = []
    if config.KEYWORDS and config.CATEGORIES:
        combos = [(kw, cat) for kw in config.KEYWORDS for cat in config.CATEGORIES]
    elif config.KEYWORDS:
        combos = [(kw, "") for kw in config.KEYWORDS]
    elif config.CATEGORIES:
        combos = [("", cat) for cat in config.CATEGORIES]
    else:
        combos = [("", "")]

    for keyword, category in combos:
        for offer in fetch_offers(keyword, category):
            if offer.id not in seen_ids:
                seen_ids.add(offer.id)
                all_offers.append(offer)

    all_offers.sort(key=lambda o: o.discount_percent, reverse=True)
    return all_offers
