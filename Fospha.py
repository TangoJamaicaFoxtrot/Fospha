import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Marketing Performance", layout="wide")

# ---- Load data ----
@st.cache_data
def load_data():
    df = pd.read_csv(
        "Fospha Data 2.csv",
        sep=";",
        parse_dates=["Date"]
    )
    df["Date_Year_Month"] = df["Date"].dt.to_period("M").astype(str)
    return df

df = load_data()

# ---- Sidebar filters ----
st.sidebar.header("Filters")

market = st.sidebar.selectbox(
    "Market",
    sorted(df["Market"].dropna().unique()),
    index=0
)

channels = st.sidebar.multiselect(
    "Channel",
    sorted(df["Channel"].dropna().unique()),
    default=df["Channel"].dropna().unique()
)

months = st.sidebar.multiselect(
    "Month",
    sorted(df["Date_Year_Month"].unique()),
    default=sorted(df["Date_Year_Month"].unique())
)

# ---- Filtered dataframe ----
filtered = df[
    (df["Market"] == market) &
    (df["Channel"].isin(channels)) &
    (df["Date_Year_Month"].isin(months))
]

# ---- Aggregations ----
summary = filtered.groupby("Date_Year_Month").agg(
    Total_Cost=("Cost", "sum"),
    Total_Revenue=("Fospha Attribution Revenue", "sum"),
    Total_New_Conv=("Fospha Attribution New Conversions", "sum")
).reset_index()

summary["ROAS"] = summary["Total_Revenue"] / summary["Total_Cost"]
summary["CAC"] = summary["Total_Cost"] / summary["Total_New_Conv"]

# ---- KPI Row ----
st.title("Marketing Performance Dashboard")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

kpi1.metric("Total Cost (£)", f"{summary['Total_Cost'].sum():,.0f}")
kpi2.metric("Total Revenue (£)", f"{summary['Total_Revenue'].sum():,.0f}")
kpi3.metric("ROAS", f"{summary['Total_Revenue'].sum() / summary['Total_Cost'].sum():.2f}")
kpi4.metric("CAC (£)", f"{summary['Total_Cost'].sum() / summary['Total_New_Conv'].sum():.2f}")

# ---- Time series chart ----
fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=summary["Date_Year_Month"],
        y=summary["Total_Cost"],
        name="Cost",
        yaxis="y1"
    )
)

fig.add_trace(
    go.Scatter(
        x=summary["Date_Year_Month"],
        y=summary["Total_Revenue"],
        name="Revenue",
        yaxis="y2"
    )
)

fig.update_layout(
    title="Cost vs Revenue Over Time",
    yaxis=dict(title="Cost (£)"),
    yaxis2=dict(title="Revenue (£)", overlaying="y", side="right"),
    template="plotly_white"
)

st.plotly_chart(fig, use_container_width=True)
