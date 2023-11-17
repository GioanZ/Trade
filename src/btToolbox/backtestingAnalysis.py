from __future__ import annotations

import pandas as pd
import numpy as np

import backtrader as bt
from typing import OrderedDict

# Constants for number formatting
num_format = "{:.2f}"
dollar_num_format = "$ " + num_format
perc_num_format = num_format + "%"


def analysis(
    strat: list, cerebro: bt.Cerebro, data_args: list, data_analisys_list: list
) -> None:
    """
    Perform analysis on the strategy and print the results.

    Args:
        strat (bt.Strategy): Backtrader strategy instance.
        cerebro (bt.Cerebro): Backtrader engine instance.
        data_args (dict): Dictionary containing data-related arguments.
        data_analisys_list (list): List of data for analysis.

    Returns:
        None
    """

    # Extract various analysis results from the strategy
    draw_downer = strat.analyzers.drawdown.get_analysis()
    sharpe_ratio_annual = strat.analyzers.sharperatio_a.get_analysis()
    annual_return = strat.analyzers.annualreturn.get_analysis()
    sqn = strat.analyzers.sqn.get_analysis()
    timer_return = strat.analyzers.timereturn.get_analysis()
    trade_analyzer = strat.analyzers.tradeanalyzer.get_analysis()

    # Print an overview of the initial and final states of the strategy
    overview_init_end(
        data_args,
        cerebro,
        timer_return,
        annual_return,
        trade_analyzer,
        sqn,
        sharpe_ratio_annual,
        draw_downer,
    )

    # Print an overview of annual returns and related data
    overview_year(annual_return, data_analisys_list)

    # Print an overview of trade statistics
    overview_bars(trade_analyzer)

    # Print a message about the current portfolio loss
    print_message(draw_downer, cerebro.broker.getvalue())


def print_md(
    df: pd.DataFrame, end_text: str | None = None, index: bool = False
) -> None:
    """
    Pretty print a Pandas DataFrame in Markdown format.

    Args:
        df (pd.DataFrame): DataFrame to be printed.
        end_text (str | None): Additional text to be printed at the end.
        index (bool): Whether to include the DataFrame index.

    Returns:
        None
    """
    print("\n" + df.to_markdown(index=index), end_text if end_text else "")


