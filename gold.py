import streamlit as st
import yfinance as yf # A common tool for gold prices

st.title("Gold Price Trends")

# 1. Fetch the data
data = yf.download("GC=F", period="100d")
data1 = yf.download("SI=F", period="100d")

# 2. Display a summary (Optional)
st.write("Current Gold prices for the last 100 days:")
st.dataframe(data.tail(10)) # Shows the last few rows of the table

# 3. Plot the chart
st.subheader("Price Movement")
st.line_chart(data['Close'])

#4. Silver
st.title("Silver Price Trends")
st.write("Current Silver prices for the last 100 days:")
st.dataframe(data1.tail(10))
st.line_chart(data1['Close'])

