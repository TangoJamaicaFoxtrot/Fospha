import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Marketing Performance Dashboard", layout="wide")

# ---- Load Data ----
@st.cache_data
def load_data():
    df = pd.read_csv("Fospha Data 2.csv", sep=";")
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Date_Year_Month"] = df["Date"].dt.to_period("M").astype(str)
    
    # Define numeric columns that might exist
    num_cols = [
        "Cost", 
        "Fospha Attribution Conversions", 
        "Fospha Attribution Revenue", 
        "Fospha Attribution New Conversions",
        "Returning Conversions",       # optional
        "Average Order Value"          # optional
    ]
    
    for col in num_cols:
        if col not in df.columns:
            df[col] = pd.NA  # fill missing optional columns
        df[col] = pd.to_numeric(df[col], errors="coerce").round(2)
    
    return df

# ---- Tabs ----
tab1, tab2, tab3, tab4 = st.tabs([
    "Overview",
    "Channel Performance",
    "Paid Social Deep Dive",
    "Trends & Efficiency"
])

# ---- Filters for tabs ----
markets = sorted(df["Market"].dropna().unique())
channels = sorted(df["Channel"].dropna().unique())

# --------------------------
# TAB 1: Overview
# --------------------------
with tab1:
    st.subheader("Marketing Overview")
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        selected_market = st.selectbox("Market", markets)
    with col2:
        selected_channel_type = st.selectbox("Channel Type", ["All", "Paid", "Owned"])

    # Filter dataframe
    filtered = df[df["Market"] == selected_market].copy()
    if selected_channel_type == "Paid":
        filtered = filtered[filtered["Channel"].str.contains("Paid", na=False)]
    elif selected_channel_type == "Owned":
        filtered = filtered[filtered["Channel"].str.contains("Owned", na=False)]

    # Aggregations
    summary = filtered.groupby("Date_Year_Month").agg(
        Total_Cost=("Cost", "sum"),
        Total_Revenue=("Fospha Attribution Revenue", "sum"),
        New_Conversions=("Fospha Attribution New Conversions", "sum"),
        Returning_Conversions=("Returning Conversions", "sum"),
        AOV=("Average Order Value", "mean")
    ).reset_index()

    summary["ROAS"] = summary.apply(lambda x: x["Total_Revenue"]/x["Total_Cost"] if x["Total_Cost"]>0 else None, axis=1)
    summary["CAC"] = summary.apply(lambda x: x["Total_Cost"]/x["New_Conversions"] if x["New_Conversions"]>0 else None, axis=1)
    summary["CPP"] = summary.apply(lambda x: x["Total_Cost"]/(x["New_Conversions"]+x["Returning_Conversions"]) 
                                   if (x["New_Conversions"]+x["Returning_Conversions"])>0 else None, axis=1)

    # KPI Row
    kpi_cols = st.columns(8)
    kpi_cols[0].metric("Total Cost (£)", f"{summary['Total_Cost'].sum():,.0f}")
    kpi_cols[1].metric("Total Revenue (£)", f"{summary['Total_Revenue'].sum():,.0f}")
    kpi_cols[2].metric("ROAS", f"{summary['ROAS'].mean():.2f}" if selected_channel_type=="Paid" else "N/A")
    kpi_cols[3].metric("CAC (£)", f"{summary['CAC'].mean():.2f}" if selected_channel_type=="Paid" else "N/A")
    kpi_cols[4].metric("CPP (£)", f"{summary['CPP'].mean():.2f}" if selected_channel_type=="Paid" else "N/A")
    kpi_cols[5].metric("AOV (£)", f"{summary['AOV'].mean():.2f}" if "AOV" in summary else "N/A")
    kpi_cols[6].metric("New Conversions", f"{summary['New_Conversions'].sum():,.0f}")
    kpi_cols[7].metric("Returning Conversions", f"{summary['Returning_Conversions'].sum():,.0f}")

# --------------------------
# TAB 2: Channel Performance
# --------------------------
with tab2:
    st.subheader("Channel Performance")
    
    col1, col2 = st.columns(2)
    with col1:
        selected_market = st.selectbox("Market", markets, key="cp_market")
    with col2:
        selected_period = st.selectbox("Month", sorted(df["Date_Year_Month"].unique()), key="cp_month")

    filtered = df[(df["Market"]==selected_market) & (df["Date_Year_Month"]==selected_period)]
    
    channel_perf = filtered.groupby("Channel").agg(
        Cost=("Cost", "sum"),
        Revenue=("Fospha Attribution Revenue", "sum"),
        New_Conversions=("Fospha Attribution New Conversions", "sum"),
        Returning_Conversions=("Returning Conversions", "sum"),
        AOV=("Average Order Value", "mean")
    ).reset_index()

    channel_perf["ROAS"] = channel_perf.apply(lambda x: x["Revenue"]/x["Cost"] if x["Cost"]>0 else None, axis=1)
    channel_perf["CAC"] = channel_perf.apply(lambda x: x["Cost"]/x["New_Conversions"] if x["New_Conversions"]>0 else None, axis=1)
    channel_perf["CPP"] = channel_perf.apply(lambda x: x["Cost"]/(x["New_Conversions"]+x["Returning_Conversions"]) 
                                             if (x["New_Conversions"]+x["Returning_Conversions"])>0 else None, axis=1)

    # Mark Owned channel metrics that don't apply
    for metric in ["ROAS","CAC","CPP"]:
        channel_perf.loc[~channel_perf["Channel"].str.contains("Paid", na=False), metric] = None

    st.dataframe(
        channel_perf.sort_values("Revenue", ascending=False).style.format({
            "Cost":"£{:,.0f}",
            "Revenue":"£{:,.0f}",
            "ROAS":"{:.2f}",
            "CAC":"£{:,.2f}",
            "CPP":"£{:,.2f}",
            "AOV":"£{:,.2f}"
        }),
        use_container_width=True
    )

