import config

import backtrader as bt

from ccxtbt import CCXTStore

from typing import Type

import time
from datetime import datetime, timedelta


def set_store(exchange_id: str, currency_trade: str) -> CCXTStore:
    """
    Set up and return a CCXTStore instance.

    Args:
        exchange_id (str): Identifier for the exchange.
        currency_trade (str): Currency used for trading.

    Returns:
        CCXTStore: Configured CCXTStore instance.
    """
    # Create our store
    store_config = {
        "apiKey": config.api_key,
        "secret": config.api_secret,
        "enableRateLimit": True,
        "nonce": lambda: str(int(time.time() * 1000)),
    }

    store = CCXTStore(
        exchange=exchange_id,
        currency=currency_trade,
        config=store_config,
        retries=5,
        sandbox=True,
    )  # https://testnet.binance.vision/

    return store


def retrieves_data(
    curr_traded: str, currency_trade: str, store: CCXTStore, data_args: dict
) -> Type[CCXTStore.DataCls]:
    """
    Retrieve data using CCXTStore based on specified parameters.

    Args:
        curr_traded (str): Symbol of the traded asset.
        currency_trade (str): Currency used for trading.
        store (CCXTStore): CCXTStore instance.
        data_args (dict): Dictionary containing data-related arguments.

    Returns:
        Type[CCXTStore.DataCls]: Retrieved data instance.
    """
    name_asset = curr_traded + "/" + currency_trade
    name = curr_traded + currency_trade

    # TODO: Fix why cannot see price cost and comm when open and close a position

    minutes_past = data_args["periodEMA"]

    if data_args["timeframe"] == "1h":
        minutes_past *= 65
        compression_minutes = 60
    elif data_args["timeframe"] == "1m":
        minutes_past += 2
        compression_minutes = 1
    else:  # 1d
        # TODO
        exit("COMING SOON IMPLEMENTATION 1d")
    debug = True if data_args["levelDebug"] >= 2 else False
    # Get our data
    # Drop newest will prevent us from loading partial data from incomplete candles
    hist_start_date = datetime.utcnow() - timedelta(minutes=minutes_past)
    data = store.getdata(
        dataname=name_asset,
        name=name,
        timeframe=bt.TimeFrame.Minutes,
        fromdate=hist_start_date,
        compression=compression_minutes,
        drop_newest=data_args["dropNewest"],
        debug=debug,
    )  # , historical=True)

    return data


def retrive_broker_mapping(exchange_id: str) -> dict:
    """
    Retrieve broker mapping for order types and order status.

    Args:
        exchange_id (str): Identifier for the exchange.

    Returns:
        dict: Broker mapping for order types and status.
    """
    if exchange_id == "binance":
        broker_mapping = {
            "order_types": {
                bt.Order.Market: "MARKET",
                bt.Order.Limit: "LIMIT",
                bt.Order.Stop: "LIMIT",
                bt.Order.StopLimit: "STOP_LOSS_LIMIT",
            },
            "mappings": {
                "closed_order": {"key": "status", "value": "closed"},
                "canceled_order": {"key": "status", "value": "canceled"},
            },
        }
    else:
        exit("COMING SOON MORE BROKER MAPPING")  # TODO

    return broker_mapping
