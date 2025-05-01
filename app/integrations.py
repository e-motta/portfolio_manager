import yfinance as yf


def get_tickers_data(symbols: list[str] | str) -> dict:
    if isinstance(symbols, str):
        return {symbols: yf.Ticker(symbols).info}

    tickers_data = yf.Tickers(" ".join(symbols))
    tickers_info = {}
    for s in symbols:
        s_data = tickers_data.tickers.get(s)
        if s_data:
            tickers_info[s] = s_data.info
    return tickers_info


if __name__ == "__main__":
    import pprint

    out = get_tickers_data(["VOOV", "VBR"])
    pprint.pprint([t for t in out.items()])
