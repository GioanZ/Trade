import parseArgs

import backtrader as bt
import backtrader.analyzers as btanal

import btToolbox.backtestingAnalysis as backtestingAnalysis

import btToolbox.backtestingRetrivesDatas as backtestingRetrivesDatas


def retrives_cerebro_with_data(data_args: dict) -> (bt.Cerebro, list):
    """
    Retrieves data and creates a cerebro instance.

    Args:
    - data_args (dict): Dictionary containing data-related arguments

    Returns:
    - bt.Cerebro: Cerebro instance
    - list: List of data analysis
    """
    # List to store data analysis
    data_analisys_list = []
    # Creating a cerebro instance
    cerebro = bt.Cerebro()

    for curr_traded in data_args["nameasset"]:
        try:
            # Retrieving data and its analysis
            data, data_analisys = backtestingRetrivesDatas.retrivesDatas(
                curr_traded, data_args
            )
            # Appending data analysis to the list
            data_analisys_list.append(data_analisys)
        except ValueError as e:
            # Handling exception if data retrieval fails
            print(curr_traded + ":\t\t\tSomething went wrong in contacting...")
            print(curr_traded + ":\t\t" + str(e) + "\n\n\n")
            print(curr_traded + "\t\t\tTry another way...\n\t\t\tUse local version...")
            # Exiting if there's an error in data import
            exit("ERROR IMPORT DATA")
        # Adding data to cerebro with asset name
        cerebro.adddata(data, name=curr_traded)

    # Returning cerebro instance and data analysis list
    return cerebro, data_analisys_list


def set_cerebro(cerebro: bt.Cerebro, data_args: dict) -> None:
    """
    Sets up the cerebro with strategies and parameters.

    Args:
    - cerebro (bt.Cerebro): Cerebro instance
    - data_args (dict): Dictionary containing data-related arguments

    Returns:
    - None
    """
    # Retrieving strategy
    retrives_strategy = backtestingRetrivesDatas.retrives_strategy(data_args)
    # Adding strategy to cerebro
    cerebro.addstrategy(retrives_strategy[0], **(retrives_strategy[1]))

    # Setting initial cash
    cerebro.broker.setcash(data_args["startcash"])

    # Setting commission
    cerebro.broker.setcommission(commission=data_args["commission"])

    # Printing starting conditions
    print("Starting Portfolio Value: %.2f" % cerebro.broker.getvalue())

    # Adding analyzers for performance analysis
    cerebro.addanalyzer(btanal.SharpeRatio_A)
    cerebro.addanalyzer(btanal.AnnualReturn)
    cerebro.addanalyzer(btanal.DrawDown)
    cerebro.addanalyzer(btanal.SQN)
    cerebro.addanalyzer(btanal.TimeReturn)
    cerebro.addanalyzer(btanal.TradeAnalyzer)


def execute() -> None:
    """
    Main execution function.

    Returns:
    - None
    """
    # Getting data arguments from command line
    data_args = parseArgs.getdata()

    # Retrieving cerebro and data analysis
    cerebro, data_analisys_list = retrives_cerebro_with_data(data_args)

    # Setting up cerebro with strategies and parameters
    set_cerebro(cerebro, data_args)

    # Running strategies
    strats = cerebro.run()

    # Analyzing results
    backtestingAnalysis.analysis(strats[0], cerebro, data_args, data_analisys_list)

    # Plotting results
    cerebro.plot(numfigs=1, style=data_args["plotstyle"])


if __name__ == "__main__":
    # Calling the main execution function
    execute()
