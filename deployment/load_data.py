import yfinance as yf
import tensorflow as tf
import pickle
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

######################
_SYMBOL = 'BTC-USD'
PREPROC_PATH = "models/preprocessor.prec"
MODEL_PATH = "models/gru32b.keras"
#######################


def create_model(file_path):
    model = tf.keras.models.load_model(file_path)
    return model


def read_preprocessor(file_path):
    with open(file_path, 'rb') as file:
        return pickle.load(file)


def load_btc_data(end_date, window_size=15):
    """
    Loads Bitcoin data from Yahoo Finance API based on the provided end date.
    Parameters:
    end_date (str): The end date until which the Bitcoin data is to be fetched in the format '%Y-%m-%d'.
    Returns:
    pandas.DataFrame: A DataFrame containing the Bitcoin data for the specified time period.
    """

    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    start_date = (end_date - timedelta(days=window_size)).strftime('%Y-%m-%d')
    end_date = end_date.strftime('%Y-%m-%d')

    data = yf.download(tickers=_SYMBOL, interval='1d', start=start_date, end=end_date)
    data = data[["High", "Low", "Close", "Open", "Volume"]]  # "Open"

    return data


def predict_future_values(model, processor, initial_data, dates, num_predictions):
    """
    Generates predictions for future values using a given model and initial data.
    Parameters:
        model (object): The model to use for prediction.
        initial_data (list or numpy.ndarray): The initial data to use for prediction.
        dates (list of datetime): The dates corresponding to the initial data.
        num_predictions (int): The number of predictions to generate.
    Returns:
        pandas.DataFrame: A DataFrame containing dates and predicted values.
    """

    predictions = []
    predicted_dates = []

    initial_data = processor.transform(initial_data)

    # Reshape initial data if necessary
    initial_data = np.array(initial_data)
    if len(initial_data.shape) == 2:
        initial_data = np.expand_dims(initial_data, axis=0)

    for _ in range(num_predictions):
        # Predict next value based on initial data
        prediction = model.predict(initial_data)

        # Append the predicted value to initial data for next prediction
        initial_data = np.concatenate((initial_data[:, 1:], np.expand_dims(prediction, axis=1)), axis=1)

        # Append the prediction to the list of predictions
        predictions.append(np.squeeze(prediction).tolist())

        # Generate date object for the predicted value
        last_date = dates[-1]
        next_date = last_date + timedelta(days=1)  # Assuming daily frequency, adjust as needed
        predicted_dates.append(next_date)

        # Update dates list for next prediction
        dates.append(next_date)

    predictions = np.array(predictions)
    predictions = processor.inverse_transform(predictions)

    # Create DataFrame with dates and predicted values
    predicted_df = pd.DataFrame({
        'High': predictions[:, 0],
        "Low": predictions[:, 1],
        "Close": predictions[:, 2],
        "Open": predictions[:, 3],
    }, index=predicted_dates)

    return predicted_df


if __name__ == '__main__':
    data = load_btc_data('2024-04-30')
    model = create_model(MODEL_PATH)
    processor = read_preprocessor(PREPROC_PATH)
    predictions = predict_future_values(model, processor, data, data.index.tolist(), num_predictions=6)

    print(predictions)
