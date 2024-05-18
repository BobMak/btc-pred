import streamlit as st
from datetime import datetime
from load_data import load_btc_data, read_preprocessor, create_model
from load_data import predict_future_values
from load_data import MODEL_PATH, FILE_PATH

model = create_model(MODEL_PATH)
processor = read_preprocessor(FILE_PATH)


def create_app():
    st.title("Bitcoin Price Prediction")

    ## To ensure tha date other than current date is not selected
    today = datetime.today().date()
    date = st.date_input("Select the date", max_value=today)
    sel_date = date.strftime('%Y-%m-%d')

    st.write("You selected date: ", sel_date)

    data = load_btc_data(sel_date)

    if st.button("Predict"):
        predictions = predict_future_values(model, processor, data, data.index.tolist(), num_predictions=7)

        st.write("Predicted price(USD) for BitCoin for the next 7 days:")

        max_high = predictions['High'].max()
        min_low = predictions['Low'].min()
        avg_close = predictions['Close'].mean()

        st.write("Predicted High: ", max_high)
        st.write("Predicted Low: ", min_low)
        st.write("Predicted Average Close: ", avg_close)

        max_high_index = predictions['High'].idxmax().strftime('%Y-%m-%d')
        min_low_index = predictions['Low'].idxmin().strftime('%Y-%m-%d')

        st.subheader("Recommended Swing Strategy:")
        sell_date = None
        load_date = None
        if max_high_index < min_low_index:
            sell_date = max_high_index
            load_date = min_low_index
        elif max_high_index == today:
            sell_date = today
        elif min_low_index < max_high_index and (max_high_index != (today + datetime.diff)):
            sell_date = min_low_index
            load_date = max_high_index#
            pass

        st.write("Predicted Highest High: ", max_high)
        st.write("Predicted Lowest Low: ", min_low)
        st.write("Predicted Highest High day: ", max_high_index)
        st.write("Predicted Lowest Low day: ", min_low_index)


if __name__ == '__main__':
    create_app()