# --------------------------
# TAB 3: Paid Social Deep Dive
# --------------------------
with tab3:
    st.subheader("Paid Social Deep Dive")
    
    paid_social = df[df["Channel"]=="Paid Social"].copy()

    col1, col2 = st.columns(2)
    with col1:
        selected_month = st.selectbox("Month", sorted(paid_social["Date_Year_Month"].unique()), key="ps_month")
    with col2:
        selected_market = st.selectbox("Market", sorted(paid_social["Market"].unique()), key="ps_market")

    filtered = paid_social[
        (paid_social["Date_Year_Month"]==selected_month) &
        (paid_social["Market"]==selected_market)
    ]

    source_perf = filtered.groupby("Source").agg(
        Cost=("Cost","sum"),
        Revenue=("Fospha Attribution Revenue","sum"),
        Conversions=("Fospha Attribution Conversions","sum"),
        New_Conversions=("Fospha Attribution New Conversions","sum")
    ).reset_index()
    
    source_perf["ROAS"] = source_perf.apply(lambda x: x["Revenue"]/x["Cost"] if x["Cost"]>0 else None, axis=1)
    source_perf["CAC"] = source_perf.apply(lambda x: x["Cost"]/x["New_Conversions"] if x["New_Conversions"]>0 else None, axis=1)
    source_perf = source_perf[source_perf["Cost"]>0]

    # Charts
    c1, c2 = st.columns(2)
    with c1:
        fig_cac = px.bar(source_perf.sort_values("CAC"), x="Source", y="CAC", title="CAC by Paid Social Source", template="plotly_white")
        st.plotly_chart(fig_cac, use_container_width=True)
    with c2:
        fig_roas = px.bar(source_perf.sort_values("ROAS", ascending=False), x="Source", y="ROAS", title="ROAS by Paid Social Source", template="plotly_white")
        st.plotly_chart(fig_roas, use_container_width=True)

    fig_scatter = px.scatter(source_perf, x="Cost", y="New_Conversions", size="Revenue", color="Source",
                             title="Cost vs New Conversions (Bubble = Revenue)", template="plotly_white")
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.subheader("Source Performance Summary")
    st.dataframe(source_perf.sort_values("ROAS", ascending=False).style.format({
        "Cost":"£{:,.0f}",
        "Revenue":"£{:,.0f}",
        "ROAS":"{:.2f}",
        "CAC":"£{:,.2f}"
    }), use_container_width=True)

# --------------------------
# TAB 4: Trends & Efficiency
# --------------------------
with tab4:
    st.subheader("Trends & Efficiency Over Time")

    col1, col2 = st.columns(2)
    with col1:
        selected_market = st.selectbox("Market", markets, key="te_market")
    with col2:
        selected_channel = st.selectbox("Channel", ["All"] + channels, key="te_channel")

    filtered = df[df["Market"]==selected_market]
    if selected_channel != "All":
        filtered = filtered[filtered["Channel"]==selected_channel]

    summary = filtered.groupby("Date_Year_Month").agg(
        Total_Cost=("Cost","sum"),
        Total_Revenue=("Fospha Attribution Revenue","sum"),
        New_Conversions=("Fospha Attribution New Conversions","sum")
    ).reset_index()
    summary["ROAS"] = summary.apply(lambda x: x["Total_Revenue"]/x["Total_Cost"] if x["Total_Cost"]>0 else None, axis=1)
    summary["CAC"] = summary.apply(lambda x: x["Total_Cost"]/x["New_Conversions"] if x["New_Conversions"]>0 else None, axis=1)

    summary["Date_Year_Month"] = pd.to_datetime(summary["Date_Year_Month"])
    summary = summary.sort_values("Date_Year_Month")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=summary["Date_Year_Month"], y=summary["Total_Cost"], name="Cost", mode="lines+markers", yaxis="y1"))
    fig.add_trace(go.Scatter(x=summary["Date_Year_Month"], y=summary["Total_Revenue"], name="Revenue", mode="lines+markers", yaxis="y2"))

    fig.update_layout(
        title=f"Cost vs Revenue Over Time – {selected_market}",
        xaxis_title="Month",
        yaxis=dict(title="Cost (£)"),
        yaxis2=dict(title="Revenue (£)", overlaying="y", side="right"),
        template="plotly_white",
        legend=dict(orientation="h", y=-0.25)
    )
    st.plotly_chart(fig, use_container_width=True)

    # Scatter: Cost vs New Conversions
    fig_scatter = px.scatter(summary, x="Total_Cost", y="New_Conversions", size="Total_Revenue",
                             title="Cost vs New Conversions (Bubble = Revenue)", template="plotly_white")
    st.plotly_chart(fig_scatter, use_container_width=True)
