"""Controle de ofertas já enviadas para evitar duplicatas."""

import json
import time
import logging
from pathlib import Path
import config

logger = logging.getLogger(__name__)

# Mantém IDs por até 7 dias (em segundos)
TTL_SECONDS = 7 * 24 * 60 * 60


def _load() -> dict:
    path = Path(config.SENT_OFFERS_FILE)
    if not path.exists():
        return {}
    try:
        with path.open() as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save(data: dict) -> None:
    path = Path(config.SENT_OFFERS_FILE)
    try:
        with path.open("w") as f:
            json.dump(data, f, indent=2)
    except OSError as e:
        logger.error("Não foi possível salvar sent_offers: %s", e)


def is_new(offer_id: str) -> bool:
    data = _load()
    return offer_id not in data


def mark_sent(offer_id: str) -> None:
    data = _load()
    data[offer_id] = int(time.time())
    _purge_old(data)
    _save(data)


def _purge_old(data: dict) -> None:
    cutoff = int(time.time()) - TTL_SECONDS
    expired = [k for k, v in data.items() if v < cutoff]
    for k in expired:
        del data[k]
