import io
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import requests

from config.indices import INDICES, WIKIPEDIA_HEADERS


def get_last_market_close(index_key: str) -> datetime:
    """Returns the datetime of the most recently completed market close for the given index."""
    config = INDICES[index_key]
    tz = ZoneInfo(config["market_tz"])
    now = datetime.now(tz)
    candidate = now.replace(hour=config["close_hour"], minute=config["close_minute"], second=0, microsecond=0)
    if now < candidate:
        candidate -= timedelta(days=1)
    while candidate.weekday() >= 5:  # skip Saturday (5) and Sunday (6)
        candidate -= timedelta(days=1)
    return candidate


def needs_download(index_key: str) -> bool:
    """Returns True if a new candle has closed since the last download."""
    marker = Path("datasets/daily") / index_key / ".last_download"
    if not marker.exists():
        return True
    last_download = datetime.fromisoformat(marker.read_text().strip())
    last_close = get_last_market_close(index_key)
    return last_download < last_close


def mark_downloaded(index_key: str) -> None:
    """Writes the current time as the last download timestamp."""
    tz = ZoneInfo(INDICES[index_key]["market_tz"])
    marker = Path("datasets/daily") / index_key / ".last_download"
    marker.write_text(datetime.now(tz).isoformat())


def get_index_companies(index_key: str) -> pd.DataFrame:
    config = INDICES[index_key]
    response = requests.get(config["url"], headers=WIKIPEDIA_HEADERS, timeout=10)
    response.raise_for_status()
    tables = pd.read_html(io.StringIO(response.text))

    symbol_col = config["symbol_col"]
    name_col = config["name_col"]
    table = next((t for t in tables if symbol_col in t.columns and name_col in t.columns), None)
    if table is None:
        raise ValueError(f"Could not find a table with columns '{symbol_col}' and '{name_col}' on {config['url']}")

    df = table[[symbol_col, name_col]].copy()
    df.columns = ["Symbol", "Name"]
    if config.get("dot_replace"):
        df["Symbol"] = df["Symbol"].str.replace(".", "-", regex=False)
    if config["suffix"]:
        df["Symbol"] = df["Symbol"] + config["suffix"]

    companies_dir = Path("datasets/companies")
    companies_dir.mkdir(parents=True, exist_ok=True)
    csv_path = companies_dir / f"{index_key}.csv"
    df.to_csv(csv_path, index=False)
    print(f"Saved {config['name']} stock list to '{csv_path}'")
    return df
