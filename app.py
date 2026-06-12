import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# A simple way to see when the app was last rerun, which can be helpful for debugging and performance monitoring.
print(f"🟢 Rerun at: {datetime.now()}")

DATA_PATH = "data/latest_hdb_resale_prices.parquet"

# 1. Load full paraquet data into memory first
@st.cache_data
def load_data(path):
    print(f"✨ Loading data at: {datetime.now()}")
    df = pd.read_parquet(path)
    # 1.2 Keep a standard pandas datetime series for the comparison
    df["month"] = pd.to_datetime(df["month"])
    # 1.3 Truncate memory footprint to only keep rows from Jan 1, 2021 to current 
    # IMPT remember to change #4.1 for calendar boundaries
    start_cutoff = pd.to_datetime("2021-01-01")
    df = df[df["month"] >= start_cutoff]
           
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

st.title("Singapore HDB Resale Dashboard")
st.caption("Building a usable dashboard from real resale transactions.")

#Construction Phase 2: building the filters on the left side

st.sidebar.header("Filters")

unique_towns = sorted(df["town"].dropna().unique())
unique_flat_types = sorted(df["flat_type"].dropna().unique())

selected_towns = st.sidebar.multiselect("Town", unique_towns, default=[])
selected_flat_types = st.sidebar.multiselect("Flat Type", unique_flat_types, default=[])

# 1. ALWAYS clean your date data at the absolute top before copying or filtering
df["month"] = pd.to_datetime(df["month"]).dt.date

filtered_df = df.copy()

# 2. DYNAMICALLY FILTER THE STREET LIST
if selected_towns:
    streets_df = filtered_df[filtered_df["town"].isin(selected_towns)]
else:
    streets_df = filtered_df 

## == Town and Flat Type Filtering
if selected_towns:
    filtered_df = filtered_df[filtered_df["town"].isin(selected_towns)]

if selected_flat_types:
    filtered_df = filtered_df[filtered_df["flat_type"].isin(selected_flat_types)]

unique_street = sorted(filtered_df["street_name"].dropna().unique())
selected_street = st.sidebar.multiselect("Street Name", unique_street, default=[])

if selected_street:
    filtered_df = filtered_df[filtered_df["street_name"].isin(selected_street)]

# 3. Dynamic Price Slider boundaries (calculated safely from current selections)
min_price = int(filtered_df["resale_price"].min())
max_price = int(filtered_df["resale_price"].max())
price_range = st.sidebar.slider(
    "Resale Price Range",
    min_value=min_price,
    max_value=max_price,
    value=(min_price, max_price),
    step=10000,
)

# FIX 1: Filter filtered_df using its own column, not df["resale_price"]
filtered_df = filtered_df[
    filtered_df["resale_price"].between(price_range[0], price_range[1])
]

# 4.1 Date range picking (calculated safely using clean dates)
# 4.2 FORCED DATE BOUNDARIES (Strictly 2017 to 2027)
calendar_min = pd.to_datetime("2021-01-01").date()
calendar_max = pd.to_datetime("2027-12-31").date()

date_min = df["month"].min()
date_max = df["month"].max()
date_range = st.sidebar.date_input(
    "Month Range", 
    value=(date_min, date_max),
    min_value=calendar_min, 
    max_value=calendar_max)

# FIX 2: This will now run perfectly because filtered_df inherits the clean dates from step 1
if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = filtered_df[
        filtered_df["month"].between(start_date, end_date)
    ]


# ==============================================================================
# ENTERPRISE MULTI-TAB ANALYTICS MATRIX INTERFACE
# ==============================================================================
# This replaces or wraps your existing visual analysis container
tab1, tab2 = st.tabs(["📊 Filtered Trend Analysis", "🏢 Floor Level Insights"])

# --- TAB 1: KEEP YOUR EXISTING CHART HERE ---
# MAIN CONTENT

with tab1:
    
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

# --- TAB 2: YOUR NEW ANALYSIS GOES HERE ---
with tab2:
    st.header("Floor Level Analytics")
    
    # Pre-calculate data for Tab 2 to keep it speedy
    # Grouping by storey_range (or your specific floor area column) to get median prices
    floor_data = (
        filtered_df.groupby("storey_range", as_index=False)["resale_price"]
        .median()
        .sort_values("storey_range") # Sorts floor levels structurally
    )

    # 1. DISPLAY THE THREE NEW REQUIREMENTS
    
    # Requirement 2 & 3: Total Transactions, Average, and Median Price Metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Total Transactions (Current View)", 
            value=f"{len(filtered_df):,}"
        )
    with col2:
        st.metric(
            label="Average Resale Price", 
            value=f"${filtered_df['resale_price'].mean():,.0f}"
        )
    with col3:
        st.metric(
            label="Median Resale Price", 
            value=f"${filtered_df['resale_price'].median():,.0f}"
        )
        
    st.markdown("---") # Visual divider line

    # Requirement 1: Price on Y-axis, Floors (Storey Range) on X-axis
    fig_floor = px.bar(
        floor_data,
        x="storey_range",
        y="resale_price",
        title="Median Resale Price by Storey Range",
        labels={"storey_range": "Floor Levels (Storey)", "resale_price": "Median Price ($)"},
        color="resale_price", # Optional color scale mapping to the values
        color_continuous_scale="Blues"
    )
    
    # Center the title natively inside Plotly layout
    fig_floor.update_layout(
        title={
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=20)
        }
    )
    
    # Render the new chart
    st.plotly_chart(fig_floor, use_container_width=True)