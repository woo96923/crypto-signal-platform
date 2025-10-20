import sys
from typing import List, Dict

import requests


UPBIT_CANDLES_MINUTE_URL = "https://api.upbit.com/v1/candles/minutes/1"


def fetch_upbit_minute_candles(market: str, count: int) -> List[Dict]:
    """Fetch recent minute candles from Upbit public API.

    Returns a list of candle dicts. Upbit returns latest-first ordering.
    Raises an exception on non-200 responses.
    """
    params = {"market": market, "count": count}
    headers = {"Accept": "application/json"}
    response = requests.get(UPBIT_CANDLES_MINUTE_URL, params=params, headers=headers, timeout=10)
    if response.status_code != 200:
        raise RuntimeError(f"Upbit API error: {response.status_code} {response.text}")
    return response.json()


def format_number(value: float) -> str:
    return f"{value:,.0f}" if value >= 100 else f"{value:,.2f}"


def print_candles_pretty(candles: List[Dict]) -> None:
    """Pretty-print candle data in a simple table.

    Expected keys per candle: candle_date_time_kst, opening_price, high_price,
    low_price, trade_price, candle_acc_trade_volume.
    """
    if not candles:
        print("No candle data.")
        return

    # Upbit returns latest first; reverse to show chronological order
    candles = list(reversed(candles))

    headers = [
        "Time (KST)",
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
    ]

    rows = []
    for c in candles:
        rows.append([
            c.get("candle_date_time_kst", "-"),
            format_number(float(c.get("opening_price", 0))),
            format_number(float(c.get("high_price", 0))),
            format_number(float(c.get("low_price", 0))),
            format_number(float(c.get("trade_price", 0))),
            f"{float(c.get('candle_acc_trade_volume', 0)):.6f}",
        ])

    # Compute column widths
    col_widths = [len(h) for h in headers]
    for row in rows:
        for idx, cell in enumerate(row):
            col_widths[idx] = max(col_widths[idx], len(str(cell)))

    def fmt_row(row_vals: List[str]) -> str:
        return "  ".join(str(val).rjust(col_widths[i]) for i, val in enumerate(row_vals))

    print(fmt_row(headers))
    print("  ".join("-" * w for w in col_widths))
    for row in rows:
        print(fmt_row(row))


def main() -> None:
    market = "KRW-BTC"
    count = 5
    try:
        candles = fetch_upbit_minute_candles(market=market, count=count)
    except Exception as exc:
        print(f"Failed to fetch candles: {exc}", file=sys.stderr)
        sys.exit(1)

    print_candles_pretty(candles)


if __name__ == "__main__":
    main()


