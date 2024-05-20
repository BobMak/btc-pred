import os

import pandas as pd
import altair as alt

import streamlit as st
from datetime import datetime, timedelta
from load_data import (MODEL_PATH, PREPROC_PATH, load_btc_data, read_preprocessor,
                       create_model, predict_future_values)


model = None
processor = read_preprocessor(PREPROC_PATH)


def create_app(num_predictions=7, window_size=15):
    st.title("Bitcoin Price Prediction")

    ## To ensure tha date other than current date is not selected
    today = datetime.today().date()
    date = st.date_input("Select the date", max_value=today)
    last_predicted_date = date + timedelta(days=num_predictions-1)
    sel_date = date.strftime('%Y-%m-%d')

    st.write("You selected date: ", sel_date)

    data = load_btc_data(sel_date, window_size=window_size)

    # to ensure we'll load the bitcoin using that
    openprices = data["Open"]
    # data = data.drop(columns=["Open"])

    if st.button("Predict"):
        predictions = predict_future_values(model, processor, data, data.index.tolist(), num_predictions=num_predictions)

        st.subheader("Predicted price(USD) for BitCoin for the next 7 days:")

        max_high = predictions['High'].max()
        min_low = predictions['Low'].min()
        avg_close = predictions['Close'].mean()

        predicted_data = pd.DataFrame(data={"predictions": [max_high, min_low, avg_close]},
                                      index=["Max High", "Min Low", "Avg Close"])

        st.dataframe(predicted_data)

        max_high_index = predictions['Open'].idxmax()
        min_low_index = predictions['Open'].idxmin()

        st.subheader("Recommended Swing Strategy:")

        sell_date = None
        load_date = None

        if max_high_index < min_low_index:
            sell_date = max_high_index
            print(f"min_low_index {min_low_index}, last_predicted_date {last_predicted_date}")
            load_date = min_low_index if min_low_index.date() != last_predicted_date else None
            # He bought? Dump it
        elif max_high_index == today and min_low_index != today:
            sell_date = today
            # bitcoin will peak later this week
        elif min_low_index < max_high_index:
            # hold if the price will be going up
            sell_date = max_high_index if max_high_index.date() != last_predicted_date else None

        sell_data = pd.DataFrame(data={"Strategy": [sell_date, load_date]}, index=["Sell Date", "Load Date"])
        st.dataframe(sell_data)

        # plot the predicted open prices and the real open prices for available data
        next_week = load_btc_data((last_predicted_date+timedelta(1)).strftime('%Y-%m-%d'), window_size=num_predictions)
        df = pd.DataFrame(data={"Predicted": predictions['Open'], "Real": next_week['Open'], 'date': [(date + timedelta(i)) for i in range(num_predictions)]})

        # Melt the dataframe to have a long format for Altair
        df_melted = df.melt('date', var_name='Type', value_name='Price (USD)')

        # Define colors for real and predicted values
        color_scale = alt.Scale(
            domain=['Real', 'Predicted'],
            range=['blue', 'red']
        )

        # Create the chart with a legend
        chart = alt.Chart(df_melted).mark_line().encode(
            x='date:T',
            y=alt.Y('Price (USD):Q', scale=alt.Scale(domain=[df_melted['Price (USD)'].min() - 5, df_melted['Price (USD)'].max() + 5])),
            color=alt.Color('Type:N', scale=color_scale, legend=alt.Legend(title="Legend")),
            tooltip=['date:T', 'Price (USD):Q', 'Type:N'],
        ).interactive()

        # Display the chart in Streamlit
        st.altair_chart(chart, use_container_width=True)
        # st.line_chart(y=next_week['Open'], x=next_week['Dates'], use_container_width=True)


if __name__ == '__main__':
    model_path = os.getenv("MODEL_PATH", MODEL_PATH)
    predictions = os.getenv("PREDICTIONS", 7)
    window_size = os.getenv("WINDOW_SIZE", 15)

    model = create_model(model_path)
    create_app(predictions, window_size)
