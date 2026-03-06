# Candlestick Screener

A Flask web application that scans stock indices for candlestick patterns using TA-Lib. Supports multiple indices, smart data download with freshness checking, and real-time download progress via Server-Sent Events.

---

## Features

- **62 TA-Lib candlestick patterns** — bullish and bearish signals detected on the most recent daily candle
- **Multiple indices** — S&P 500, NASDAQ-100, DAX, FTSE 100
- **Smart download** — skips re-downloading if data is already current (compares last download time against the most recent market close in the correct timezone)
- **Real-time progress bar** — SSE-based streaming shows per-symbol download progress without blocking the UI
- **Finviz charts** — daily candlestick chart rendered inline for every match
- **Company names** — results show the full company name alongside the ticker symbol

---

## Tech Stack

| Tool | Version |
| - | - |
| Python | 3.13.9 |
| uv | 0.9.4 |
| Flask | 3.1.3 |
| pandas | 3.0.1 |
| yfinance | 1.2.0 |
| TA-Lib | 0.6.3 |
| lxml | 6.0.2 |

---

## Project Structure

```text
src/
    app.py               # Flask routes: /, /snapshot, /snapshot/stream
    utils.py             # Download helpers: freshness check, market close, index companies
    config/
        indices.py       # INDICES dict (market timezone, close time, Wikipedia source)
        patterns.py      # 62 TA-Lib candlestick pattern names
    templates/
        index.html       # Full UI: index selector, download, pattern scan, results
datasets/
    companies/           # Cached company lists per index (CSV)
    daily/
        sp500/           # Daily OHLCV CSVs + .last_download marker
        nasdaq100/
        dax/
        ftse100/
pyproject.toml
uv.lock
```

---

## Getting Started

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- TA-Lib shared library (platform-specific install required before `uv sync`)

### Install dependencies

```bash
uv sync
```

### Run the app

```bash
uv run flask --app src/app run --debug
```

Then open [http://localhost:5000](http://localhost:5000).

---

## Usage

1. **Select an index** from the dropdown (S&P 500, NASDAQ-100, DAX, FTSE 100).
2. **Download Data** — fetches 1 month of daily OHLCV data for all index constituents from Yahoo Finance. A progress bar shows live per-symbol status. Already-current data is skipped automatically.
3. **Scan for Pattern** — select a candlestick pattern and click Scan. Matches are shown in a table with bullish (green) / bearish (red) highlighting and an inline Finviz chart for each result.

To force a re-download even when data is current, append `?force=true` to the download URL or use the browser console to call `/snapshot/stream?index=sp500&force=true`.

---

## Supported Indices

| Key | Name | Exchange timezone | Market close |
| --- | ---- | ----------------- | ------------ |
| `sp500` | S&P 500 | America/New_York | 16:00 |
| `nasdaq100` | NASDAQ-100 | America/New_York | 16:00 |
| `dax` | DAX | Europe/Berlin | 17:30 |
| `ftse100` | FTSE 100 | Europe/London | 16:30 |

Company lists are sourced from Wikipedia on first download and cached locally.

---

## How Freshness Checking Works

Before downloading, the app computes the **last expected market close** for the selected index (most recent weekday at the configured close time in the market's timezone). If the `.last_download` marker file in `datasets/daily/{index}/` is newer than that close time, the download is skipped.
