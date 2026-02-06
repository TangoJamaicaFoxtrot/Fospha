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

df = load_data()

num_cols = [
    "Cost",
    "Fospha Attribution Conversions",
    "Fospha Attribution Revenue",
    "Fospha Attribution New Conversions"
]
for col in num_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce").round(2)

# ------------------
# Tabs
# ------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Task 4: ROAS by Channel",
    "Task 5: Paid Social ROAS Over Time",
    "Task 6: Paid Social – October Source Performance",
    "Task 7: UK Cost & Revenue Over Time",
    "Bonus Task: Paid Social Deep Dive"
    
])

# ------------------
# TAB 1: ROAS by Channel
# ------------------
with tab1:
    st.header("ROAS by Channel (Paid Only)")

    paid_channels = [
        "Paid Search - Generic",
        "Paid Shopping",
        "Paid Social",
        "Performance Max"
    ]

    channel_filtered = df[df["Channel"].isin(paid_channels)]

    channel_pivot = (
        channel_filtered
        .groupby("Channel")
        .agg(
            Cost=("Cost", "sum"),
            Revenue=("Fospha Attribution Revenue", "sum"),
            New_Conversions=("Fospha Attribution New Conversions", "sum"),
            Total_Conversions=("Fospha Attribution Conversions", "sum")
        )
        .reset_index()
    )

    # Returning conversions
    channel_pivot["Returning_Conversions"] = (
        channel_pivot["Total_Conversions"] - channel_pivot["New_Conversions"]
    ).clip(lower=0)

    # Core metrics
    channel_pivot["ROAS"] = channel_pivot["Revenue"] / channel_pivot["Cost"]
    channel_pivot["CAC"] = channel_pivot["Cost"] / channel_pivot["New_Conversions"]
    channel_pivot["CPP"] = channel_pivot["Cost"] / channel_pivot["Total_Conversions"]
    channel_pivot["AOV"] = channel_pivot["Revenue"] / channel_pivot["Total_Conversions"]

    # Display table (metrics-heavy)
    st.dataframe(
        channel_pivot[[
            "Channel",
            "Cost",
            "Revenue",
            "ROAS",
            "CAC",
            "CPP",
            "AOV",
            "New_Conversions",
            "Returning_Conversions"
        ]].style.format({
            "Cost": "£{:,.0f}",
            "Revenue": "£{:,.0f}",
            "ROAS": "{:.2f}",
            "CAC": "£{:,.2f}",
            "CPP": "£{:,.2f}",
            "AOV": "£{:,.2f}"
        }),
        use_container_width=True
    )

    # Chart stays simple (ROAS only)
    fig_channel_roas = px.bar(
        channel_pivot,
        x="Channel",
        y="ROAS",
        title="ROAS by Paid Channel"
    )
    st.plotly_chart(fig_channel_roas, use_container_width=True)


# ------------------
# TAB 2: Paid Social ROAS over time
# ------------------
with tab2:
    st.header("Paid Social ROAS Over Time (Jun–Oct)")

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
# TAB 3: Paid Social – CAC & Cost by Source (October)
# ------------------
with tab3:
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
# TAB 4: UK – Cost & Revenue over time
# ------------------
with tab4:
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

with tab5:
    st.header("Paid Social Deep Dive")
