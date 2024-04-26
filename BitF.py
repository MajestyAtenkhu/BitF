import streamlit as st
import requests
import json
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

def query_bitcoin(network="bitcoin", limit=10, offset=0, from_date=None, till_date=None):
    url = "https://graphql.bitquery.io"
    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": "BQY8QMKaYn8d2fN4jqXRhjd3iLuFHfYf"  # Replace 'your_api_key' with your actual BitQuery API key
    }
    query = """
    query ($network: BitcoinNetwork!, $limit: Int!, $offset: Int!, $from: ISO8601DateTime, $till: ISO8601DateTime) {
    bitcoin(network: $network) {
        blocks(
        options: {desc: "height", limit: $limit, offset: $offset}
        date: {since: $from, till: $till}
        ) {
        timestamp {
            time(format: "%Y-%m-%d %H:%M:%S")
        }
        height
        difficulty
        transactionCount
        blockSizeBigInt
        blockSize
        blockHash
        }
    }
    }
    """
    variables = {
        "network": network,
        "limit": limit,
        "offset": offset,
        "from": from_date,
        "till": till_date
    }
    response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        st.error(f"API request failed with status code: {response.status_code}")
        return None

def setup_interface():
    st.title('Bitcoin On-Chain Data Viewer')
    limit = st.number_input('Number of blocks', min_value=1, value=10)
    from_date = st.date_input("From date", datetime(2020, 1, 1))
    till_date = st.date_input("Till date", datetime.now())
    network = st.selectbox('Network', ['bitcoin', 'bitcoin-cash', 'bitcoin-sv', 'litecoin', 'dogecoin'])
    return network, limit, from_date, till_date

def fetch_bitcoin_hourly_data():
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {"vs_currency": "usd", "days": "2"}  # Fetch data for the last 2 days to get hourly data
    response = requests.get(url, params=params)
    data = response.json()
    prices = [item[1] for item in data["prices"]]
    timestamps = [datetime.fromtimestamp(item[0] / 1000) for item in data["prices"]]
    df = pd.DataFrame({"Timestamp": timestamps, "Price": prices})
    return df

def plot_price_chart(df):
    plt.figure(figsize=(10, 5))
    plt.plot(df['Timestamp'], df['Price'], label='BTC Price (USD)', marker='o')
    plt.xlabel('Timestamp')
    plt.ylabel('Price (USD)')
    plt.title('Hourly Bitcoin Price Over the Last 2 Days')
    plt.xticks(rotation=45)
    plt.legend()
    st.pyplot(plt)

def calculate_and_plot_volatility(df):
    df.set_index('Timestamp', inplace=True)
    df['Hourly Volatility'] = df['Price'].rolling(window=24).std()
    plt.figure(figsize=(10, 5))
    plt.plot(df.index, df['Hourly Volatility'], label='Hourly Volatility', color='red', marker='o')
    plt.xlabel('Timestamp')
    plt.ylabel('Volatility')
    plt.title('Hourly Bitcoin Volatility Over the Last 2 Days')
    plt.xticks(rotation=45)
    plt.legend()
    st.pyplot(plt)


def main():
    st.title('Bitcoin On-Chain Data and Market Viewer')
    
    # Fetch and plot Bitcoin price data
    bitcoin_price_data = fetch_bitcoin_hourly_data()
    plot_price_chart(bitcoin_price_data)
    calculate_and_plot_volatility(bitcoin_price_data)
    
    # Existing functionality for blockchain data
    network, limit, from_date, till_date = setup_interface()
    if st.button('Load Data'):
        data = query_bitcoin(network=network, limit=limit, from_date=str(from_date), till_date=str(till_date))
        if data and 'data' in data and 'bitcoin' in data['data'] and 'blocks' in data['data']['bitcoin']:
            blocks = data['data']['bitcoin']['blocks']
            if blocks:
                df = pd.json_normalize(blocks)
                plot_data(df)  # Plots block size and transactions
                st.write(df)  # Displays the DataFrame as a table
        else:
            st.error("Failed to fetch data or data is incomplete.")


if __name__ == "__main__":
    main()
