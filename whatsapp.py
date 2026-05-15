"""
Envio de mensagens via Evolution API (https://doc.evolution-api.com).
Para usar outra API de WhatsApp, implemente a interface _send_text.
"""

import requests
import logging
import config

logger = logging.getLogger(__name__)


def _evolution_headers() -> dict:
    return {
        "apikey": config.EVOLUTION_API_KEY,
        "Content-Type": "application/json",
    }


def _send_text(group_id: str, text: str) -> bool:
    if not all([config.EVOLUTION_API_URL, config.EVOLUTION_API_KEY, config.EVOLUTION_INSTANCE]):
        logger.error(
            "Evolution API não configurada. Defina EVOLUTION_API_URL, "
            "EVOLUTION_API_KEY e EVOLUTION_INSTANCE no .env"
        )
        return False

    url = f"{config.EVOLUTION_API_URL.rstrip('/')}/message/sendText/{config.EVOLUTION_INSTANCE}"
    payload = {
        "number": group_id,
        "text": text,
        "delay": 1000,
    }

    try:
        resp = requests.post(url, json=payload, headers=_evolution_headers(), timeout=20)
        resp.raise_for_status()
        logger.info("Mensagem enviada para %s", group_id)
        return True
    except requests.HTTPError as e:
        logger.error("Erro HTTP ao enviar mensagem: %s — %s", e, resp.text)
        return False
    except requests.RequestException as e:
        logger.error("Erro de conexão ao enviar mensagem: %s", e)
        return False


def send_offer(message: str) -> bool:
    if not config.WHATSAPP_GROUP_ID:
        logger.error("WHATSAPP_GROUP_ID não configurado no .env")
        return False
    return _send_text(config.WHATSAPP_GROUP_ID, message)


def send_offers_batch(messages: list[str]) -> int:
    """Envia uma lista de mensagens e retorna quantas foram enviadas com sucesso."""
    sent = 0
    for msg in messages:
        if send_offer(msg):
            sent += 1
    return sent
