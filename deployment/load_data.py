import os

import streamlit
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

@streamlit.cache_resource(hash_funcs={tf.keras.models.Model: id})
def load_models(file_path):
    model_name = file_path.split("/")[-1].split(".")[0]
    model_dir = "/".join(file_path.split("/")[:-1])
    model_names = os.listdir(model_dir)
    models_names = [m for m in model_names if model_name in m]
    model_paths = [os.path.join(model_dir, m) for m in models_names]
    models = []
    for model_path in model_paths:
        model = tf.keras.models.load_model(model_path)
        models.append(model)
    print(f"loaded {models_names}")
    return models


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


def predict_future_values(models, processor, initial_data, dates, num_predictions):
    """
    Generates predictions for future values using a given model and initial data.
    Parameters:
        models (list of objects): The model to use for prediction.
        initial_data (list or numpy.ndarray): The initial data to use for prediction.
        dates (list of datetime): The dates corresponding to the initial data.
        num_predictions (int): The number of predictions to generate.
    Returns:
        pandas.DataFrame: A DataFrame containing dates and predicted values.
    """

    predictions = []
    predictions_stds = []
    predicted_dates = []

    initial_data = processor.transform(initial_data)

    # Reshape initial data if necessary
    initial_data = np.array(initial_data)
    if len(initial_data.shape) == 2:
        initial_data = np.expand_dims(initial_data, axis=0)

    for _ in range(num_predictions):
        # Predict next value based on initial data
        predictions_ = []
        # mixture of couch experts
        for model in models:
            prediction = model.predict(initial_data)
            predictions_.append(prediction)
        predictions_mean = np.mean(predictions_, axis=0)
        predictions_std = np.std(processor.inverse_transform(np.array(predictions_).squeeze()), axis=0)
        print(_, predictions_mean.shape)
        # Append the predicted value to initial data for next prediction
        initial_data = np.concatenate((initial_data[:, 1:], np.expand_dims(predictions_mean, axis=1)), axis=1)

        # Append the prediction to the list of predictions
        predictions.append(np.squeeze(predictions_mean).tolist())
        predictions_stds.append(np.squeeze(predictions_std).tolist())

        # Generate date object for the predicted value
        last_date = dates[-1]
        next_date = last_date + timedelta(days=1)  # Assuming daily frequency, adjust as needed
        predicted_dates.append(next_date)

        # Update dates list for next prediction
        dates.append(next_date)

    predictions = np.array(predictions)
    predictions = processor.inverse_transform(predictions)
    predictions_std = np.array(predictions_stds)
    # predictions_std = processor.inverse_transform(predictions_std)

    # Create DataFrame with dates and predicted values
    predicted_df = pd.DataFrame({
        'High': predictions[:, 0],
        "Low": predictions[:, 1],
        "Close": predictions[:, 2],
        "Open": predictions[:, 3],
        "openstd": predictions_std[:, 3]
    }, index=predicted_dates)

    return predicted_df


if __name__ == '__main__':
    data = load_btc_data('2024-04-30')
    models = load_models(MODEL_PATH)
    processor = read_preprocessor(PREPROC_PATH)
    predictions = predict_future_values(models, processor, data, data.index.tolist(), num_predictions=6)

    print(predictions)
