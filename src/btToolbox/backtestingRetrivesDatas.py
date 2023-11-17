import time
import os
import pandas as pd
from datetime import datetime

import yfinance as yf

import ccxt

import backtrader.feeds as btfeeds

from .strategyKC import KeltnerChannelsStrategy

from typing import Tuple, Type, Dict

# Flags for different functionalities
FLAG_YF = False
FLAG_1H = True
CSV = True if FLAG_YF == True else True  # TODO insert choice in parseArgs.py


def retireves_data_path(file_name: str) -> str:
    """
    Get the path for data files.

    Args:
        file_name (str): The name of the data file.

    Returns:
        str: The full path for the data file.
    """
    return os.path.join(os.path.dirname(__file__), "../../datacsv/" + file_name)


def retrievesBinance(
    name_file: str, from_date: datetime, timeframe: str
) -> pd.DataFrame:
    """
    Retrieve data from the Binance exchange.

    Args:
        name_file (str): The name of the traded asset.
        from_date (datetime): The starting date for data retrieval.
        timeframe (str): The timeframe for OHLCV data.

    Returns:
        pd.DataFrame: The retrieved data in DataFrame format.
    """

    # Initialize the Binance exchange object
    exchange = ccxt.binance()  # TODO: change if is not 1h
    flag = 2
    start_date_int = exchange.parse8601(from_date.strftime("%Y-%m-%dT%H:%M:%SZ"))

    df = None
    while flag != 0:
        print(start_date_int, timeframe)
        if FLAG_1H:
            print(
                "I'M USING 1 HOUR TIMEFRAME, IF YOU WANT 1MINUTE OR OTHER CHANGE MANUALLY IN THE CODE"
            )  # TODO fix and delete this prints
            print("THE FIX WILL COME SOON")
            timeframe = "1h"

        # Fetch OHLCV data from Binance
        ohlc = exchange.fetch_ohlcv(
            name_file, timeframe=timeframe, since=start_date_int
        )
        old_date = start_date_int
        start_date_int = ohlc[-1][0] + 3600000

        if flag == 2:
            df = pd.DataFrame(
                ohlc, columns=["Date", "Open", "High", "Low", "Close", "Volume"]
            )
            df["Date"] = pd.to_datetime(df["Date"], unit="ms")
            df.set_index("Date", inplace=True)
            flag = 1
        else:
            nuovi_df = pd.DataFrame(
                ohlc, columns=["Date", "Open", "High", "Low", "Close", "Volume"]
            )
            nuovi_df["Date"] = pd.to_datetime(nuovi_df["Date"], unit="ms")
            nuovi_df.set_index("Date", inplace=True)
            df = df.append(nuovi_df)
        print(df)

        # Check if additional data is needed
        if int(time.time()) * 1000 <= start_date_int or old_date == start_date_int:
            flag = 0

    # Drop the last row to avoid duplicated data
    df = df.drop(df.index[-1])

    # Adjust the DataFrame columns
    df["Adj Close"] = df["Close"]
    df["Datetime"] = df.index
    df.set_index("Datetime", inplace=True)
    df = df[["Open", "High", "Low", "Close", "Adj Close", "Volume"]]
    # df.to_csv(retireves_data_path('binance.csv'), index=True)
    print(df)

    return df


def retrivesDatas(
    curr_traded: str, data_args: dict
) -> (btfeeds.PandasData, pd.DataFrame):
    """
    Retrieve data for backtesting.

    Args:
        curr_traded (str): The symbol for the traded asset.
        data_args (dict): Dictionary containing data-related arguments.

    Returns:
        Tuple[btfeeds.PandasData, pd.DataFrame]: A tuple containing backtrader data feed and the data in DataFrame format.
    """
    # Create the name of the traded asset
    name_asset = curr_traded + "/" + data_args["currencyTrade"]

    # Check the data source and fetch data accordingly
    if FLAG_YF:
        if name_asset != "BTC/USDT":
            exit(
                "ERROR: UPCOMING ON YT THE POSIBILITY OF MULTIPLE CHOICE, FOR NOW BTC/USD"
            )  # TODO
        name_asset = curr_traded + "/" + "USD"
        data_analisys = yf.download(
            name_asset,
            start=data_args["fromdate"],
            end=data_args["todate"],
            interval=data_args["timeframe"],
        )
        data = btfeeds.PandasData(dataname=data_analisys)
        print(name_asset + ":\t\t\tCorrectly contacted Yahoo Financials")
    else:
        if CSV:
            if name_asset != "BTC/USDT":
                exit(
                    "ERROR: UPCOMING ON binance.csv THE POSIBILITY OF MULTIPLE CHOICE, FOR NOW BTC/USDT"
                )  # TODO

            name_file = retireves_data_path("binance.csv")

            data = btfeeds.GenericCSVData(dataname=name_file)

            data_analisys = pd.read_csv(retireves_data_path("binance.csv"))

            # Converts 'Datetime' column to a datetime object
            data_analisys["Datetime"] = pd.to_datetime(data_analisys["Datetime"])

            # Set 'Datetime' as the index of the DataFrame
            data_analisys.set_index("Datetime", inplace=True)

            print(name_asset + ":\t\t\tCorrectly contacted binance.csv")
        else:
            data_analisys = retrievesBinance(
                name_asset, data_args["fromdate"], data_args["timeframe"]
            )
            data = btfeeds.PandasData(dataname=data_analisys)
            print(name_asset + ":\t\t\tCorrectly contacted Binance")

    return data, data_analisys


def retrives_strategy(data_args: dict) -> Tuple[Type, Dict]:
    """
    Retrieve the backtesting strategy and its parameters.

    Args:
        data_args (dict): Dictionary containing strategy-related arguments.

    Returns:
        Tuple[Type, Dict]: A tuple containing the strategy class and its parameters.
    """
    if FLAG_YF:
        return KeltnerChannelsStrategy, dict(  # TODO
            period_EMA=24,
            period_ATR=4,
            live=False,
            risk_amount_buy=50,
            risk_amount_sell=20,
            stopprice=0.01,
            order_params_buy=1.8,
            order_params_sell=0.8,
        )
    else:
        return KeltnerChannelsStrategy, dict(
            period_EMA=data_args["periodEMA"],
            period_ATR=data_args["periodATR"],
            live=data_args["live"],
            risk_amount_buy=data_args["riskAmountBuy"],
            risk_amount_sell=data_args["riskAmountSell"],
            stopprice=data_args["stopprice"],
            order_params_buy=data_args["orderParamBuy"],
            order_params_sell=data_args["orderParamSell"],
        )
