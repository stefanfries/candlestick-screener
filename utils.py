import pandas as pd


def get_sp500_symbols() -> pd.DataFrame:
    # Get S&P 500 table from Wikipedia
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    tables = pd.read_html(url)

    # The first table usually contains the data we want
    sp500_table = tables[0]

    # Extract symbol and name columns
    sp500_df = sp500_table[["Symbol", "Security"]]
    sp500_df.columns = ["Symbol", "Name"]

    # Optional: clean symbols for yfinance (some symbols like BRK.B need special handling)
    sp500_df.loc[:, "Symbol"] = sp500_df["Symbol"].str.replace(".", "-", regex=False)

    # Save to CSV
    sp500_df.to_csv("datasets/sp500_companies.csv", index=False)

    print("Saved S&P 500 stock list to 'sp500_symbols.csv'")
    return sp500_df
