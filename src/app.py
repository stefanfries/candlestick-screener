import json
from pathlib import Path

import pandas as pd
import talib
import yfinance as yf
from flask import Flask, Response, render_template, request, stream_with_context

from config.indices import INDICES
from config.patterns import patterns
from utils import (
    get_index_companies,
    get_last_market_close,
    mark_downloaded,
    needs_download,
)

app = Flask(__name__)


@app.route("/")
def index() -> str:
    """Render the index.html template"""

    pattern = request.args.get("pattern", None)
    index_key = request.args.get("index", "sp500")
    matches = []
    if pattern and pattern in patterns:
        talib_func = getattr(talib, pattern)
        companies_path = Path("datasets/companies") / f"{index_key}.csv"
        if companies_path.exists():
            companies = pd.read_csv(companies_path, index_col="Symbol")["Name"].to_dict()
            for symbol, name in companies.items():
                filepath = Path("datasets/daily") / index_key / f"{symbol}.csv"
                if not filepath.exists():
                    continue
                df = pd.read_csv(filepath, header=0, skiprows=[1, 2])
                try:
                    result = talib_func(
                        df["Open"], df["High"], df["Low"], df["Close"]
                    )
                    last_value = result.iloc[-1]
                    if last_value != 0:
                        matches.append({"symbol": symbol, "name": name, "signal": last_value})
                except Exception as e:
                    print(f"Error processing {symbol}: {e}")
    available_indices = {k: v["name"] for k, v in INDICES.items()}
    return render_template("index.html", patterns=patterns, pattern=pattern, matches=matches, indices=available_indices, index_key=index_key)


@app.route("/snapshot")
def snapshot() -> dict:
    index_key = request.args.get("index", "sp500")
    force = request.args.get("force", "false").lower() == "true"
    if index_key not in INDICES:
        return {"code": "error", "message": f"Unknown index '{index_key}'"}, 400
    if not force and not needs_download(index_key):
        last_close = get_last_market_close(index_key)
        return {"code": "skipped", "reason": f"Data already up to date. Last close: {last_close.strftime('%Y-%m-%d %H:%M %Z')}"}
    df = get_index_companies(index_key)
    symbols = df["Symbol"].tolist()
    daily_dir = Path("datasets/daily") / index_key
    daily_dir.mkdir(parents=True, exist_ok=True)
    for f in daily_dir.glob("*.csv"):
        f.unlink()
    failed = []
    for symbol in symbols:
        data = yf.download(symbol, period="1mo", interval="1d", auto_adjust=True)
        if data.empty:
            failed.append(symbol)
        else:
            data.to_csv(daily_dir / f"{symbol}.csv")
    mark_downloaded(index_key)
    return {"code": "success", "index": index_key, "failed": failed}


@app.route("/snapshot/stream")
def snapshot_stream() -> Response:
    index_key = request.args.get("index", "sp500")
    force = request.args.get("force", "false").lower() == "true"

    def _sse(payload: dict) -> str:
        return f"data: {json.dumps(payload)}\n\n"

    def generate():
        if index_key not in INDICES:
            yield _sse({"type": "error", "message": f"Unknown index '{index_key}'"})
            return
        if not force and not needs_download(index_key):
            last_close = get_last_market_close(index_key)
            yield _sse({"type": "skipped", "reason": f"Data already up to date. Last close: {last_close.strftime('%Y-%m-%d %H:%M %Z')}"})
            return
        df = get_index_companies(index_key)
        symbols = df["Symbol"].tolist()
        total = len(symbols)
        daily_dir = Path("datasets/daily") / index_key
        daily_dir.mkdir(parents=True, exist_ok=True)
        for f in daily_dir.glob("*.csv"):
            f.unlink()
        failed = []
        for i, symbol in enumerate(symbols, 1):
            yield _sse({"type": "progress", "current": i, "total": total, "symbol": symbol})
            data = yf.download(symbol, period="1mo", interval="1d", auto_adjust=True, progress=False)
            if data.empty:
                failed.append(symbol)
            else:
                data.to_csv(daily_dir / f"{symbol}.csv")
        mark_downloaded(index_key)
        yield _sse({"type": "done", "failed": failed})

    return Response(stream_with_context(generate()), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
