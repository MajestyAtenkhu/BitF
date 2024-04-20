import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime

# Define the function to query Bitcoin data
def query_bitcoin(network="bitcoin", limit=1, offset=0, from_date=None, till_date=None):
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

# Set up the Streamlit interface
st.title('Bitcoin On-Chain Data Viewer')

# User inputs for the API query
limit = st.number_input('Number of blocks', min_value=1, value=5)
from_date = st.date_input("From date", datetime(2020, 1, 1))
till_date = st.date_input("Till date", datetime.now())
network = st.selectbox('Network', ['bitcoin', 'bitcoin-cash', 'bitcoin-sv', 'litecoin', 'dogecoin'])

# Button to trigger data loading
if st.button('Load Data'):
    data = query_bitcoin(network=network, limit=limit, from_date=str(from_date), till_date=str(till_date))
    if data:
        blocks = data['data']['bitcoin']['blocks']
        df = pd.json_normalize(blocks)
        st.write(df)
    else:
        st.error("Failed to fetch data. Check your API key and network settings.")