def overview_init_end(
    data_args: dict,
    cerebro: bt.Cerebro,
    timer_return: OrderedDict,
    annual_return: OrderedDict,
    trade_analyzer: OrderedDict,
    sqn: OrderedDict,
    sharpe_ratio: OrderedDict,
    draw_downer: OrderedDict,
) -> None:
    """
    Print an overview of the initial and final states of the strategy.

    Args:
        data_args (dict): Dictionary containing data-related arguments.
        cerebro (bt.Cerebro): Backtrader engine instance.
        timer_return (OrderedDict): Timereturn analysis results.
        annual_return (OrderedDict): Annualreturn analysis results.
        trade_analyzer (OrderedDict): Tradeanalyzer analysis results.
        sqn (OrderedDict): SQN analysis results.
        sharpe_ratio (OrderedDict): Sharpe ratio analysis results.
        draw_downer (OrderedDict): Drawdown analysis results.

    Returns:
        None
    """

    # Create a DataFrame for initial strategy parameters
    df = pd.DataFrame(
        {
            "INITIAL DEPOSIT": [f"$ {data_args['startcash']}"],
            "DATE START DATA": [next(iter(timer_return))],
            "DATE END DATA": [list(timer_return.keys())[-1]],
            "COMMISSION": [data_args["commission"]],
            "CURRENCY TRADE": [data_args["currencyTrade"]],
        }
    )

    # Print initial parameters
    print_md(df)

    # Create a DataFrame for initial strategy parameters
    df = pd.DataFrame(
        {
            "TIMEFRAME": [data_args["timeframe"]],
            "EMA PERIOD": [data_args["periodEMA"]],
            "ATR PERIOD": [data_args["periodATR"]],
            "BUY RISK AMOUNT": [data_args["riskAmountBuy"]],
            "SELL RISK AMOUNT": [data_args["riskAmountSell"]],
            "STOP PRICE": [data_args["stopprice"]],
        }
    )

    # Print initial parameters
    print_md(df)

    # Create a DataFrame for total portfolio and performance metrics
    df = pd.DataFrame(
        {
            "TOTAL PORTFOLIO VALUE": [
                dollar_num_format.format(cerebro.broker.getvalue())
            ],
            "TOTAL CASH": [dollar_num_format.format(cerebro.broker.getcash())],
            "TOTAL NET PROFIT": [
                dollar_num_format.format(
                    cerebro.broker.getcash() - data_args["startcash"]
                )
            ],
            "TOTAL % NET PROFIT": [
                perc_num_format.format(
                    (cerebro.broker.getvalue() - data_args["startcash"])
                    * 100
                    / data_args["startcash"]
                )
            ],
            "YEARLY AVG % RETURN": [
                "{:.2%}".format(np.mean(list(annual_return.values())))
            ],
            "# OPEN TRADERS": [trade_analyzer["total"]["open"]],
            "# CLOSED TRADERS": [trade_analyzer["total"]["closed"]],
        }
    )

    # Print total portfolio and performance metrics
    print_md(df)

    # Create a DataFrame for additional strategy performance metrics
    print_md(
        pd.DataFrame(
            {
                "SQN": [num_format.format(sqn["sqn"])],
                "SHARPE RATIO ANNUAL": [num_format.format(sharpe_ratio["sharperatio"])],
                "MAX DRAWDOWN": [
                    dollar_num_format.format(draw_downer["max"]["moneydown"])
                ],
                "MAX % DRAWDOWN": [
                    perc_num_format.format(draw_downer["max"]["drawdown"])
                ],
                "ACTUAL DRAWDOWN": [dollar_num_format.format(draw_downer["moneydown"])],
                "ACTUAL % DRAWDOWN": [perc_num_format.format(draw_downer["drawdown"])],
            }
        )
    )


def overview_year(annual_return: OrderedDict, data_analisys_list: list) -> None:
    """
    Print an overview of annual returns and related data.

    Args:
        annual_return (OrderedDict): Annualreturn analysis results.
        data_analisys_list (list): List of data for analysis.

    Returns:
        None
    """

    # Create a DataFrame with annual return information
    df = pd.DataFrame(
        {
            "YEAR": annual_return.keys(),
            "ANNUAL % RETURN WALLET": map(
                lambda x: "{:.1%}".format(x), annual_return.values()
            ),
        }
    )

    # Define column names for additional annual data
    column_names = {
        "Year Perc": "BEGINNING-END OF YEAR",
        "Max Perc": "ANNUAL MAX % RETURN ASSET",
        "Min Perc": "ANNUAL MIN % RETURN ASSET",
    }

    # Name for date column
    date_name = "Datetime"

    # Merge with additional annual data (max, min, increase percentages)
    df = df.merge(
        annual_max_min_increase_perc_asset(data_analisys_list)[
            [date_name] + list(column_names.keys())
        ],
        left_on="YEAR",
        right_on=date_name,
    ).drop(date_name, axis=1)

    # Rename columns
    df.rename(columns=column_names, inplace=True)

    # Format percentage columns
    for col in list(column_names.values()):
        df[col] = df[col].apply(lambda x: "{:.1%}".format(x))

    # Print the final DataFrame
    print_md(df, "\n")


