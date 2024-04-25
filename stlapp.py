import streamlit as st
from main import predict
from prophet.plot import plot_plotly, plot_components_plotly


st.title('BTC prediction')

m, forecast = predict()
# plot with plotly
fig1 = m.plot(forecast)
fig2 = m.plot_components(forecast)
plot_plotly(m, forecast)
plot_components_plotly(m, forecast)
# st.image(fig1.to_image(format="png"))
# st.image(fig2.to_image(format="png"))
st.plotly_chart(plot_plotly(m, forecast))