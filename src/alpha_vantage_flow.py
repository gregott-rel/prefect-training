from prefect import flow, task, unmapped, get_run_logger
from prefect.blocks.system import Secret
import requests
import csv

@task
def get_stock_symbols():
    return ["IBM", "MSFT", "GOOGL"]

@task
def get_api_key():
    secret_block = Secret.load("alphavantageapikey")

    # Access the stored secret
    return secret_block.get()

@task
def get_stock_data(api_key, symbol):
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={api_key}'
    r = requests.get(url)
    data = r.json()

    return data

@task
def clean_and_aggregate_data(stock_data):
    symbol = stock_data.get("Meta Data").get("2. Symbol")
    time_series = stock_data.get("Time Series (5min)")

    min = None
    max = None

    for key in time_series:
        slice_min = time_series.get(key).get("3. low")
        slice_max = time_series.get(key).get("2. high")

        if min == None or slice_min < min:
            min = slice_min

        if max == None or slice_max > max:
            max = slice_max

    return [symbol, min, max]

@task
def save_results(result_array):
    header = ['symbol', 'min', 'max']

    with open('alpha_vantage.csv', 'w', encoding='UTF8') as f:
        writer = csv.writer(f)

        writer.writerow(header)

        for row in result_array:
            writer.writerow(row)

@flow
def alpha_vantage_etl(symbols = []):
    key = get_api_key()

    stock_data = get_stock_data.map(unmapped(key), symbols)
    aggregated = clean_and_aggregate_data.map(stock_data)

    save_results(aggregated)


if __name__ == "__main__":
    alpha_vantage_etl()
