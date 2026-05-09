from datetime import datetime


def company(data):
    return {
        "name": data.get("name"),
        "ticker": data.get("ticker"),
        "exchange_code": data.get("exchangeCode"),
        "start_date": data.get("startDate"),
        "description": data.get("description"),
    }


def summary(data):
    prev_close = data.get("prevClose")
    last = data.get("last") or data.get("tngoLast")

    if last is not None and prev_close is not None:
        change = round((last - prev_close), 2)
        change_pct = round((change / prev_close * 100), 2)
    else:
        change = None
        change_pct = None

    return {
        "ticker": data.get("ticker"),
        "date": (data.get("timestamp", "") or "")[:10],
        "prev_close": prev_close,
        "open": data.get("open"),
        "high": data.get("high"),
        "low": data.get("low"),
        "last_price": last,
        "change": change,
        "change_percent": change_pct,
        "volume": data.get("volume"),
    }
