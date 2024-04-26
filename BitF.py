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

def plot_data(df):
    plt.figure(figsize=(10, 5))
    plt.plot(df['timestamp.time'], df['blockSize'], label='Block Size', marker='o')
    plt.plot(df['timestamp.time'], df['transactionCount'], label='Transactions Per Block', marker='o')
    plt.xlabel('Timestamp')
    plt.ylabel('Block Size / Transactions')
    plt.title('Block Size and Transactions Per Block Over Time')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(plt)

def main():
    network, limit, from_date, till_date = setup_interface()
    if st.button('Load Data'):
        data = query_bitcoin(network=network, limit=limit, from_date=str(from_date), till_date=str(till_date))
        if data and 'data' in data and 'bitcoin' in data['data'] and 'blocks' in data['data']['bitcoin']:
            blocks = data['data']['bitcoin']['blocks']
            if blocks:
                df = pd.json_normalize(blocks)
                st.write(df)
                plot_data(df)
        else:
            st.error("Failed to fetch data or data is incomplete.")

if __name__ == "__main__":
    main()
