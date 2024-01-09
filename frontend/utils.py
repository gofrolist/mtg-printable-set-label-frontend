import datetime
import logging

import requests
from django.core.cache import cache
from django.utils import timezone
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Retry Strategy for requests
retry_strategy = Retry(
    total=3,  # Total number of retries to allow
    status_forcelist=[
        429,
        500,
        502,
        503,
        504,
    ],  # Status codes to retry    allowed_methods=
    allowed_methods=["HEAD", "GET", "OPTIONS"],  # HTTP methods to retry
    backoff_factor=1,  # Backoff factor for retries
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session = requests.Session()
session.mount("https://", adapter)  # Mount the retry strategy

# Constants
SCRYFALL_SETS_API_URL = "https://api.scryfall.com/sets"
SCRYFALL_SETS_CACHE_KEY = "scryfall-sets"
SCRYFALL_SETS_CACHE_DURATION_HOURS = 8

EXCLUDED_SETS = (
    "cmb1",  # Mystery Booster Playtest Cards
    "amh1",  # Modern Horizon Art Series
    "cmb2",  # Mystery Booster Playtest Cards Part Deux
    "fbb",  # Foreign Black Border
    "sum",  # Summer Magic / Edgar
    "4bb",  # Fourth Edition Foreign Black Border
    "bchr",  # Chronicles Foreign Black Border
    "rin",  # Rinascimento
    "ren",  # Renaissance
    "rqs",  # Rivals Quick Start Set
    "itp",  # Introductory Two-Player Set
    "sir",  # Shadows over Innistrad Remastered
    "sis",  # Shadows of the Past
    "cst",  # Coldsnap Theme Decks
    "scd",  # Starter Commander Decks - set has an icon issue
)

log = logging.getLogger(__name__)  # noqa


def get_scryfall_set_data():
    cached_result = cache.get(SCRYFALL_SETS_CACHE_KEY)
    if cached_result:
        log.debug("Using cached sets data.")
        return cached_result

    log.debug("Fetching sets from Scryfall API...")

    def fetch_sets():
        try:
            resp = session.get(SCRYFALL_SETS_API_URL)
            resp.raise_for_status()
            sets = resp.json().get("data", [])
            # Save the sets back to the cache
            cache.set(
                SCRYFALL_SETS_CACHE_KEY, sets, SCRYFALL_SETS_CACHE_DURATION_HOURS * 3600
            )
            return sets
        except requests.exceptions.RequestException as e:
            log.error("Failed to fetch sets data from Scryfall API: %s", str(e))
            return []

    return fetch_sets()


def get_grouped_sets():
    current_date = timezone.now().date()

    def is_expansion_valid(expansion):
        if (
            expansion["digital"]
            or expansion["set_type"] in ("memorabilia", "token", "vanguard", "promo")
            or expansion["code"] in EXCLUDED_SETS
        ):
            return False

        release_date = datetime.datetime.strptime(
            expansion["released_at"], "%Y-%m-%d"
        ).date()
        return release_date <= current_date

    sets = get_scryfall_set_data()
    grouped_sets = {}

    for exp in (expansion for expansion in sets if is_expansion_valid(expansion)):
        set_type = exp["set_type"].replace("_", " ")
        grouped_sets.setdefault(set_type, []).append((exp["code"], exp))

    return sorted(grouped_sets.items())
