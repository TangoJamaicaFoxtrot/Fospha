import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Fospha – Simplified Dashboard", layout="wide")

# ------------------
# Load data
# ------------------
@st.cache_data
def load_data():
    df = pd.read_csv("Fospha Data 2.csv", sep=";")
    df["Date"] = pd.to_datetime(df["Date"])
    df["Month"] = df["Date"].dt.strftime("%b")
    return df
    num_cols = ["Cost", "Fospha Attribution Conversions", "Fospha Attribution Revenue", "Fospha Attribution New Conversions"]
    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").round(2)
df = load_data()

# ------------------
# 1️⃣ ROAS by Channel
# ------------------
st.header("ROAS by Channel")

channel_pivot = (
    df.groupby("Channel")
    .agg(
        Cost=("Cost", "sum"),
        Revenue=("Fospha Attribution Revenue", "sum")
    )
    .reset_index()
)

channel_pivot["ROAS"] = channel_pivot["Revenue"] / channel_pivot["Cost"]

st.dataframe(channel_pivot)

fig_channel_roas = px.bar(
    channel_pivot,
    x="Channel",
    y="ROAS",
    title="ROAS by Channel"
)
st.plotly_chart(fig_channel_roas, use_container_width=True)

# ------------------
# 2️⃣ Paid Social ROAS over time (Jun–Oct)
# ------------------
st.header("Paid Social ROAS Over Time")

paid_social = df[df["Channel"] == "Paid Social"]

paid_social_pivot = (
    paid_social
    .groupby("Month")
    .agg(
        Cost=("Cost", "sum"),
        Revenue=("Fospha Attribution Revenue", "sum")
    )
    .reset_index()
)

paid_social_pivot["ROAS"] = (
    paid_social_pivot["Revenue"] / paid_social_pivot["Cost"]
)

# Keep months ordered
paid_social_pivot["Month"] = pd.Categorical(
    paid_social_pivot["Month"],
    categories=["Jun", "Jul", "Aug", "Sep", "Oct"],
    ordered=True
)
paid_social_pivot = paid_social_pivot.sort_values("Month")

st.dataframe(paid_social_pivot)

fig_paid_social_roas = px.line(
    paid_social_pivot,
    x="Month",
    y="ROAS",
    markers=True,
    title="Paid Social ROAS Over Time"
)
st.plotly_chart(fig_paid_social_roas, use_container_width=True)

# ------------------
# 3️⃣ Paid Social – CAC & Cost by Source (October)
# ------------------
st.header("Paid Social – CAC & Cost by Source (October)")

october_paid_social = paid_social[paid_social["Month"] == "Oct"]

source_pivot = (
    october_paid_social
    .groupby("Source")
    .agg(
        Cost=("Cost", "sum"),
        New_Conversions=("Fospha Attribution New Conversions", "sum")
    )
    .reset_index()
)

source_pivot["CAC"] = source_pivot["Cost"] / source_pivot["New_Conversions"]

st.dataframe(source_pivot)

fig_source = px.bar(
    source_pivot,
    x="Source",
    y=["Cost", "CAC"],
    barmode="group",
    title="Paid Social Cost & CAC by Source (October)"
)
st.plotly_chart(fig_source, use_container_width=True)

# ------------------
# 4️⃣ UK – Cost & Revenue over time
# ------------------
st.header("UK Cost & Revenue Over Time")

uk_data = df[df["Market"] == "UK"]

uk_pivot = (
    uk_data
    .groupby("Month")
    .agg(
        Cost=("Cost", "sum"),
        Revenue=("Fospha Attribution Revenue", "sum")
    )
    .reset_index()
)

uk_pivot["Month"] = pd.Categorical(
    uk_pivot["Month"],
    categories=["Jun", "Jul", "Aug", "Sep", "Oct"],
    ordered=True
)
uk_pivot = uk_pivot.sort_values("Month")

st.dataframe(uk_pivot)

fig_uk = px.line(
    uk_pivot,
    x="Month",
    y=["Cost", "Revenue"],
    markers=True,
    title="UK Cost & Revenue Over Time"
)
st.plotly_chart(fig_uk, use_container_width=True)
