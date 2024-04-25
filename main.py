import pandas as pd
from prophet import Prophet
from prophet.plot import plot_plotly, plot_components_plotly


def predict():
    df = pd.read_csv('BTC-USD.csv')
    df.drop(['Open', 'High', 'Low', 'Adj Close', 'Volume'], axis=1, inplace=True)
    df.columns = ['ds', 'y']
    m = Prophet()
    m.fit(df)
    future = m.make_future_dataframe(periods=365)
    future.tail()
    forecast = m.predict(future)
    forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail()
    return m, forecast


if __name__ == '__main__':
    m, forecast = predict()
    fig1 = m.plot(forecast)
    fig2 = m.plot_components(forecast)