from __future__ import absolute_import, division, print_function, unicode_literals

import backtrader as bt
import backtrader.indicators as btind


class IndicatorKeltnerChannels(bt.Indicator):
    """
    Custom indicator class for Keltner Channels

    Functionality:
    - This indicator consists of two lines, 'atrlow' and 'atrhigh,'
    with the default color cyan. These lines represent the bands of
    the Exponential Moving Average (EMA) with a default period of 20.
    One line is incremented, and the other is decremented by twice the
    value of the Average True Range (ATR) with a default period of 14.

    """

    # Define lines for the indicator
    lines = (
        "atrlow",
        "atrhigh",
    )

    # Define plot information
    plotinfo = dict(subplot=False, plotname="Keltner Channel")

    # Define plot lines with colors
    plotlines = dict(
        atrlow=dict(color="cyan"),
        atrhigh=dict(color="cyan"),
    )

    # Define parameters for the indicator
    params = dict(
        period_EMA=20,  # Period for Exponential Moving Average
        period_ATR=14,  # Period for Average True Range
    )

    def __init__(self) -> None:
        """
        Initialization method for the indicator.

        Calculates Keltner Channels based on Exponential Moving Average (EMA) and Average True Range (ATR).
        """

        # Calculate Exponential Moving Average (EMA) of the input data
        ema = btind.EMA(self.data, period=self.p.period_EMA)

        # Calculate twice the Average True Range (ATR) of the input data
        atr_x_2 = btind.ATR(self.data, period=self.p.period_ATR) * 2

        # Calculate Keltner Channels: lower and upper bands
        self.l.atrlow = ema - atr_x_2
        self.l.atrhigh = ema + atr_x_2
