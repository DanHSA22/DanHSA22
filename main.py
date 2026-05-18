#!/usr/bin/env python3
"""
Bot de Ofertas — Mercado Livre → WhatsApp
Busca ofertas com desconto e posta automaticamente em um grupo do WhatsApp.
"""

import logging
import time
import signal
import sys

import config
import mercadolivre
import whatsapp
import storage

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("bot.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)

_running = True


def _handle_signal(sig, frame):
    global _running
    logger.info("Encerrando bot (sinal %s)…", sig)
    _running = False


def run_once() -> None:
    logger.info("Iniciando busca de ofertas…")
    all_offers = mercadolivre.fetch_all_offers()

    new_offers = [o for o in all_offers if storage.is_new(o.id)]
    logger.info("%d ofertas novas de %d encontradas", len(new_offers), len(all_offers))

    to_send = new_offers[: config.MAX_OFFERS_PER_RUN]
    if not to_send:
        logger.info("Nenhuma oferta nova para enviar.")
        return

    messages = [offer.format_message() for offer in to_send]
    sent = whatsapp.send_offers_batch(messages)
    logger.info("%d/%d mensagens enviadas com sucesso", sent, len(to_send))

    for offer, msg_sent in zip(to_send, [True] * sent + [False] * (len(to_send) - sent)):
        if msg_sent:
            storage.mark_sent(offer.id)


def run_loop() -> None:
    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    interval = config.SCHEDULE_INTERVAL_MINUTES * 60
    logger.info(
        "Bot iniciado — intervalo: %d minutos | desconto mínimo: %d%%",
        config.SCHEDULE_INTERVAL_MINUTES,
        config.MIN_DISCOUNT_PERCENT,
    )

    while _running:
        try:
            run_once()
        except Exception:
            logger.exception("Erro inesperado durante execução — tentando novamente no próximo ciclo")

        if not _running:
            break

        logger.info("Próxima busca em %d minutos…", config.SCHEDULE_INTERVAL_MINUTES)
        elapsed = 0
        while elapsed < interval and _running:
            time.sleep(5)
            elapsed += 5

    logger.info("Bot encerrado.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        run_once()
    else:
        run_loop()
