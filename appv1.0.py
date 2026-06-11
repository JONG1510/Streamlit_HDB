import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# A simple way to see when the app was last rerun, which can be helpful for debugging and performance monitoring.
print(f"🟢 Rerun at: {datetime.now()}")

DATA_PATH = "data/latest_hdb_resale_prices.parquet"

#
@st.cache_data
def load_data(path):
    print(f"✨ Loading data at: {datetime.now()}")
    df = pd.read_parquet(path)
    df["month"] = pd.to_datetime(df["month"])
    return df

df = load_data(DATA_PATH)

### Phase 2: Setting up the Page and Main Canvas
##This layout section sets the structural boundaries of the browser page before any data visuals are rendered.

st.set_page_config(
    page_title="HDB Resale Dashboard",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="auto",
    )

#===Helps create 2 columns ==== 
# Create two columns: wide left column for title, narrow right column for a metric/logo
#col1, col2 = st.columns([2, 1])

#with col1:
 #   st.title("Singapore HDB Resale Dashboard")
 #   st.caption("Code-along: building a usable dashboard from real resale transactions.")

#with col2:
  # Adds a subtle status badge or metric directly to the right of your title
  #  st.metric(label="Data Currency", value="YTD 2026", delta="Live Updated")

#===End: helps create 2 columns ==== 

st.title("Singapore HDB Resale Dashboard")
st.caption("Building a usable dashboard from real resale transactions.")

#Construction Phase 2: building the filters on the left side

st.sidebar.header("Filters")

unique_towns = sorted(df["town"].dropna().unique())
unique_flat_types = sorted(df["flat_type"].dropna().unique())

selected_towns = st.sidebar.multiselect("Town", unique_towns, default=[])
selected_flat_types = st.sidebar.multiselect("Flat Type", unique_flat_types, default=[])


filtered_df = df.copy()

# 3. DYNAMICALLY FILTER THE STREET LIST
# If towns are selected, narrow down the source data before extracting unique streets
if selected_towns:
    streets_df = filtered_df[filtered_df["town"].isin(selected_towns)]
else:
    streets_df = filtered_df # If no town is selected, show all streets

## == original code for unique town and flat
if selected_towns:
    filtered_df = filtered_df[filtered_df["town"].isin(selected_towns)]

if selected_flat_types:
    filtered_df = filtered_df[filtered_df["flat_type"].isin(selected_flat_types)]

unique_street = sorted(filtered_df["street_name"].dropna().unique())
selected_street = st.sidebar.multiselect("Street Name", unique_street, default=[])

if selected_street:
    filtered_df = filtered_df[filtered_df["street_name"].isin(selected_street)]

min_price = int(filtered_df["resale_price"].min())
max_price = int(filtered_df["resale_price"].max())
price_range = st.sidebar.slider(
    "Resale Price Range",
    min_value=min_price,
    max_value=max_price,
    value=(min_price, max_price),
    step=10000,
)

filtered_df = filtered_df[
df["resale_price"].between(price_range[0], price_range[1])
]
# JONG: Convert the 'month' column to datetime objects
df["month"] = pd.to_datetime(df["month"])

date_min = df["month"].min().date()
date_max = df["month"].max().date()
date_range = st.sidebar.date_input("Month Range", value=(date_min, date_max))

if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = filtered_df[filtered_df["month"].between(
        pd.to_datetime(start_date), pd.to_datetime(end_date)
    )]

# MAIN CONTENT

st.header("Filtered Results")
st.write(f"Matching rows: {len(filtered_df):,} | Columns: {len(filtered_df.columns)}")
st.dataframe(filtered_df.head(20), width="stretch")

#KPI METRICS
st.header("Key Metrics")
# Create four columns for the metrics and unpack them
# We can then use each column to place a metric
col1, col2, col3, col4 = st.columns(4)

# Each col provides a .metric() method that takes a label and a value
col1.metric("Transactions", f"{len(filtered_df):,}")
col2.metric("Average Price", f"${filtered_df['resale_price'].mean():,.0f}")
col3.metric("Median Price", f"${filtered_df['resale_price'].median():,.0f}")
col4.metric("Median Floor Area", f"{filtered_df['floor_area_sqm'].median():.1f} sqm")

import plotly.express as px

st.header("Visual Analysis")

col_left, col_right = st.columns(2)

# Tells Streamlit to put the following content in the left column
with col_left:
    st.subheader("Average Resale Price by Town")
    avg_price_by_town = (
        filtered_df.groupby("town", as_index=False)["resale_price"]
        .mean()
        .sort_values("resale_price", ascending=False)
        .head(10) # Top 10 towns only for clarity
    )
    # Create a Plotly bar chart with towns on x-axis and average resale price on y-axis
    fig_town = px.bar(avg_price_by_town, x="town", y="resale_price")
    # Display the Plotly chart in Streamlit
    st.plotly_chart(fig_town, width="stretch")

# Tells Streamlit to put the following content in the right column
with col_right:
    st.subheader("Transactions by Flat Type")
    tx_by_flat = (
        filtered_df.groupby("flat_type", as_index=False)
        .size()
        .rename(columns={"size": "transactions"})
        .sort_values("transactions", ascending=False)
    )
    # Create a Plotly bar chart with flat types on x-axis and transaction counts on y-axis
    fig_flat = px.bar(tx_by_flat, x="flat_type", y="transactions")
    # Display the Plotly chart in Streamlit
    st.plotly_chart(fig_flat, width="stretch")

    
    # Monthly Trend of Resale Prices

    st.subheader("Monthly Median Resale Price")
trend = (
    filtered_df.groupby("month", as_index=False)["resale_price"]
    .median()
    .sort_values("month")
)
# Create a Plotly line chart with month on x-axis and median resale price on y-axis
fig_trend = px.line(trend, x="month", y="resale_price", markers=True)
# Display the Plotly chart in Streamlit
st.plotly_chart(fig_trend, width="stretch")

