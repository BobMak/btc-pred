import os

import pandas as pd
import altair as alt

import streamlit as st
from datetime import datetime, timedelta
from load_data import (MODEL_PATH, PREPROC_PATH, load_btc_data, read_preprocessor,
                       load_models, predict_future_values)


models = None
processor = read_preprocessor(PREPROC_PATH)


def create_app(num_predictions=7, window_size=15):
    st.title("Bitcoin price Prediction")

    ## To ensure tha date other than current date is not selected
    today = datetime.today().date() + timedelta(1)
    date = st.date_input("Select the date", max_value=today + timedelta(1))
    last_predicted_date = date + timedelta(days=num_predictions-1)
    sel_date = date.strftime('%Y-%m-%d')

    st.write("You selected date: ", sel_date)

    data = load_btc_data(sel_date, window_size=window_size)

    # to ensure we'll load the bitcoin using that
    openprices = data["Open"]
    # data = data.drop(columns=["Open"])

    if st.button("Predict"):

        predictions = predict_future_values(model, processor, data, data.index.tolist(), num_predictions=num_predictions)

        st.subheader("Predicted price (USD) for BitCoin for the next 7 days:")

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
        df = pd.DataFrame(data={
            "Predicted": predictions['Open'],
            "Real": next_week['Open'],
            "date": [(date + timedelta(i)) for i in range(num_predictions)]
        })

        opendf = pd.DataFrame(data={
            "openstd": predictions['openstd'],
            "date": [(date + timedelta(i)) for i in range(num_predictions)]
        })
        # Melt the dataframe to have a long format for Altair
        df_melted = df.melt('date', var_name='Type', value_name='price')
        df_melted = pd.merge(df_melted, opendf, on='date')
        # Define colors for real and predicted values
        color_scale = alt.Scale(
            domain=['Real', 'Predicted'],
            range=['blue', 'red']
        )
        min_v = df_melted['price'].min() - df_melted['openstd'].max()
        max_v = df_melted['price'].max() + df_melted['openstd'].max()
        # Create the chart with a legend
        chart = alt.Chart(df_melted).mark_line().encode(
            x='date:T',
            y=alt.Y('price:Q', scale=alt.Scale(domain=[min_v, max_v])),
            color=alt.Color('Type:N', scale=color_scale, legend=alt.Legend(title="Legend")),
            tooltip=['date:T', 'price:Q', 'Type:N'],
        )
        df_area = pd.DataFrame(data={
            "date": df_melted['date'],
            "price": df_melted['price'],
            "price_low": df_melted['price'] - df_melted['openstd'],
            "price_high": df_melted['price'] + df_melted['openstd']
        })
        print(df_area.head())
        bounds = alt.Chart(df_area).mark_area(opacity=0.3, color='red').encode(
            x='date:T',
            y=alt.Y('price_low:Q'),
            y2=alt.Y2('price_high:Q'),
        )
        # Display the chart in Streamlit chart upper
        st.altair_chart(alt.layer(chart, bounds).interactive(), use_container_width=True)


if __name__ == '__main__':
    model_path = os.getenv("MODEL_PATH", MODEL_PATH)
    predictions = os.getenv("PREDICTIONS", 7)
    window_size = os.getenv("WINDOW_SIZE", 15)

    model = load_models(model_path)
    create_app(predictions, window_size)
