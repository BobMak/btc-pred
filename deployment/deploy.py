import streamlit as st
import tensorflow as tf
import pickle
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import yfinance as yf
from load_data import load_btc_data, read_preprocessor, create_model
from load_data import predict_future_values
from load_data import MODEL_PATH, FILE_PATH

model = create_model(MODEL_PATH)
processor = read_preprocessor(FILE_PATH)


def create_app():
    st.title("Bitcoin Price Prediction")

    ## To ensure tha date other than current date is not selected
    today = datetime.today().date()
    date = st.date_input("Select the date", max_value = today)
    sel_date = date.strftime('%Y-%m-%d')

    st.write("You selected date: ", sel_date)

    st.title("Predicted Price for the next 7 days:")

    data = load_btc_data(sel_date)

    if st.button("Predict"):
        predictions = predict_future_values(model, processor, data, data.index.tolist(), num_predictions=7)

        st.write("Predictions:")
        st.write(predictions)

        max_high = predictions['High'].max()
        min_low = predictions['Low'].min()
        avg_close = predictions['Close'].mean()

        max_high_index = predictions['High'].idxmax().strftime('%Y-%m-%d')
        min_low_index = predictions['Low'].idxmin().strftime('%Y-%m-%d')

        st.write("Predicted High: ", max_high)
        st.write("Predicted Low: ", min_low)
        st.write("Predicted Average Close: ", avg_close)
        st.write("Predicted Highest High day: ", max_high_index)
        st.write("Predicted Lowest Low day: ", min_low_index)


if __name__ == '__main__':
    create_app()
