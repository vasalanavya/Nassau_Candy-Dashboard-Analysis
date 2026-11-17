import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Nassau Candy Dashboard",
    layout="wide"
)

# Automatically load CSV
@st.cache_data
def load_data():
    df = pd.read_csv("Nassau Candy Distributor.csv")
    df.columns = df.columns.str.strip()
    return df

df = load_data()

st.title("Nassau Candy Distributor")
st.subheader("Product Line Profitability & Margin Performance Analysis")

st.success("Dataset loaded successfully!")

st.write("Total Records:", len(df))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime
# ==================================================
# 1. PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Nassau Candy Profitability Dashboard",
    page_icon="🍬",
    layout="wide"
)

st.title("🍬 Nassau Candy Distributor")
st.subheader(
    "Product Line Profitability & Margin Performance Analysis"
)

st.markdown("---")


# ==================================================
# 2. AUTOMATIC CSV LOADING
# ==================================================

@st.cache_data
def load_data():

    df = pd.read_csv("Nassau Candy Distributor.csv")

    df.columns = df.columns.str.strip()

    required_columns = [
        "Order Date",
        "Division",
        "Product Name",
        "Sales",
        "Cost",
        "Gross Profit",
        "Units"
    ]

    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing columns in CSV: {missing}"
        )

    df["Order Date"] = pd.to_datetime(
        df["Order Date"], errors="coerce"
    )

    numeric_columns = [
        "Sales", "Cost", "Gross Profit", "Units"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(
            df[col], errors="coerce"
        )

    df = df.dropna(
        subset=[
            "Order Date",
            "Division",
            "Product Name",
            "Sales",
            "Cost",
            "Gross Profit",
            "Units"
        ]
    ).copy()

    df = df[df["Sales"] > 0].copy()

    df["Gross Margin"] = (
        df["Gross Profit"] / df["Sales"]
    ) * 100

    df["Profit Per Unit"] = (
        df["Gross Profit"] /
        df["Units"].replace(0, pd.NA)
    )

    return df


try:
    df = load_data()

except Exception as e:
    st.error(f"Dataset loading error: {e}")
    st.stop()


st.success("Nassau Candy dataset loaded successfully!")

# ==================================================
# 3. SIDEBAR - USER CAPABILITIES
# ==================================================

st.sidebar.title("Dashboard Controls")

# Date Range Selector

min_date = df["Order Date"].min().date()
max_date = df["Order Date"].max().date()
min_date=datetime.date(2025,1,1)
max_date=datetime.date(2040,12,31)
date_range = st.sidebar.date_input(
    "Date Range Selector",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Division Filter

division_list = sorted(
    df["Division"].dropna().unique().tolist()
)

selected_division = st.sidebar.selectbox(
    "Division Filter",
    ["All Divisions"] + division_list
)

# Margin Threshold Slider

margin_threshold = st.sidebar.slider(
    "Margin Threshold (%)",
    min_value=0,
    max_value=100,
    value=20,
    step=1
)

# Product Search

product_search = st.sidebar.text_input(
    "Product Search",
    placeholder="Enter product name..."
)

st.sidebar.markdown("---")
st.sidebar.caption(
    "Nassau Candy Product Profitability Analysis"
)

# ==================================================
# 4. APPLY USER FILTERS
# ==================================================

filtered_df = df.copy()

if len(date_range) == 2:

    start_date, end_date = date_range

    filtered_df = filtered_df[
        (filtered_df["Order Date"].dt.date >= start_date) &
        (filtered_df["Order Date"].dt.date <= end_date)
    ]

if selected_division != "All Divisions":

    filtered_df = filtered_df[
        filtered_df["Division"] == selected_division
    ]

if product_search.strip():

    filtered_df = filtered_df[
        filtered_df["Product Name"].str.contains(
            product_search,
            case=False,
            na=False
        )
    ]

if filtered_df.empty:

    st.warning(
        "No records found. Please change your filters."
    )
    st.stop()


# ==================================================
# 5. PRODUCT LEVEL SUMMARY
# ==================================================

product_summary = (
    filtered_df.groupby("Product Name", as_index=False)
    .agg({
        "Sales": "sum",
        "Cost": "sum",
        "Gross Profit": "sum",
        "Units": "sum"
    })
)

product_summary["Gross Margin"] = (
    product_summary["Gross Profit"] /
    product_summary["Sales"].replace(0, pd.NA)
) * 100

product_summary["Profit Per Unit"] = (
    product_summary["Gross Profit"] /
    product_summary["Units"].replace(0, pd.NA)
)

# ==========================================
# KPI CALCULATIONS
# ==========================================

# Revenue Contribution
product_summary["Revenue Contribution"] = (
    product_summary["Sales"] /
    filtered_df["Sales"].sum()
) * 100

# Profit Contribution
total_gross_profit = filtered_df["Gross Profit"].sum()

if total_gross_profit != 0:
    product_summary["Profit Contribution"] = (
        product_summary["Gross Profit"] /
        total_gross_profit
    ) * 100
else:
    product_summary["Profit Contribution"] = 0

# Monthly Margin Volatility
monthly_data = (
    filtered_df.groupby(
        filtered_df["Order Date"].dt.to_period("M")
    )
    .agg({
        "Sales": "sum",
        "Gross Profit": "sum"
    })
    .reset_index()
)

monthly_data["Order Date"] = (
    monthly_data["Order Date"].astype(str)
)

monthly_data["Gross Margin"] = (
    monthly_data["Gross Profit"] /
    monthly_data["Sales"].replace(0, pd.NA)
) * 100

margin_volatility = monthly_data[
    "Gross Margin"
].std()


# ==================================================
# 6. DIVISION LEVEL SUMMARY
# ==================================================

division_summary = (
    filtered_df.groupby("Division", as_index=False)
    .agg({
        "Sales": "sum",
        "Cost": "sum",
        "Gross Profit": "sum"
    })
)

division_summary["Gross Margin"] = (
    division_summary["Gross Profit"] /
    division_summary["Sales"].replace(0, pd.NA)
) * 100


# ==================================================
# MODULE 1: PRODUCT PROFITABILITY OVERVIEW
# ==================================================

st.header("1. Product Profitability Overview")

total_sales = filtered_df["Sales"].sum()
total_cost = filtered_df["Cost"].sum()
total_profit = filtered_df["Gross Profit"].sum()
total_units = filtered_df["Units"].sum()

gross_margin = (
    total_profit / total_sales * 100
    if total_sales else 0
)

profit_per_unit = (
    total_profit / total_units
    if total_units else 0
)

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Sales", f"{total_sales:,.2f}")
c2.metric("Total Cost", f"{total_cost:,.2f}")
c3.metric("Gross Profit", f"{total_profit:,.2f}")
c4.metric("Gross Margin", f"{gross_margin:.2f}%")

c5, c6 = st.columns(2)

c5.metric("Total Units", f"{total_units:,.0f}")
c6.metric("Profit Per Unit", f"{profit_per_unit:,.2f}")

st.markdown("---")

# ==========================================
# MODULE: KEY PERFORMANCE INDICATORS
# ==========================================

st.markdown("---")

st.header("Key Performance Indicators (KPIs)")

st.write(
    "This section measures product profitability, "
    "revenue contribution, profit contribution "
    "and monthly margin stability."
)

# Calculate overall KPIs

kpi_gross_margin = (
    filtered_df["Gross Profit"].sum() /
    filtered_df["Sales"].sum() * 100
    if filtered_df["Sales"].sum() != 0 else 0
)

kpi_profit_per_unit = (
    filtered_df["Gross Profit"].sum() /
    filtered_df["Units"].sum()
    if filtered_df["Units"].sum() != 0 else 0
)

# Five KPI Cards

k1, k2, k3, k4, k5 = st.columns(5)

k1.metric(
    "Gross Margin",
    f"{kpi_gross_margin:.2f}%"
)

k2.metric(
    "Profit Per Unit",
    f"{kpi_profit_per_unit:,.2f}"
)

k3.metric(
    "Revenue Contribution",
    "100.00%"
)

k4.metric(
    "Profit Contribution",
    "100.00%" if total_gross_profit != 0 else "N/A"
)

k5.metric(
    "Margin Volatility",
    f"{margin_volatility:.2f}%" 
    if pd.notna(margin_volatility) else "N/A"
)

st.caption(
    "Revenue and profit contribution cards show "
    "the overall filtered dataset. Product-level "
    "contributions are displayed below."
)

# Product KPI Table

st.subheader("Product-Level KPI Analysis")

kpi_table = product_summary[
    [
        "Product Name",
        "Gross Margin",
        "Profit Per Unit",
        "Revenue Contribution",
        "Profit Contribution"
    ]
].copy()

st.dataframe(
    kpi_table,
    use_container_width=True,
    hide_index=True
)

# Revenue Contribution Chart

st.subheader("Product Revenue Contribution")

fig_kpi1 = px.bar(
    product_summary.nlargest(
        10, "Revenue Contribution"
    ),
    x="Product Name",
    y="Revenue Contribution",
    title="Top 10 Products by Revenue Contribution",
    color="Revenue Contribution"
)

st.plotly_chart(
    fig_kpi1,
    use_container_width=True
)

# Profit Contribution Chart

st.subheader("Product Profit Contribution")

fig_kpi2 = px.bar(
    product_summary.nlargest(
        10, "Profit Contribution"
    ),
    x="Product Name",
    y="Profit Contribution",
    title="Top 10 Products by Profit Contribution",
    color="Profit Contribution"
)

st.plotly_chart(
    fig_kpi2,
    use_container_width=True
)

# Margin Volatility Chart

st.subheader("Monthly Gross Margin Volatility")

fig_kpi3 = px.line(
    monthly_data,
    x="Order Date",
    y="Gross Margin",
    markers=True,
    title="Monthly Gross Margin Trend"
)

st.plotly_chart(
    fig_kpi3,
    use_container_width=True
)


# Product Level Margin Leaderboard

st.subheader("Product-Level Margin Leaderboard")

leaderboard = product_summary.sort_values(
    "Gross Margin", ascending=False
)

st.dataframe(
    leaderboard,
    use_container_width=True,
    hide_index=True
)

# Profit Contribution Chart

st.subheader("Product Profit Contribution")

profit_chart = product_summary.sort_values(
    "Gross Profit", ascending=False
).head(10)

fig1 = px.bar(
    profit_chart,
    x="Product Name",
    y="Gross Profit",
    title="Top 10 Products by Gross Profit",
    color="Gross Profit"
)

st.plotly_chart(fig1, use_container_width=True)


# ==================================================
# MODULE 2: DIVISION PERFORMANCE
# ==================================================

st.markdown("---")
st.header("2. Division Performance Dashboard")

# Revenue vs Profit

st.subheader("Revenue vs Profit Comparison")

fig2 = px.bar(
    division_summary,
    x="Division",
    y=["Sales", "Gross Profit"],
    barmode="group",
    title="Division-wise Revenue and Gross Profit"
)

st.plotly_chart(fig2, use_container_width=True)

# Margin Distribution

st.subheader("Margin Distribution by Division")

fig3 = px.bar(
    division_summary,
    x="Division",
    y="Gross Margin",
    color="Division",
    title="Gross Margin Percentage by Division"
)

st.plotly_chart(fig3, use_container_width=True)


# ==================================================
# MODULE 3: COST VS MARGIN DIAGNOSTICS
# ==================================================

st.markdown("---")
st.header("3. Cost vs Margin Diagnostics")

# Cost Sales Scatter Plot

st.subheader("Cost-Sales Scatter Plot")

fig4 = px.scatter(
    product_summary,
    x="Cost",
    y="Sales",
    size="Gross Profit",
    color="Gross Margin",
    hover_name="Product Name",
    title="Product Cost vs Sales Analysis"
)

st.plotly_chart(fig4, use_container_width=True)

# Margin Risk Flags

st.subheader("Margin Risk Flags")

risk_df = product_summary.copy()

def classify_product(row):

    if row["Gross Profit"] < 0:
        return "Loss Making"

    elif row["Gross Margin"] < margin_threshold:
        return "Margin Poor"

    elif (
        row["Sales"] > 0
        and row["Cost"] / row["Sales"] > 0.80
    ):
        return "Cost Heavy"

    elif row["Gross Margin"] < 30:
        return "Pricing Review"

    else:
        return "Healthy"


risk_df["Product_Flag"] = risk_df.apply(
    classify_product,
    axis=1
)

st.dataframe(
    risk_df[
        [
            "Product Name",
            "Sales",
            "Cost",
            "Gross Profit",
            "Gross Margin",
            "Product_Flag"
        ]
    ],
    use_container_width=True,
    hide_index=True
)

# Risk Flag Chart

risk_counts = (
    risk_df["Product_Flag"]
    .value_counts()
    .reset_index()
)

risk_counts.columns = [
    "Product Flag", "Product Count"
]

fig5 = px.bar(
    risk_counts,
    x="Product Flag",
    y="Product Count",
    color="Product Flag",
    title="Product Margin Risk Classification"
)

st.plotly_chart(fig5, use_container_width=True)


# ==================================================
# MODULE 4: PROFIT CONCENTRATION ANALYSIS
# ==================================================

st.markdown("---")
st.header("4. Profit Concentration Analysis")

# Pareto Analysis

st.subheader("Gross Profit Pareto Chart")

pareto_df = product_summary.sort_values(
    "Gross Profit", ascending=False
).copy()

pareto_df["Cumulative Profit"] = (
    pareto_df["Gross Profit"].cumsum()
)

if pareto_df["Gross Profit"].sum() != 0:

    pareto_df["Cumulative Percentage"] = (
        pareto_df["Cumulative Profit"] /
        pareto_df["Gross Profit"].sum()
    ) * 100

else:

    pareto_df["Cumulative Percentage"] = 0

fig6 = go.Figure()

fig6.add_trace(
    go.Bar(
        x=pareto_df["Product Name"],
        y=pareto_df["Gross Profit"],
        name="Gross Profit"
    )
)

fig6.add_trace(
    go.Scatter(
        x=pareto_df["Product Name"],
        y=pareto_df["Cumulative Percentage"],
        name="Cumulative %",
        yaxis="y2",
        mode="lines+markers"
    )
)

fig6.update_layout(
    title="Product-wise Gross Profit Pareto Analysis",
    xaxis_title="Product Name",
    yaxis_title="Gross Profit",
    yaxis2=dict(
        title="Cumulative Percentage",
        overlaying="y",
        side="right",
        range=[0, 110]
    )
)

st.plotly_chart(fig6, use_container_width=True)

# 80% Profit Contribution

st.subheader("Products Contributing to 80% of Gross Profit")

pareto_80 = pareto_df[
    pareto_df["Cumulative Percentage"] <= 80
]

if pareto_80.empty and not pareto_df.empty:
    pareto_80 = pareto_df.head(1)

st.dataframe(
    pareto_80[
        [
            "Product Name",
            "Gross Profit",
            "Cumulative Percentage"
        ]
    ],
    use_container_width=True,
    hide_index=True
)

# Profit Dependency Indicator

st.subheader("Profit Dependency Indicators")

total_product_profit = product_summary[
    "Gross Profit"
].sum()

top_5_profit = product_summary.nlargest(
    5, "Gross Profit"
)["Gross Profit"].sum()

dependency = (
    top_5_profit / total_product_profit * 100
    if total_product_profit > 0 else 0
)

d1, d2 = st.columns(2)

d1.metric(
    "Top 5 Products Profit Contribution",
    f"{dependency:.2f}%"
)

d2.metric(
    "Number of Products",
    len(product_summary)
)

st.info(
    "A higher contribution from a small group of products "
    "indicates greater dependence on those products for "
    "gross profit generation."
)


# ==================================================
# 7. PRODUCT SEARCH RESULTS
# ==================================================

st.markdown("---")
st.header("5. Product Search Results")

if product_search.strip():

    st.write(
        f"Search results for: **{product_search}**"
    )

    st.dataframe(
        product_summary,
        use_container_width=True,
        hide_index=True
    )

else:

    st.write(
        "Enter a product name in the sidebar search box "
        "to view specific product information."
    )

# ==================================================
# MODULE 5: FACTORY LOCATION ANALYSIS
# ==================================================

st.markdown("---")

st.header("5. Factory Location Analysis")

st.write(
    "This module displays the geographical locations "
    "of five factories associated with the Nassau Candy "
    "dataset using latitude and longitude coordinates."
)

# Factory coordinates

factory_data = pd.DataFrame({
    "Factory": [
        "Lot's O' Nuts",
        "Wicked Choccy's",
        "Sugar Shack",
        "Secret Factory",
        "The Other Factory"
    ],

    "Latitude": [
        32.881893,
        32.076176,
        48.119140,
        41.446333,
        35.117500
    ],

    "Longitude": [
        -111.768036,
        -81.088371,
        -96.181150,
        -90.565487,
        -89.971107
    ]
})

# Display factory count

f1, f2 = st.columns(2)

f1.metric(
    "Total Factories",
    len(factory_data)
)

f2.metric(
    "Coordinate Records",
    len(factory_data)
)

# Display interactive map


# Display interactive factory map
st.subheader("Interactive Factory Location Map")

fig_factory = px.scatter_map(
    factory_data,
    lat="Latitude",
    lon="Longitude",
    hover_name="Factory",
    hover_data={
        "Latitude": True,
        "Longitude": True
    },
    zoom=3.2,
    height=550,
    title="Geographical Distribution of Factories",
    map_style="open-street-map"
)

fig_factory.update_layout(
    margin={
        "r": 0,
        "t": 50,
        "l": 0,
        "b": 0
    }
)

st.plotly_chart(
    fig_factory,
    use_container_width=True
)



st.plotly_chart(
    fig_factory,
    use_container_width=True
)

# Factory coordinate table

st.subheader("Factory Coordinate Details")

st.dataframe(
    factory_data,
    use_container_width=True,
    hide_index=True
)

# Factory location insights

st.subheader("Factory Location Summary")

st.write(
    "The map represents the geographical distribution "
    "of five factory locations. Users can hover over "
    "the map markers to view factory names and their "
    "corresponding geographical coordinates."
)

st.info(
    "Factory coordinates are used to visualize "
    "geographical locations. They do not independently "
    "represent product-to-factory relationships."
)

# ==================================================
# MODULE 6: PRODUCTS AND FACTORIES CORRELATION
# ==================================================

st.markdown("---")

st.header("6. Products and Factories Correlation Analysis")

st.write(
    "This module analyses the relationship between "
    "product divisions, individual products and their "
    "assigned manufacturing factories."
)

# ------------------------------------------
# PRODUCT AND FACTORY MAPPING
# ------------------------------------------

product_factory_data = pd.DataFrame({

    "Division": [
        "Chocolate", "Chocolate", "Chocolate",
        "Chocolate", "Chocolate",
        "Sugar", "Sugar", "Sugar", "Sugar",
        "Other",
        "Sugar",
        "Sugar",
        "Other", "Other", "Other"
    ],

    "Product Name": [
        "Wonka Bar - Nutty Crunch Surprise",
        "Wonka Bar - Fudge Mallows",
        "Wonka Bar -Scrumdiddlyumptious",
        "Wonka Bar - Milk Chocolate",
        "Wonka Bar - Triple Dazzle Caramel",
        "Laffy Taffy",
        "SweeTARTS",
        "Nerds",
        "Fun Dip",
        "Fizzy Lifting Drinks",
        "Everlasting Gobstopper",
        "Hair Toffee",
        "Lickable Wallpaper",
        "Wonka Gum",
        "Kazookles"
    ],

    "Factory": [
        "Lot's O' Nuts",
        "Lot's O' Nuts",
        "Lot's O' Nuts",
        "Wicked Choccy's",
        "Wicked Choccy's",
        "Sugar Shack",
        "Sugar Shack",
        "Sugar Shack",
        "Sugar Shack",
        "Sugar Shack",
        "Secret Factory",
        "The Other Factory",
        "Secret Factory",
        "Secret Factory",
        "The Other Factory"
    ]
})


# ------------------------------------------
# FACTORY COORDINATES
# ------------------------------------------

factory_coordinates = pd.DataFrame({

    "Factory": [
        "Lot's O' Nuts",
        "Wicked Choccy's",
        "Sugar Shack",
        "Secret Factory",
        "The Other Factory"
    ],

    "Latitude": [
        32.881893,
        32.076176,
        48.119140,
        41.446333,
        35.117500
    ],

    "Longitude": [
        -111.768036,
        -81.088371,
        -96.181150,
        -90.565487,
        -89.971107
    ]
})


# ------------------------------------------
# KPI SUMMARY
# ------------------------------------------

total_products = product_factory_data[
    "Product Name"
].nunique()

total_factories = product_factory_data[
    "Factory"
].nunique()

total_divisions = product_factory_data[
    "Division"
].nunique()

a, b, c = st.columns(3)

a.metric("Total Products", total_products)
b.metric("Total Factories", total_factories)
c.metric("Total Divisions", total_divisions)


# ------------------------------------------
# INTERACTIVE FILTERS
# ------------------------------------------

st.subheader("Product and Factory Filters")

f1, f2, f3 = st.columns(3)

with f1:
    division_filter = st.selectbox(
        "Select Division",
        ["All Divisions"] +
        sorted(product_factory_data["Division"].unique()),
        key="factory_division_filter"
    )

with f2:
    factory_filter = st.selectbox(
        "Select Factory",
        ["All Factories"] +
        sorted(product_factory_data["Factory"].unique()),
        key="product_factory_filter"
    )

with f3:
    search_product = st.text_input(
        "Search Product",
        placeholder="Enter product name...",
        key="factory_product_search"
    )


# ------------------------------------------
# APPLY FILTERS
# ------------------------------------------

mapping_filtered = product_factory_data.copy()

if division_filter != "All Divisions":

    mapping_filtered = mapping_filtered[
        mapping_filtered["Division"] == division_filter
    ]

if factory_filter != "All Factories":

    mapping_filtered = mapping_filtered[
        mapping_filtered["Factory"] == factory_filter
    ]

if search_product.strip():

    mapping_filtered = mapping_filtered[
        mapping_filtered["Product Name"].str.contains(
            search_product,
            case=False,
            na=False
        )
    ]


# ------------------------------------------
# PRODUCT FACTORY RELATIONSHIP TABLE
# ------------------------------------------

st.markdown("---")

st.subheader("Product-to-Factory Relationship Table")

st.dataframe(
    mapping_filtered,
    use_container_width=True,
    hide_index=True
)


# ------------------------------------------
# FACTORY-WISE PRODUCT COUNT
# ------------------------------------------

st.markdown("---")

st.subheader("Factory-wise Product Distribution")

factory_summary = (
    mapping_filtered.groupby("Factory", as_index=False)
    .agg(
        Product_Count=("Product Name", "nunique")
    )
)

fig_factory_products = px.bar(
    factory_summary,
    x="Factory",
    y="Product_Count",
    color="Factory",
    title="Number of Products Assigned to Each Factory",
    text="Product_Count"
)

st.plotly_chart(
    fig_factory_products,
    use_container_width=True
)


# ------------------------------------------
# DIVISION-WISE PRODUCT DISTRIBUTION
# ------------------------------------------

st.subheader("Division-wise Product Distribution")

division_summary_factory = (
    mapping_filtered.groupby("Division", as_index=False)
    .agg(
        Product_Count=("Product Name", "nunique")
    )
)

fig_division_products = px.pie(
    division_summary_factory,
    names="Division",
    values="Product_Count",
    title="Product Distribution by Division",
    hole=0.4
)

st.plotly_chart(
    fig_division_products,
    use_container_width=True
)


# ------------------------------------------
# DIVISION AND FACTORY RELATIONSHIP
# ------------------------------------------

st.subheader("Division and Factory Relationship")

fig_relationship = px.sunburst(
    mapping_filtered,
    path=["Division", "Factory", "Product Name"],
    title="Division → Factory → Product Hierarchy"
)

st.plotly_chart(
    fig_relationship,
    use_container_width=True
)


# ------------------------------------------
# CONNECT PRODUCT MAPPING WITH SALES DATA
# ------------------------------------------

st.markdown("---")

st.subheader("Product-wise Sales and Factory Analysis")

# Normalize names to improve matching
def normalize_product_name(series):
    return (
        series.astype(str)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .str.casefold()
    )

mapping_sales = product_factory_data.copy()
sales_products = product_summary.copy()

mapping_sales["Product Key"] = normalize_product_name(
    mapping_sales["Product Name"]
)

sales_products["Product Key"] = normalize_product_name(
    sales_products["Product Name"]
)

factory_performance = mapping_sales.merge(
    sales_products[
        [
            "Product Key",
            "Sales",
            "Cost",
            "Gross Profit",
            "Gross Margin"
        ]
    ],
    on="Product Key",
    how="left"
)

st.dataframe(
    factory_performance[
        [
            "Division",
            "Product Name",
            "Factory",
            "Sales",
            "Cost",
            "Gross Profit",
            "Gross Margin"
        ]
    ],
    use_container_width=True,
    hide_index=True
)

matched_products = factory_performance[
    "Sales"
].notna().sum()

unmatched_products = total_products - matched_products

st.info(
    f"Products matched with sales data: {matched_products} | "
    f"Products without a matching sales record: {unmatched_products}"
)

st.caption(
    "Product-factory relationships are based on the "
    "provided mapping. Sales and profitability figures "
    "are joined using normalized product names."
)

# ==================================================
# 8. FINAL DATA SUMMARY
# ==================================================

st.markdown("---")

st.header("Final Data Summary")

st.write(
    "Number of records after filtering:",
    len(filtered_df)
)

st.write(
    "Number of products:",
    filtered_df["Product Name"].nunique()
)

st.write(
    "Number of divisions:",
    filtered_df["Division"].nunique()
)

st.caption(
    "Nassau Candy Distributor | Product Line "
    "Profitability & Margin Performance Analysis"
)

st.success("Complete Dashboard Loaded Successfully!")
