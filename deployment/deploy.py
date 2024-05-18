
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from load_data import MODEL_PATH, FILE_PATH
from load_data import load_btc_data, read_preprocessor, create_model
from load_data import predict_future_values

model = create_model(MODEL_PATH)
processor = read_preprocessor(FILE_PATH)


def create_app(num_predictions=7):
    st.title("Bitcoin Price Prediction")

    ## To ensure tha date other than current date is not selected
    today = datetime.today().date()
    date = st.date_input("Select the date", max_value=today)
    last_predicted_date = today + timedelta(days=num_predictions)
    sel_date = date.strftime('%Y-%m-%d')


    st.write("You selected date: ", sel_date)

    data = load_btc_data(sel_date)

    # to ensure we'll load the bitcoin using that
    openprices = data["Open"]
    data = data.drop(columns=["Open"])

    if st.button("Predict"):
        predictions = predict_future_values(model, processor, data, data.index.tolist(), num_predictions=7)

        st.subheader("Predicted price(USD) for BitCoin for the next 7 days:")

        max_high = predictions['High'].max()
        min_low = predictions['Low'].min()
        avg_close = predictions['Close'].mean()

        predicted_data = pd.DataFrame(data={"predictions": [max_high, min_low, avg_close]},
                                      index=["Max High", "Min Low", "Avg Close"])

        st.dataframe(predicted_data)

        max_high_index = predictions['High'].idxmax()
        min_low_index = predictions['Low'].idxmin()

        st.subheader("Recommended Swing Strategy:")

        sell_date = None
        load_date = None

        if max_high_index < min_low_index:
            sell_date = max_high_index
            load_date = min_low_index if min_low_index != last_predicted_date else None
            # He bought? Dump it
        elif max_high_index == today and min_low_index != today:
            sell_date = today
            # bitcoin will peak later this week
        elif min_low_index < max_high_index:
            # hold if the price will be going up
            sell_date = max_high_index if max_high_index != last_predicted_date else None

        sell_data = pd.DataFrame(data={"Strategy": [sell_date, load_date]}, index=["Sell Date", "Load Date"])
        st.dataframe(sell_data)


if __name__ == '__main__':
    create_app()
