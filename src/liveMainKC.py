import backtrader as bt

import parseArgs

from btToolbox import retrievesDataBroker

from btToolbox.strategyKC import KeltnerChannelsStrategy


def create_cerebro_with_data(data_args: dict) -> bt.Cerebro:
    """
    Creates a cerebro instance and adds data.

    Args:
    - data_args (dict): Dictionary containing data-related arguments

    Returns:
    - bt.Cerebro: Cerebro instance
    """
    # Creating a cerebro instance with quicknotify enabled
    cerebro = bt.Cerebro(quicknotify=True)

    # Setting up data store and broker
    store = retrievesDataBroker.set_store(
        data_args["exchangeId"], data_args["currencyTrade"]
    )
    broker = store.getbroker(
        broker_mapping=retrievesDataBroker.retrive_broker_mapping(
            data_args["exchangeId"]
        )
    )
    # Setting broker for cerebro
    cerebro.setbroker(broker)

    # Adding data for each asset
    for curr_traded in data_args["nameasset"]:
        try:
            # Retrieving data for the asset
            data = retrievesDataBroker.retrieves_data(
                curr_traded, data_args["currencyTrade"], store, data_args
            )
            print(curr_traded + ":\t\t\tCorrectly contacted " + data_args["exchangeId"])
        except ValueError as e:
            print("ERROR IMPORT DATA")
            exit(-1)
        # Adding data to cerebro with asset name
        cerebro.adddata(data, name=curr_traded)

    # Returning the cerebro instance
    return cerebro


def set_cerebro(cerebro: bt.Cerebro, data_args: dict) -> None:
    """
    Sets up the cerebro with the KeltnerChannelsStrategy and parameters.

    Args:
    - cerebro (bt.Cerebro): Cerebro instance
    - data_args (dict): Dictionary containing data-related arguments

    Returns:
    - None
    """
    # Adding KeltnerChannelsStrategy to cerebro with provided parameters
    cerebro.addstrategy(
        KeltnerChannelsStrategy,
        period_EMA=data_args["periodEMA"],
        period_ATR=data_args["periodATR"],
        live=data_args["live"],
        risk_amount_buy=data_args["riskAmountBuy"],
        risk_amount_sell=data_args["riskAmountSell"],
        stopprice=data_args["stopprice"],
        order_params_buy=data_args["orderParamBuy"],
        order_params_sell=data_args["orderParamSell"],
        debug=True if data_args["levelDebug"] > 0 else False,
    )

    # Setting the commission
    cerebro.broker.setcommission(commission=data_args["commission"])

    # Printing starting conditions
    print("USDT present in the wallet %.2f" % cerebro.broker.getvalue())


def execute() -> None:
    """
    Main execution function.

    Returns:
    - None
    """
    # Retrieves input parameters
    # Getting data arguments from command line with verbose mode
    data_args = parseArgs.getdata(True)

    # Creating cerebro with data
    cerebro = create_cerebro_with_data(data_args)

    # Setting up cerebro with strategies and parameters
    set_cerebro(cerebro, data_args)

    # Running strategies
    cerebro.run()


if __name__ == "__main__":
    # Calling the main execution function
    execute()