def overview_bars(trade_analyzer: OrderedDict) -> None:
    """
    Print an overview of trade statistics.

    Args:
        trade_analyzer (OrderedDict): Tradeanalyzer analysis results.

    Returns:
        None
    """

    def short_or_long(s_l):
        """
        Extract trade statistics for either short or long positions.

        Args:
            s_l (str): 'short' or 'long'.

        Returns:
            dict: Trade statistics for 'Won' and 'Lost'.
        """

        def won_or_lost(w_l):
            """
            Extract statistics for either won or lost trades.

            Args:
                w_l (str): 'won' or 'lost'.

            Returns:
                list: Trade statistics.
            """
            return [
                trade_analyzer[s_l][w_l],
                dollar_num_format.format(trade_analyzer[s_l]["pnl"][w_l]["total"]),
                dollar_num_format.format(trade_analyzer[s_l]["pnl"][w_l]["max"]),
                trade_analyzer["len"][s_l][w_l]["total"],
                trade_analyzer["len"][s_l][w_l]["max"],
                trade_analyzer["len"][s_l][w_l]["min"],
                num_format.format(trade_analyzer["len"][s_l][w_l]["average"]),
            ]

        return {"Won": won_or_lost("won"), "Lost": won_or_lost("lost")}

    def df_short_or_long(s_l, cols):
        """
        Create and print a DataFrame for either short or long positions.

        Args:
            s_l (str): 'short' or 'long'.
            cols (list): List of column names.

        Returns:
            None
        """
        df_short = pd.DataFrame.from_dict(
            short_or_long(s_l), orient="index", columns=cols
        )
        df_short.index.name = s_l.capitalize()
        print_md(df_short, index=True)

    # Define column names for trade statistics
    cols = [
        "# Total Position",
        "PNL Total",
        "PNL Max",
        "Length of open positions",
        "Length Max",
        "Length Min",
        "Length AVG",
    ]

    # Print trade statistics for both short and long positions
    df_short_or_long("short", cols)
    df_short_or_long("long", cols)


def annual_max_min_increase_perc_asset(datas: list) -> pd.DataFrame:
    """
    Calculate annual max, min, and increase percentages for asset data.

    Args:
        datas (list): List of asset data.

    Returns:
        None
    """

    # Initialize an empty DataFrame to store results
    df = pd.DataFrame()
    # Counter for handling the first iteration
    i = 0

    # Iterate through each dataset in the list
    for data in datas:
        # Calculate max, min, and increase percentages for each year
        first_max_min_per_year = data.groupby(data.index.year).agg(
            {"Open": "first", "Adj Close": ["max", "min", "last"]}
        )
        first_max_min_per_year.columns = [
            "First Open",
            "Max Close",
            "Min Close",
            "Last Close",
        ]
        first_max_min_per_year["Max Perc"] = (
            first_max_min_per_year["Max Close"] - first_max_min_per_year["First Open"]
        ) / first_max_min_per_year["First Open"]
        first_max_min_per_year["Min Perc"] = (
            first_max_min_per_year["Min Close"] - first_max_min_per_year["First Open"]
        ) / first_max_min_per_year["First Open"]
        first_max_min_per_year["Year Perc"] = (
            first_max_min_per_year["Last Close"] - first_max_min_per_year["First Open"]
        ) / first_max_min_per_year["First Open"]

        # If it's the first iteration, set the DataFrame
        if i == 0:
            df = pd.DataFrame(first_max_min_per_year)
        else:
            # Concatenate with the existing DataFrame for subsequent iterations
            df1 = pd.DataFrame(first_max_min_per_year)
            df = pd.concat([df, df1])

        # Increment the counter
        i += 1

    # Group by the 'Datetime' column and sum values for each date
    df = df.groupby("Datetime").sum().reset_index()

    return df


def print_message(draw_downer: OrderedDict, value: float) -> None:
    """
    Print a message about the current portfolio loss.

    Args:
        draw_downer (OrderedDict): Drawdown analysis results.
        value (float): Current portfolio value.

    Returns:
        None
    """
    print(
        f"\nThe current loss from the maximum value reached by the portfolio is $ {draw_downer['moneydown']:.2f}, "
        f"which occurred {draw_downer['len']} bars ago, i.e., the portfolio fell by about "
        f"{draw_downer['drawdown']:.2f}%, until it reached the current level of $ {value:.2f}."
        f"\nIn order to carry out this strategy you had to be prepared to bear a loss of "
        f"{draw_downer['max']['drawdown']:.2f}%, about $ {draw_downer['max']['moneydown']:.2f} from the maximum "
        f"value reached by the portfolio."
    )
