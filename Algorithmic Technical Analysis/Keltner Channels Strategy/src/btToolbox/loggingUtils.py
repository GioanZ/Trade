from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
    annotations,
)

from datetime import datetime

import backtrader as bt
import backtrader.feeds as btfeeds

from typing import Type


def log(self, txt: str, dt: datetime | float | None = None) -> None:
    """
    Custom log function to print strategy-specific logs.

    Args:
        self: Reference to the strategy instance.
        txt (str): Text to be logged.
        dt (datetime | float | None): Datetime or float timestamp. Defaults to None.

    Returns:
        None
    """
    if self.p.print_position:
        # Logging function fot this strategy
        dt = dt or self.data.datetime[0]
        if isinstance(dt, float):
            dt = bt.num2date(dt)
        print("%s, %s" % (dt.isoformat(), txt))
    # bt.num2date(self.data.datetime[0]).isoformat() # TODO


def notify_order(self, order: bt.Order) -> None:
    """
    Notification function for order status changes.

    Args:
        self: Reference to the strategy instance.
        order (bt.Order): Order object representing the current order.

    Returns:
        None
    """
    d_name = order.data._name
    if order.status in [order.Submitted, order.Accepted]:
        if self.debug == True:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            self.log("%s - ORDER ACCEPTED/SUBMITTED" % d_name, dt=order.created.dt)
        self.orders[d_name] = order
    else:
        # Handling order status other than Submitted or Accepted
        if order.status in [order.Completed]:
            # Handling order status Completed
            if order.isbuy():
                # Handling Buy order execution
                self.position_short_long[d_name] = 1
                if self.debug == True:
                    # Debug mode logging for Buy execution
                    self.log(
                        "%s - BUY EXECUTED DEBUG, Price: %s, Cost: %s, Comm %.2f"
                        % (
                            d_name,
                            order.executed.price,
                            order.executed.value,
                            order.executed.comm,
                        )
                    )
                    print("USDT present in the wallet %.2f" % self.broker.getvalue())
                else:
                    self.log(
                        "%s - BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f"
                        % (
                            d_name,
                            order.executed.price,
                            order.executed.value,
                            order.executed.comm,
                        )
                    )
            else:  # Sell
                # Handling Sell order execution
                self.position_short_long[d_name] = -1
                if self.debug == True:
                    # Debug mode logging for Sell execution
                    self.log(
                        "%s - SELL EXECUTED DEBUG, Price: %s, Cost: %s, Comm %s"
                        % (
                            d_name,
                            order.executed.price,
                            order.executed.value,
                            order.executed.comm,
                        )
                    )
                    print("USDT present in the wallet %.2f" % self.broker.getvalue())
                else:
                    self.log(
                        "%s - SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f"
                        % (
                            d_name,
                            order.executed.price,
                            order.executed.value,
                            order.executed.comm,
                        )
                    )
            self.flagclose[d_name] = 0
        else:
            # Handling order status other than Completed
            self.position_short_long[d_name] = 0
            if order.status in [order.Partial]:
                self.log("%s - ORDER Partial: %s" % (d_name, order.status))
            elif order.status in [order.Rejected]:
                self.log("%s - ORDER Rejected: %s" % (d_name, order.status))
            elif order.status in [order.Margin]:
                self.log("%s - ORDER Margin: %s" % (d_name, order.status))
            elif order.status in [order.Cancelled]:
                self.log("%s - ORDER Cancelled: %s" % (d_name, order.status))
            elif order.status in [order.Expired]:
                self.log("%s - ORDER Expired: %s" % (d_name, order.status))

        # Sentinel to None: new orders allowed
        self.orders[d_name] = None


def print_values_candel(self, d: Type[btfeeds.BaseData]) -> None:
    """
    Custom function to print candle values.

    Args:
        self: Reference to the strategy instance.
        d (Type[btfeeds.BaseData]): Candle data.

    Returns:
        None
    """
    if self.p.print_position:
        print(
            "{} - {} | O: {} H: {} L: {} C: {} V:{}".format(
                d.datetime.datetime(),
                d._name,
                d.open[0],
                d.high[0],
                d.low[0],
                d.close[0],
                d.volume[0],
            )
        )
