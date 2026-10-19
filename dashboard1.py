
import os
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px 

# ---------- PAGE CONFIGURATION ----------
st.set_page_config(
    page_title="Customer Data Analysis ",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- PROFESSIONAL DASHBOARD DESIGN ----------
st.markdown("""
<style>
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1450px;
    }

    [data-testid="stMetric"] {
        background: var(--secondary-background-color);
        padding: 20px;
        border-radius: 14px;
        border: 1px solid rgba(128, 128, 128, 0.25);
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.95rem;
        font-weight: 600;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
    }

    [data-testid="stSidebar"] {
        border-right: 1px solid rgba(128, 128, 128, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# ---------- DASHBOARD HEADER ----------
st.title("📊 Customer Data Analysis Dashboard")
st.caption(
    "Explore customer records, country distribution, "
    "subscription trends and business insights."
)

st.divider()

# ---------- LOAD DATA ----------

@st.cache_data
def load_data():
    path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "customers-100.csv"
    )

    data = pd.read_csv(path)
    data.columns = data.columns.str.strip()

    required_columns = [
        "Country", "City", "Company",
        "First Name", "Last Name",
        "Email", "Subscription Date"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns in CSV: {', '.join(missing_columns)}"
        )

    data["Subscription Date"] = pd.to_datetime(
        data["Subscription Date"],
        errors="coerce"
    )

    return data


try:
    df = load_data()
except Exception as e:
    st.error(f"Could not load the dataset: {e}")
    st.stop()

# Data Quality Report

st.header("Data Quality Report")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Rows", f"{len(df):,}")

with col2:
    st.metric("Total Columns", f"{len(df.columns):,}")

with col3:
    st.metric(
        "Missing Values",
        f"{df.isnull().sum().sum():,}"
    )

with col4:
    st.metric(
        "Duplicate Rows",
        f"{df.duplicated().sum():,}"
    )

st.subheader("Missing Values by Column")

missing_data = df.isnull().sum()
missing_data = missing_data[missing_data > 0]

if not missing_data.empty:
    st.bar_chart(missing_data)
else:
    st.success("No missing values found!")

st.subheader("Dataset Preview")
st.dataframe(df.head(10), use_container_width=True)


# ---------- DATA QUALITY SCORE ----------
st.divider()
st.header("🎯 Data Quality Score")

# Total number of cells in the dataset
total_cells = df.shape[0] * df.shape[1]

# Count missing cells
missing_cells = int(df.isnull().sum().sum())

# Count duplicate rows
duplicate_rows = int(df.duplicated().sum())

# Calculate missing-value rate and duplicate-row rate
missing_rate = (
    missing_cells / total_cells * 100
    if total_cells > 0 else 0
)

duplicate_rate = (
    duplicate_rows / len(df) * 100
    if len(df) > 0 else 0
)

# Calculate overall score
quality_score = max(
    0,
    100 - missing_rate - duplicate_rate
)

# Display results
q1, q2, q3 = st.columns(3)

with q1:
    st.metric(
        "Overall Quality Score",
        f"{quality_score:.2f}%"
    )

with q2:
    st.metric(
        "Missing Values",
        f"{missing_cells:,}",
        delta=f"{missing_rate:.2f}% of all cells",
        delta_color="inverse"
    )

with q3:
    st.metric(
        "Duplicate Rows",
        f"{duplicate_rows:,}",
        delta=f"{duplicate_rate:.2f}% of rows",
        delta_color="inverse"
    )

# Progress bar
st.progress(int(round(quality_score)))

# Explain the score
if quality_score >= 90:
    st.success("Good dataset quality! Only limited cleaning may be needed.")
elif quality_score >= 70:
    st.warning("Moderate dataset quality. Review missing values and duplicates.")
else:
    st.error("Dataset needs cleaning before further analysis.")

st.caption(
    "Score formula: 100 − missing-cell percentage − duplicate-row percentage. "
    "This is a simple project-specific indicator, not a universal data-quality standard."
)

# ---------- SIDEBAR FILTERS ----------
st.sidebar.title("🔎 Dashboard Filters")

# Country filter
countries = sorted(df["Country"].dropna().unique())

selected_countries = st.sidebar.multiselect(
    "Select countries",
    options=countries,
    default=countries
)

# ---------- SUBSCRIPTION DATE RANGE FILTER ----------
st.sidebar.subheader("📅 Subscription Date Range")

valid_dates = df["Subscription Date"].dropna()

if not valid_dates.empty:
    min_date = valid_dates.min().date()
    max_date = valid_dates.max().date()

    selected_dates = st.sidebar.date_input(
        "Select date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        key="subscription_date_range"
    )
else:
    selected_dates = ()
    
# Customer / Company search

# ---------- ADVANCED CUSTOMER SEARCH ----------
search = st.sidebar.text_input(
    "🔎 Search customers",
    placeholder="Name, email, company, city...",
    key="advanced_customer_search"
)

# Apply country filter first
filtered = df[df["Country"].isin(selected_countries)].copy()

# Apply subscription date filter
if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:
    start_date, end_date = selected_dates

    filtered = filtered[
        filtered["Subscription Date"].dt.date.between(
            start_date,
            end_date
        )
    ].copy()
    
# Search across multiple customer fields
if search.strip():
    search_columns = [
        "First Name",
        "Last Name",
        "Email",
        "Company",
        "City",
        "Country"
    ]

    search_text = (
        filtered[search_columns]
        .fillna("")
        .astype(str)
        .agg(" ".join, axis=1)
    )

    filtered = filtered[
        search_text.str.contains(
            search.strip(),
            case=False,
            regex=False,
            na=False
        )
    ].copy()

st.sidebar.caption(
    f"Showing {len(filtered)} of {len(df)} customers"
)

# ---------- PROFESSIONAL BUSINESS OVERVIEW ----------

# ---------- DYNAMIC KPI DASHBOARD ----------
st.subheader("📌 Business Overview")

# Use the filtered data from the sidebar
total_customers = len(filtered)
total_countries = filtered["Country"].nunique()
total_companies = filtered["Company"].nunique()
total_cities = filtered["City"].nunique()

valid_subscriptions = (
    filtered["Subscription Date"].notna().sum()
)

k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.metric(
        "👥 Customers",
        f"{total_customers:,}"
    )

with k2:
    st.metric(
        "🌍 Countries",
        f"{total_countries:,}"
    )

with k3:
    st.metric(
        "🏢 Companies",
        f"{total_companies:,}"
    )

with k4:
    st.metric(
        "🏙️ Cities",
        f"{total_cities:,}"
    )

with k5:
    st.metric(
        "📅 Valid Subscriptions",
        f"{valid_subscriptions:,}"
    )

st.caption(
    "All KPIs update automatically based on your selected "
    "countries and customer search."
)

st.divider()

# ---------- INTERACTIVE CHARTS ----------
st.subheader("📊 Customer Data Visualization")

left, right = st.columns(2)

with left:
    st.markdown("#### 🌍 Customers by Country")

    chart_type = st.selectbox(
        "Choose chart type",
        ["Bar Chart", "Line Chart"],
        key="country_chart_type"
    )

    country_counts = (
        filtered["Country"]
        .value_counts()
        .head(10)
    )

    if not country_counts.empty:
        if chart_type == "Bar Chart":
            st.bar_chart(country_counts)
        else:
            st.line_chart(country_counts)

        st.caption("Top 10 countries in the filtered data.")
    else:
        st.info("No country data matches your filters.")


with right:
    st.markdown("#### 📅 Monthly Subscription Trend")

    valid_dates = filtered["Subscription Date"].dropna()

    if not valid_dates.empty:
        monthly = (
            valid_dates
            .dt.to_period("M")
            .value_counts()
            .sort_index()
        )

        monthly.index = monthly.index.astype(str)

        st.bar_chart(monthly)
        st.caption("Number of subscriptions recorded per month.")
    else:
        st.info("No valid subscription dates match your filters.")


st.divider()


# ---------- INTERACTIVE PIE / DONUT CHART ----------
st.divider()
st.header("🍩 Interactive Customer Distribution")

st.write(
    "Explore the distribution of customers across countries."
)

if filtered.empty:
    st.info("No customer records match your current filters.")

else:
    # Count customers by country
    country_counts = (
        filtered["Country"]
        .fillna("Unknown")
        .value_counts()
    )

    # Show top 7 countries and group the rest as Other
    if len(country_counts) > 8:
        chart_counts = country_counts.head(7).copy()
        chart_counts["Other Countries"] = (
            country_counts.iloc[7:].sum()
        )
    else:
        chart_counts = country_counts

    # Let the user choose chart style
    chart_style = st.radio(
        "Choose chart style",
        ["Pie Chart", "Donut Chart"],
        horizontal=True,
        key="customer_distribution_style"
    )

    hole_size = 0.0 if chart_style == "Pie Chart" else 0.5

    # Create interactive chart
    fig = px.pie(
        names=chart_counts.index,
        values=chart_counts.values,
        title="Customer Share by Country",
        hole=hole_size
    )

    fig.update_traces(
        textposition="inside",
        textinfo="percent",
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Customers: %{value}<br>"
            "Share: %{percent}"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        legend_title_text="Country",
        margin=dict(t=60, b=20, l=20, r=20)
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.caption(
        "The chart updates according to your selected countries "
        "and customer search."
    )

# Subscription date insights
df["Subscription Date"] = pd.to_datetime(
    df["Subscription Date"], errors="coerce"
)

valid_dates = df["Subscription Date"].dropna()

if not valid_dates.empty:
    latest_date = valid_dates.max()
    earliest_date = valid_dates.min()

    st.write(f"📅 Earliest subscription: {earliest_date.date()}")
    st.write(f"📅 Latest subscription: {latest_date.date()}")

    monthly_subscriptions = (
        valid_dates.dt.to_period("M").value_counts().sort_index()
    )

    st.write("📈 Monthly subscription counts")
    st.bar_chart(monthly_subscriptions)
    
    # ---------- PROFESSIONAL CUSTOMER INSIGHTS ----------
st.subheader("💡 Business Insights")

if filtered.empty:
    st.info("Change your filters to generate customer insights.")
else:
    country_counts = filtered["Country"].value_counts()
    valid_dates = filtered["Subscription Date"].dropna()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🌍 Customer Distribution")

        if not country_counts.empty:
            top_country = country_counts.index[0]
            top_count = int(country_counts.iloc[0])
            percentage = top_count / len(filtered) * 100

            st.success(
                f"**Top country:** {top_country}"
            )
            st.write(f"Customers: {top_count}")
            st.write(f"Share of filtered customers: {percentage:.1f}%")

        st.write(
            f"**Unique companies:** {filtered['Company'].nunique()}"
        )
        st.write(
            f"**Unique cities:** {filtered['City'].nunique()}"
        )

    with col2:
        st.markdown("#### 📅 Subscription Overview")

        if not valid_dates.empty:
            monthly_counts = (
                valid_dates.dt.to_period("M")
                .value_counts()
                .sort_index()
            )

            st.write(f"**Valid subscription dates:** {len(valid_dates)}")
            st.write(f"**First subscription:** {valid_dates.min().date()}")
            st.write(f"**Latest subscription:** {valid_dates.max().date()}")
            st.write(
    f"**Busiest month:** "
    f"{monthly_counts.idxmax().strftime('%B %Y')}"
)
            st.write(
                f"**Subscriptions in busiest month:** "
                f"{int(monthly_counts.max())}"
            )
        else:
            st.info("No valid subscription dates available.")

    st.caption(
        "Insights are calculated from the selected customer records "
        "using Python. They are not AI-generated predictions."
    )


# ---------- CUSTOMER SEGMENTATION ----------
st.divider()
st.header("👥 Customer Segmentation")

st.write(
    "Analyze customers by country, company, or subscription period."
)

# Select segmentation method
segment_type = st.selectbox(
    "Choose segmentation type",
    [
        "Country",
        "Company",
        "Subscription Period"
    ],
    key="customer_segment_type"
)

if filtered.empty:
    st.info("No customer records match your current filters.")

elif segment_type == "Country":
    segment_counts = (
        filtered["Country"]
        .fillna("Unknown")
        .value_counts()
        .head(10)
    )

    st.subheader("🌍 Customers by Country")
    st.bar_chart(segment_counts)

    st.dataframe(
        segment_counts.rename_axis("Country")
        .reset_index(name="Customer Count"),
        hide_index=True,
        use_container_width=True
    )

elif segment_type == "Company":
    segment_counts = (
        filtered["Company"]
        .fillna("Unknown")
        .value_counts()
        .head(10)
    )

    st.subheader("🏢 Customers by Company")
    st.bar_chart(segment_counts)

    st.dataframe(
        segment_counts.rename_axis("Company")
        .reset_index(name="Customer Count"),
        hide_index=True,
        use_container_width=True
    )

elif segment_type == "Subscription Period":
    dates = filtered["Subscription Date"].dropna()

    if dates.empty:
        st.info("No valid subscription dates are available.")
    else:
        today = pd.Timestamp.today().normalize()

        # Divide records into three date-based groups
        segment_labels = [
            "Older: before 1 year",
            "Recent: within 1 year",
            "Future-dated subscriptions"
        ]

        conditions = [
            dates < (today - pd.DateOffset(years=1)),
            (dates >= (today - pd.DateOffset(years=1)))
            & (dates <= today),
            dates > today
        ]

        segment_data = pd.Series(
            "Unclassified",
            index=dates.index,
            dtype="object"
        )

        for condition, label in zip(conditions, segment_labels):
            segment_data.loc[condition] = label

        segment_counts = (
            segment_data.value_counts()
            .reindex(segment_labels, fill_value=0)
        )

        st.subheader("📅 Customers by Subscription Period")
        st.bar_chart(segment_counts)

        st.dataframe(
            segment_counts.rename_axis("Subscription Period")
            .reset_index(name="Customer Count"),
            hide_index=True,
            use_container_width=True
        )

st.caption(
    "Segmentation is based on the currently filtered customer records. "
    "It describes the dataset; it does not predict customer behavior."
)

# ---------- CUSTOMER DATA CHAT ASSISTANT ----------
st.subheader("💬 Customer Data Chat Assistant")

st.write(
    "Ask a question about the customer data currently selected "
    "in your filters."
)

st.caption(
    "Try: How many customers? Which country has the most customers? "
    "How many companies? What is the subscription trend?"
)

question = st.chat_input(
    "Ask a question about your customers..."
)

if question:
    st.chat_message("user").write(question)

    q = question.lower().strip()

    with st.chat_message("assistant"):
        if filtered.empty:
            st.write(
                "No customer records match your current filters. "
                "Please change the filters and try again."
            )

        elif (
            "total customer" in q
            or "how many customer" in q
            or "number of customer" in q
            or "customer count" in q
        ):
            st.write(
                f"There are **{len(filtered)} customers** "
                "in the currently filtered data."
            )

        elif (
            "company" in q
            or "companies" in q
        ):
            st.write(
                f"There are **{filtered['Company'].nunique()} unique "
                "companies** in the currently filtered data."
            )

        elif (
            "city" in q
            or "cities" in q
        ):
            city_counts = filtered["City"].nunique()

            st.write(
                f"There are **{city_counts} unique cities** "
                "in the currently filtered data."
            )

        elif (
            "country" in q
            and any(word in q for word in ["most", "highest", "top", "maximum"])
        ):
            counts = filtered["Country"].value_counts()

            if not counts.empty:
                st.write(
                    f"The country with the most customers is "
                    f"**{counts.index[0]}**, with "
                    f"**{int(counts.iloc[0])} customers**."
                )
            else:
                st.write("No country information is available.")

        elif "countr" in q:
            country_list = sorted(
                filtered["Country"].dropna().unique()
            )

            st.write("Countries in the filtered data:")
            st.write(", ".join(country_list))

        elif any(word in q for word in ["subscription", "trend", "month"]):
            dates = filtered["Subscription Date"].dropna()

            if dates.empty:
                st.write("No valid subscription dates were found.")
            else:
                monthly_counts = (
                    dates.dt.to_period("M")
                    .value_counts()
                    .sort_index()
                )

                busiest_month = monthly_counts.idxmax()

                st.write(
                    f"Valid subscription dates: **{len(dates)}**"
                )
                st.write(
                    f"Busiest subscription month: **{busiest_month}**"
                )
                st.write(
                    f"Subscriptions in that month: "
                    f"**{int(monthly_counts.max())}**"
                )

        elif "email" in q:
            st.write(
                "Email information is available in the Customer Records "
                "table below. Use the sidebar search to find a customer."
            )

        else:
            st.write(
                "I can answer questions about customer count, countries, "
                "companies, cities and subscription trends. "
                "Try one of the example questions above."
            )


st.divider()

# ---------- COLUMN SELECTOR & DATA EXPLORER ----------

st.divider()
st.subheader("🔎 Column Selector & Data Explorer")

if filtered.empty:
    st.info("No customer records match the current filters.")
else:
    available_columns = filtered.columns.tolist()

    default_columns = [
        col for col in [
            "First Name",
            "Last Name",
            "Email",
            "Country",
            "City",
            "Company",
            "Subscription Date"
        ]
        if col in available_columns
    ]

    selected_columns = st.multiselect(
        "Choose columns to display",
        options=available_columns,
        default=default_columns,
        key="customer_display_columns"
    )

    if selected_columns:
        st.dataframe(
            filtered[selected_columns],
            use_container_width=True,
            hide_index=True
        )

        st.caption(
            f"Displaying {len(selected_columns)} columns "
            f"and {len(filtered):,} customer records."
        )
    else:
        st.warning("Please select at least one column.")
        
# ---------- CUSTOMER RECORDS ----------
st.subheader("👥 Customer Records")
st.dataframe(
    filtered,
    width="stretch",
    hide_index=True
)

st.download_button(
    label="⬇️ Download Filtered CSV",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="filtered_customers.csv",
    mime="text/csv",
    key="download_filtered_customers"
)


# ---------- EXCEL EXPORT ----------
import io

excel_buffer = io.BytesIO()

with pd.ExcelWriter(
    excel_buffer,
    engine="openpyxl"
) as writer:
    filtered.to_excel(
        writer,
        index=False,
        sheet_name="Customer Records"
    )

st.download_button(
    label="📊 Download Filtered Excel",
    data=excel_buffer.getvalue(),
    file_name="filtered_customers.xlsx",
    mime=(
        "application/vnd.openxmlformats-officedocument."
        "spreadsheetml.sheet"
    ),
    key="download_filtered_excel"
)

st.caption("Customer Data Analysis Dashboard • Built with Python, Pandas, Matplotlib and Streamlit")

# Data Cleaning Section

st.header("🧹 Data Cleaning")

st.write("Check and clean missing values and duplicate rows.")

cleaned_df = df.copy()

col1, col2 = st.columns(2)

with col1:
    st.write("Missing values:", cleaned_df.isnull().sum().sum())

with col2:
    st.write("Duplicate rows:", cleaned_df.duplicated().sum())

if st.button("Clean Dataset"):
    cleaned_df = cleaned_df.drop_duplicates()
    cleaned_df = cleaned_df.dropna()

    st.success("Dataset cleaned successfully!")

    st.write("Rows after cleaning:", len(cleaned_df))

    csv_data = cleaned_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Cleaned Dataset",
        data=csv_data,
        file_name="cleaned_customer_data.csv",
        mime="text/csv"
    )
    
    
# ---------- DATA VALIDATION & CLEANING PREVIEW ----------

st.divider()
st.subheader("🧹 Data Validation & Cleaning Preview")

if filtered.empty:
    st.info("No customer records available for validation.")
else:
    missing_cells = int(filtered.isnull().sum().sum())
    duplicate_rows = int(filtered.duplicated().sum())

    preview_df = filtered.drop_duplicates().dropna()
    removed_rows = len(filtered) - len(preview_df)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Missing Cells", f"{missing_cells:,}")

    with col2:
        st.metric("Duplicate Rows", f"{duplicate_rows:,}")

    with col3:
        st.metric("Rows After Cleaning", f"{len(preview_df):,}")

    st.write("**Missing values by column**")
    missing_by_column = filtered.isnull().sum()
    missing_by_column = missing_by_column[missing_by_column > 0]

    if missing_by_column.empty:
        st.success("No missing values found in the filtered data.")
    else:
        st.dataframe(
            missing_by_column.rename("Missing Values").to_frame(),
            use_container_width=True
        )

    st.write("**Cleaning preview**")
    st.caption(
        f"Potential rows removed by dropping duplicates and "
        f"rows containing missing values: {removed_rows:,}"
    )

    st.dataframe(
        preview_df.head(10),
        use_container_width=True,
        hide_index=True
    )

    # Download Business Insights Report

st.subheader("Download Business Insights Report")

country_counts = df["Country"].value_counts()
city_counts = df["City"].value_counts()

report = f"""
CUSTOMER DATA ANALYSIS REPORT
=============================

Total Customers/Records: {len(df)}
Total Unique Countries: {df['Country'].nunique()}
Total Unique Cities: {df['City'].nunique()}

Top Country:
{country_counts.idxmax() if not country_counts.empty else 'No data'}

Top City:
{city_counts.idxmax() if not city_counts.empty else 'No data'}
"""

st.download_button(
    label="Download Insights Report",
    data=report,
    file_name="customer_analysis_report.txt",
    mime="text/plain"
)

# Country-wise Customer Analysis
st.subheader("Customers by Country")

country_counts = df["Country"].value_counts().head(10)

st.bar_chart(country_counts)

# City-wise Customer Analysis
st.subheader("Top 10 Cities by Customers")

city_counts = df["City"].value_counts().head(10)

st.bar_chart(city_counts)

# Business Insights

st.header("💡 Business Insights")

# Customer Analysis - Key Findings

st.header("🔍 Customer Analysis & Key Findings")

# Country Analysis
country_counts = df["Country"].value_counts()

if not country_counts.empty:
    top_country = country_counts.idxmax()
    top_country_count = country_counts.max()
    country_percentage = (top_country_count / len(df)) * 100

    st.subheader("🌍 Country Analysis")

    col1, col2 = st.columns(2)

    col1.metric("Leading Country", top_country)
    col2.metric("Records in Leading Country", top_country_count)

    st.write(
        f"{country_percentage:.2f}% of all records "
        f"belong to {top_country}."
    )

    st.bar_chart(country_counts.head(10))

# City Analysis
city_counts = df["City"].value_counts()

if not city_counts.empty:
    top_city = city_counts.idxmax()
    top_city_count = city_counts.max()

    st.subheader("🏙️ City Analysis")

    col1, col2 = st.columns(2)

    col1.metric("Leading City", top_city)
    col2.metric("Records in Leading City", top_city_count)

    st.bar_chart(city_counts.head(10))

# Country with maximum customers
country_counts = df["Country"].value_counts()

if not country_counts.empty:
    top_country = country_counts.index[0]
    top_count = country_counts.iloc[0]

    st.success(
        f"Most customers are from {top_country} "
        f"({top_count} customers)."
    )

# ---------- CUSTOM DESIGN ----------
st.markdown("""
<style>
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}
[data-testid="stMetric"] {
    background: var(--secondary-background-color);
    padding: 18px;
    border-radius: 12px;
    border: 1px solid rgba(128,128,128,0.2);
}
</style>
""", unsafe_allow_html=True)

st.divider()


