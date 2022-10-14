import yfinance as yf
from prefect import flow, task, get_run_logger
from prefect.tasks import task_input_hash

@task(retries=3, cache_key_fn=task_input_hash)
def get_cashflow(ticker):
    return yf.Ticker(ticker).info.get("operatingCashflow")

@task
def output_cashflow(ticker, cashflow):
    logger = get_run_logger()

    formatted = "${:0,.2f}".format(cashflow)
    logger.info(f"{ticker} cash flow - {formatted}")

@flow
def print_cashflow(ticker):
    cashflow = get_cashflow(ticker)
    output_cashflow(ticker, cashflow)

@flow
def print_multiple_cashflows():
    print_cashflow("MSFT")
    print_cashflow("AMZN")
    print_cashflow("GOOG")

if __name__ == "__main__":
    print_multiple_cashflows()
