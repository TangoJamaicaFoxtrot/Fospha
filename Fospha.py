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
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Task 4",
    "Task 5",
    "Task 6",
    "Task 7",
    "Bonus Task 1",
    "Bonus Task 2"
    
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
import plotly.graph_objects as go

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

    # ---- Explicit ordering (Pinterest last) ----
    source_order = [
        s for s in source_pivot["Source"].unique()
        if s.lower() != "pinterest"
    ] + ["Pinterest"]

    source_pivot["Source"] = pd.Categorical(
        source_pivot["Source"],
        categories=source_order,
        ordered=True
    )

    source_pivot = source_pivot.sort_values("Source")

    st.dataframe(source_pivot)

    # ---- Chart ----
    fig = go.Figure()

    # Cost (bars, left axis)
    fig.add_trace(
        go.Bar(
            x=source_pivot["Source"],
            y=source_pivot["Cost"],
            name="Cost",
            yaxis="y1"
        )
    )

    # CAC (line, right axis)
    fig.add_trace(
        go.Scatter(
            x=source_pivot["Source"],
            y=source_pivot["CAC"],
            name="CAC",
            yaxis="y2",
            mode="lines+markers"
        )
    )

    fig.update_layout(
        title="Paid Social Cost & CAC by Source (October)",
        xaxis_title="Source",
        yaxis=dict(title="Cost"),
        yaxis2=dict(
            title="CAC",
            overlaying="y",
            side="right"
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    st.plotly_chart(fig, use_container_width=True)


# ------------------
# TAB 4: UK – Cost & Revenue over time
# ------------------
import plotly.graph_objects as go

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

    fig = go.Figure()

    # Cost (left axis)
    fig.add_trace(
        go.Scatter(
            x=uk_pivot["Month"],
            y=uk_pivot["Cost"],
            name="Cost",
            mode="lines+markers",
            yaxis="y1"
        )
    )

    # Revenue (right axis)
    fig.add_trace(
        go.Scatter(
            x=uk_pivot["Month"],
            y=uk_pivot["Revenue"],
            name="Revenue",
            mode="lines+markers",
            yaxis="y2"
        )
    )

    fig.update_layout(
        title="UK Cost & Revenue Over Time",
        xaxis_title="Month",
        yaxis=dict(title="Cost"),
        yaxis2=dict(
            title="Revenue",
            overlaying="y",
            side="right"
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    st.plotly_chart(fig, use_container_width=True)


with tab5:
    st.header("Paid Channel Deep Dive")

    # --------------------
    # Month filter (multi-select)
    # --------------------
    all_months = ["Jun", "Jul", "Aug", "Sep", "Oct"]
    selected_months = st.multiselect(
        "Select Month(s)",
        options=all_months,
        default=all_months
    )

    # --------------------
    # Filtered data
    # --------------------
    paid_channels = [
        "Paid Search - Generic",
        "Paid Shopping",
        "Paid Social",
        "Performance Max"
    ]
    df_paid = df[
        (df["Channel"].isin(paid_channels)) &
        (df["Month"].isin(selected_months))
    ]

    # --------------------
    # 1️⃣ KPI Strip
    # --------------------
    total_cost = df_paid["Cost"].sum()
    total_revenue = df_paid["Fospha Attribution Revenue"].sum()
    total_new = df_paid["Fospha Attribution New Conversions"].sum()
    total_total = df_paid["Fospha Attribution Conversions"].sum()
    total_returning = total_total - total_new
    total_returning = max(total_returning, 0)
    roas = total_revenue / total_cost if total_cost > 0 else None
    cac = total_cost / total_new if total_new > 0 else None
    cpp = total_cost / total_total if total_total > 0 else None
    aov = total_revenue / total_total if total_total > 0 else None
    pct_new = total_new / total_total if total_total > 0 else None

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("Total Cost (£)", f"{total_cost:,.0f}")
    k2.metric("Total Revenue (£)", f"{total_revenue:,.0f}")
    k3.metric("ROAS", f"{roas:.2f}")
    k4.metric("CAC (£)", f"{cac:,.2f}")
    k5.metric("CPP (£)", f"{cpp:,.2f}")
    k6.metric("% New Conversions", f"{pct_new:.0%}")

    # --------------------
    # 2️⃣ Channel Efficiency Matrix (ROAS vs CAC)
    # --------------------
    channel_pivot = (
        df_paid.groupby("Channel")
        .agg(
            Cost=("Cost", "sum"),
            Revenue=("Fospha Attribution Revenue", "sum"),
            New_Conversions=("Fospha Attribution New Conversions", "sum"),
            Total_Conversions=("Fospha Attribution Conversions", "sum")
        )
        .reset_index()
    )

    channel_pivot["CAC"] = channel_pivot["Cost"] / channel_pivot["New_Conversions"]
    channel_pivot["ROAS"] = channel_pivot["Revenue"] / channel_pivot["Cost"]

    fig_matrix = go.Figure()
    fig_matrix.add_trace(
        go.Scatter(
            x=channel_pivot["CAC"],
            y=channel_pivot["ROAS"],
            mode="markers+text",
            text=channel_pivot["Channel"],
            textposition="top center",
            marker=dict(size=channel_pivot["Cost"] / 1000, sizemode="area", sizeref=2),
            name="Channel"
        )
    )

    fig_matrix.update_layout(
        title="Paid Channel Efficiency (ROAS vs CAC, bubble size = spend)",
        xaxis_title="CAC (£)",
        yaxis_title="ROAS",
        template="plotly_white"
    )

    st.plotly_chart(fig_matrix, use_container_width=True)

    # --------------------
    # 3️⃣ New vs Returning Conversions by Channel (stacked bar)
    # --------------------
    channel_pivot["Returning_Conversions"] = (
        channel_pivot["Total_Conversions"] - channel_pivot["New_Conversions"]
    ).clip(lower=0)

    fig_stack = go.Figure()
    fig_stack.add_trace(
        go.Bar(
            x=channel_pivot["Channel"],
            y=channel_pivot["New_Conversions"],
            name="New Conversions"
        )
    )
    fig_stack.add_trace(
        go.Bar(
            x=channel_pivot["Channel"],
            y=channel_pivot["Returning_Conversions"],
            name="Returning Conversions"
        )
    )
    fig_stack.update_layout(
        title="New vs Returning Conversions by Paid Channel",
        barmode="stack",
        xaxis_title="Channel",
        yaxis_title="Conversions",
        template="plotly_white"
    )
    st.plotly_chart(fig_stack, use_container_width=True)

    # --------------------
    # 4️⃣ CAC vs CPP Table
    # --------------------
    channel_pivot["CPP"] = channel_pivot["Cost"] / channel_pivot["Total_Conversions"]
    channel_pivot["AOV"] = channel_pivot["Revenue"] / channel_pivot["Total_Conversions"]

    st.subheader("Paid Channel Metrics Table")
    st.dataframe(
        channel_pivot[[
            "Channel", "Cost", "Revenue", "ROAS", "CAC", "CPP", "AOV",
            "New_Conversions", "Returning_Conversions"
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

    # --------------------
    # 5️⃣ Paid Cost vs Revenue Over Time (dual-axis)
    # --------------------
    time_pivot = (
        df_paid.groupby("Month")
        .agg(Cost=("Cost", "sum"), Revenue=("Fospha Attribution Revenue", "sum"))
        .reset_index()
    )

    fig_time = go.Figure()
    fig_time.add_trace(
        go.Scatter(x=time_pivot["Month"], y=time_pivot["Cost"], mode="lines+markers", name="Cost", yaxis="y1")
    )
    fig_time.add_trace(
        go.Scatter(x=time_pivot["Month"], y=time_pivot["Revenue"], mode="lines+markers", name="Revenue", yaxis="y2")
    )
    fig_time.update_layout(
        title="Paid Channel Cost vs Revenue Over Time",
        xaxis_title="Month",
        yaxis=dict(title="Cost (£)"),
        yaxis2=dict(title="Revenue (£)", overlaying="y", side="right"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template="plotly_white"
    )
    st.plotly_chart(fig_time, use_container_width=True)

