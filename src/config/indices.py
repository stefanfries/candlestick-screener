INDICES = {
    "sp500": {
        "name": "S&P 500",
        "url": "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies",
        "symbol_col": "Symbol",
        "name_col": "Security",
        "suffix": "",
        "dot_replace": True,
        "market_tz": "America/New_York",
        "close_hour": 16,
        "close_minute": 0,
    },
    "nasdaq100": {
        "name": "NASDAQ-100",
        "url": "https://en.wikipedia.org/wiki/Nasdaq-100",
        "symbol_col": "Ticker",
        "name_col": "Company",
        "suffix": "",
        "dot_replace": False,
        "market_tz": "America/New_York",
        "close_hour": 16,
        "close_minute": 0,
    },
    "dax": {
        "name": "DAX",
        "url": "https://en.wikipedia.org/wiki/DAX",
        "symbol_col": "Ticker",
        "name_col": "Company",
        "suffix": "",
        "dot_replace": False,
        "market_tz": "Europe/Berlin",
        "close_hour": 17,
        "close_minute": 30,
    },
    "ftse100": {
        "name": "FTSE 100",
        "url": "https://en.wikipedia.org/wiki/FTSE_100_Index",
        "symbol_col": "Ticker",
        "name_col": "Company",
        "suffix": ".L",
        "dot_replace": False,
        "market_tz": "Europe/London",
        "close_hour": 16,
        "close_minute": 30,
    },
}

WIKIPEDIA_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}
