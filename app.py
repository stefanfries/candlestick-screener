import yfinance as yf
from flask import Flask, render_template

from patterns import patterns
from utils import get_sp500_symbols

app = Flask(__name__)


@app.route("/")
def hello_world() -> str:
    """Render the index.html template"""

    return render_template("index.html", patterns=patterns)


@app.route("/snapshot")
def snapshot() -> dict:
    df = get_sp500_symbols()
    print(df)
    """Simulate a snapshot operation"""
    # with open("datasets/companies.csv") as f:
    # companies = f.read().splitlines()
    # for company in companies:
    #     symbol = company.split(",")[0]
    #     df = yf.download(symbol, period="1mo", interval="1d")
    #     df.to_csv(f"datasets/daily/{symbol}.csv")
    return {"code": "success"}
