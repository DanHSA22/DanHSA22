"""
Envio de mensagens via Green API (https://green-api.com).
Plano gratuito: 500 mensagens/mês — sem precisar instalar nada.
"""

import requests
import logging
import config

logger = logging.getLogger(__name__)


def _send_text(chat_id: str, text: str) -> bool:
    if not all([config.GREEN_API_ID_INSTANCE, config.GREEN_API_TOKEN]):
        logger.error(
            "Green API não configurada. Defina GREEN_API_ID_INSTANCE e "
            "GREEN_API_TOKEN no .env"
        )
        return False

    url = (
        f"https://api.green-api.com/waInstance{config.GREEN_API_ID_INSTANCE}"
        f"/sendMessage/{config.GREEN_API_TOKEN}"
    )
    payload = {
        "chatId": chat_id,
        "message": text,
    }

    try:
        resp = requests.post(url, json=payload, timeout=20)
        resp.raise_for_status()
        logger.info("Mensagem enviada para %s", chat_id)
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
