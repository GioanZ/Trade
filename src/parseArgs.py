from __future__ import annotations

import argparse
from argparse import Namespace

from datetime import datetime


def getdata(live: bool | None = False) -> dict:
    """
    Retrieves and processes command-line arguments to create a dictionary of data-related arguments.

    Args:
    - live (bool | None): Flag indicating live mode

    Returns:
    - dict: Dictionary containing data-related arguments
    """
    # Parsing command-line arguments using a separate function
    args = parse_args(live)
    # Initializing a dictionary for data-related arguments
    dfkwargs = dict()

    array = []
    for namefile in args.nameasset.split(","):
        array.append(namefile.strip())
    # Storing asset names in the dictionary
    dfkwargs["nameasset"] = array

    fromdate = datetime.strptime(args.fromdate, "%Y-%m-%d")
    # Storing start date in the dictionary
    dfkwargs["fromdate"] = fromdate

    todate = datetime.strptime(args.todate, "%Y-%m-%d")
    # Storing end date in the dictionary
    dfkwargs["todate"] = todate

    # Storing various arguments in the dictionary
    dfkwargs["plotstyle"] = args.plotstyle
    dfkwargs["startcash"] = args.startcash
    dfkwargs["currencyTrade"] = args.currencyTrade
    dfkwargs["commission"] = args.commission
    dfkwargs["periodEMA"] = 13  # args.periodEMA
    dfkwargs["periodATR"] = 7  # args.periodATR
    dfkwargs["riskAmountBuy"] = args.riskAmountBuy
    dfkwargs["riskAmountSell"] = args.riskAmountSell
    dfkwargs["stopprice"] = 0.01  # args.stopprice
    dfkwargs["orderParamBuy"] = 0.6  # args.orderParamBuy
    dfkwargs["orderParamSell"] = 0.7  # args.orderParamSell
    dfkwargs["live"] = args.live
    dfkwargs["levelDebug"] = args.levelDebug

    if args.timeframe1d:
        dfkwargs["timeframe"] = "1d"
    elif args.timeframe1m:
        dfkwargs["timeframe"] = "1m"

    if (
        args.timeframe1h or "timeframe" not in dfkwargs
    ):  # If more than one timeframe is selected, the default setting is 1h.
        dfkwargs["timeframe"] = "1h"
        if dfkwargs["levelDebug"] > 1:
            # If debug requires more data (=> 1m)
            dfkwargs["timeframe"] = "1m"

    dfkwargs["dropNewest"] = args.dropNewest
    dfkwargs["exchangeId"] = args.exchangeId

    # Returning the dictionary containing data-related arguments
    return dfkwargs


def parse_args(live: bool | None = False) -> Namespace:
    """
    Parses command-line arguments.

    Args:
    - live (bool | None): Flag indicating live mode

    Returns:
    - Namespace: Parsed arguments
    """
    # Creating an argument parser
    parser = argparse.ArgumentParser(description="Showcase for Order Execution Types")

    # Adding various arguments to the parser
    parser.add_argument(
        "--nameasset",
        "-na",
        required=False,
        default="BTC",
        help="Activities to be negotiated",
    )
    parser.add_argument(
        "--fromdate",
        "-f",
        required=False,
        default="2021-01-01",
        help="Starting date in YYYY-MM-DD format",
    )
    parser.add_argument(
        "--todate",
        "-t",
        required=False,
        default="2023-10-07",
        help="Ending date in YYYY-MM-DD format",
    )
    parser.add_argument(
        "--plotstyle",
        "-ps",
        required=False,
        default="bar",
        choices=["bar", "line", "candle"],
        help="Plot the read data",
    )
    parser.add_argument(
        "--startcash",
        "-sc",
        required=False,
        type=int,
        default=10000.0,
        help="Starting cash",
    )
    parser.add_argument(
        "--currencyTrade",
        "-ct",
        required=False,
        default="USDT",
        help="Currency for trading",
    )
    parser.add_argument(
        "--commission",
        "-cm",
        required=False,
        type=float,
        default=0.0 if live == True else 0.001,
        help="Commission rate",
    )
    parser.add_argument(
        "--periodEMA",
        "-pema",
        required=False,
        type=int,
        default=13 if live == True else 13,
        help="EMA period",
    )  # 24)
    parser.add_argument(
        "--periodATR",
        "-patr",
        required=False,
        type=int,
        default=7 if live == True else 7,
        help="ATR period",
    )  # 24)
    parser.add_argument(
        "--riskAmountBuy",
        "-rab",
        required=False,
        type=int,
        default=70,
        help="Buy risk amount",
    )
    parser.add_argument(
        "--riskAmountSell",
        "-ras",
        required=False,
        type=int,
        default=30,
        help="Sell risk amount",
    )
    parser.add_argument(
        "--stopprice",
        "-stpp",
        required=False,
        type=float,
        default=0.01,
        help="Stop price",
    )
    parser.add_argument(
        "--orderParamBuy",
        "-opb",
        required=False,
        type=float,
        default=0.4 if live == True else 0.6,
        help="Buy order parameter",
    )  # 1.8)
    parser.add_argument(
        "--orderParamSell",
        "-ops",
        required=False,
        type=float,
        default=0.7 if live == True else 0.7,
        help="Sell order parameter",
    )  # 0.8)
    parser.add_argument(
        "--live", "-lv", required=False, default=live, help="Live mode flag"
    )
    parser.add_argument(
        "--levelDebug", "-ld", required=False, type=int, default=1, help="Debug level"
    )
    parser.add_argument(
        "--timeframe1m", "-t1m", required=False, default=False, help="1m timeframe"
    )
    parser.add_argument(
        "--timeframe1h", "-t1h", required=False, default=False, help="1h timeframe"
    )
    parser.add_argument(
        "--timeframe1d", "-t1d", required=False, default=False, help="1d timeframe"
    )
    parser.add_argument(
        "--dropNewest", "-dn", required=False, default=False, help="Drop newest"
    )
    parser.add_argument(
        "--exchangeId", "-exid", required=False, default="binance", help="Exchange ID"
    )

    # Parsing and returning the arguments
    return parser.parse_args()
