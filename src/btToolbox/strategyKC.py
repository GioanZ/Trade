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
import backtrader.indicators as btind

from . import loggingUtils

from . import indicatorKC as iKC

from typing import Type


class KeltnerChannelsStrategy(bt.Strategy):
    """
    Custom strategy based on Keltner Channels.

    Args:
        - period_EMA (int): Period for Exponential Moving Average (default: 20).
        - period_ATR (int): Period for Average True Range (default: 14).
        - live (bool): Flag for live trading (default: False).
        - risk_amount_buy (float): Risk amount for buy orders as a percentage of cash (default: 30%).
        - risk_amount_sell (float): Risk amount for sell orders as a percentage of cash (default: 15%).
        - stopprice (float): Stop price parameter (default: 0.01).
        - order_params_buy (float): Order parameter for buy orders (default: 1.8).
        - order_params_sell (float): Order parameter for sell orders (default: 0.8).
        - print_position (bool): Flag to print position information (default: True).
        - debug (bool): Flag for debug mode (default: False).

    Keltner Channels calcolati come segue:
        - atrlow = EMA - 2 * ATR
        - atrhigh = EMA + 2 * ATR

    Strategy Logic:
        Entry Conditions:
            - Buy Signal: Generated when the closing price crosses above the upper Keltner Band (CrossOver BUY).
            - Sell Signal: Generated when the closing price crosses below the lower Keltner Band (CrossOver SELL).

        Exit Conditions:
            - Return Inside Keltner Bands:
                - If the strategy is already in a position, exit occurs when the closing price re-enters
                within the Keltner Bands.
                - For long positions, check if the closing price is below the upper Keltner Band.
                - For short positions, check if the closing price is above the lower Keltner Band.
                If this condition is met, a signal is generated to close the position.
            - Stop Loss:
                - An alternative exit strategy is the stop loss.
                    - For long positions, the stop loss is calculated as a percentage (stopprice) below
                    the opening price.
                    - For short positions, the stop loss is calculated as a percentage (stopprice) above
                    the opening price.
                    If the closing price reaches or surpasses the stop loss level, a signal is generated
                    to close the position.

        Position Management:
            The risk amount for buy and sell orders is determined by risk_amount_buy and risk_amount_sell,
            respectively, as a percentage of available capital.
            Parameters order_params_buy and order_params_sell are added and subtracted, respectively, to
            calculate the order price based on the closing and low prices.
                - For long positions, price = d.close * (1.0 + self.p.order_params_buy / 100.0),
                - For short positions price = d.low * (1.0 - self.p.order_params_sell / 100.0)).
    """

    params = dict(
        period_EMA=20,
        period_ATR=14,
        live=False,
        risk_amount_buy=30,
        risk_amount_sell=15,
        stopprice=0.01,
        order_params_buy=1.8,
        order_params_sell=0.8,
        print_position=True,
        debug=False,
    )

    def log(self, txt: str, dt: datetime | float | None = None) -> None:
        """Logging function for the strategy."""
        loggingUtils.log(self, txt, dt)

    def notify_order(self, order: bt.Order) -> None:
        """Notification function for order events."""
        loggingUtils.notify_order(self, order)

    def __init__(self) -> None:
        """
        Initialization method for the strategy.

        Initializes various attributes, indicators, and flags for the strategy.
        """
        self.orders = {}
        self.ema = {}
        self.position_short_long = {}
        self.ema = {}
        self.atrlow = {}
        self.atrhigh = {}
        self.keltner_channels = {}
        self.flagsell = {}
        self.flagbuy = {}
        self.flagclose = {}
        self.debug = self.p.debug

        for d in self.datas:
            d_name = d._name
            self.orders[d_name] = None
            self.position_short_long[d_name] = 0
            self.ema[d_name] = btind.EMA(d, period=self.p.period_EMA)
            self.keltner_channels[d_name] = iKC.IndicatorKeltnerChannels(
                d,
                period_EMA=self.p.period_EMA,
                period_ATR=self.p.period_ATR,
                subplot=False,
            )
            self.flagsell[d_name] = -btind.CrossOver(
                d.close,
                self.keltner_channels[d_name].atrlow,
                plot=False,
                plotname="CrossOver SELL",
            )
            self.flagbuy[d_name] = btind.CrossOver(
                d.close,
                self.keltner_channels[d_name].atrhigh,
                plot=False,
                plotname="CrossOver BUY",
            )
            self.flagclose[d_name] = 0

    def params_order(self, d: Type[btfeeds.BaseData], is_buy: bool = True) -> float:
        """
        Calculate order price based on specified parameters.

        Args:
            d (Type[btfeeds.BaseData]): Data instance.
            is_buy (bool): Flag indicating if it's a buy order (default: True).

        Returns:
            float: Calculated order price.
        """
        if is_buy:
            price = d.close * (1.0 + self.p.order_params_buy / 100.0)
        else:
            price = d.low * (1.0 - self.p.order_params_sell / 100.0)
        if self.p.debug == True:
            print("Price DEBUG: ", price)
        return price

    def next(self) -> None:
        """
        Main strategy logic executed on each data point.

        Iterates over data feeds, checks conditions, and executes buy/sell orders.
        """
        for d in self.datas:
            if self.p.live:
                loggingUtils.print_values_candel(self, d)
            d_name = d._name
            # Without flagclose a close order could be cancelled if you wanted to trade but the market closed
            #   immediately after you launched the close order
            if self.flagclose[d_name] == 1:
                return
            # If it is not completed, not powerful enough, then cancel the order
            if self.orders[d_name]:
                # if (self.orders[d_name].isbuy() and self.flagbuy[d_name] < 0) or (self.orders[d_name].issell()
                #   and self.flagsell[d_name] < 0):
                loggingUtils.log(self, "%s - PENDING... CANCEL!!!" % d_name)
                self.cancel(self.orders[d_name])
                return

            # If it enters the channel => close the position
            if self.getposition(d).size != 0:
                size = self.getposition(d).size
                # long
                if self.position_short_long[d_name] > 0:
                    if self.flagbuy[d_name] < 0:
                        # order = exchange.create_order(symbol, operation, side, amount)
                        self.close(data=d, size=size)
                        loggingUtils.log(self, "%s - CLOSE ALL LONG POSIZION" % d_name)
                        self.flagclose[d_name] = 1
                # short
                elif self.position_short_long[d_name] < 0:
                    if self.flagsell[d_name] < 0:
                        self.close(data=d, size=size)
                        loggingUtils.log(self, "%s - CLOSE ALL SHORT POSITION" % d_name)
                        self.flagclose[d_name] = 1
                else:
                    loggingUtils.log(self, "%s ERROR POSITION" % d_name)
                    exit(-1)
                return

            # Valid is not performing well enough
            valid = None  # self.data.datetime.date(0) + datetime.timedelta(days=self.p.valid)

            # If it is out of the channel => open position
            if self.flagbuy[d_name] > 0:
                price = self.params_order(d, True)
                risk_amount = (self.p.risk_amount_buy / 100) * self.broker.getcash()
                size = risk_amount / price
                self.buy(
                    data=d,
                    exectype=bt.Order.Stop,
                    size=size,
                    price=price,
                    valid=valid,
                    stopprice=price * (1 - self.p.stopprice),
                    stopLossPrice=price * (1 - self.p.stopprice),
                )
                loggingUtils.log(self, "%s - BUY Create: %.2f" % (d_name, price))
            elif self.flagsell[d_name] > 0:
                price = self.params_order(d, False)
                risk_amount = (self.p.risk_amount_sell / 100) * self.broker.getcash()
                size = risk_amount / price
                self.sell(
                    data=d,
                    exectype=bt.Order.Stop,
                    size=size,
                    price=price,
                    valid=valid,
                    stopprice=price * (1 + self.p.stopprice),
                    stopLossPrice=price * (1 + self.p.stopprice),
                )
                loggingUtils.log(self, "%s - SELL Create: %.2f" % (d_name, price))
