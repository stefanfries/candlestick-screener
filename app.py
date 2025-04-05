import os

import pandas as pd
import talib
import yfinance as yf
from flask import Flask, render_template, request

from patterns import patterns
from utils import get_sp500_symbols

app = Flask(__name__)


@app.route("/")
def index() -> str:
    """Render the index.html template"""

    pattern = request.args.get("pattern", None)
    if pattern:
        datafiles = os.listdir("datasets/daily")
        for filename in datafiles:
            df = pd.read_csv(f"datasets/daily/{filename}")
            try:
                result = talib.CDLENGULFING(
                    df["Open"], df["High"], df["Low"], df["Close"]
                )
                print(f"result: {result}")
            except:
                pass
    return render_template("index.html", patterns=patterns)


@app.route("/snapshot")
def snapshot() -> dict:
    df = get_sp500_symbols()
    symbols = df["Symbol"].tolist()
    for symbol in symbols:
        data = yf.download(symbol, period="1mo", interval="1d", auto_adjust=True)
        data.to_csv(f"datasets/daily/{symbol}.csv")
    return {"code": "success"}
