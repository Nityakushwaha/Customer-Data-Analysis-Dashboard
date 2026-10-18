
import os
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt



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

    div[data-testid="stVerticalBlock"] > div:has(> div.stButton) {
        gap: 0.5rem;
    }

    h1, h2, h3 {
        letter-spacing: -0.4px;
    }

    [data-testid="stSidebar"] {
        border-right: 1px solid rgba(128, 128, 128, 0.2);
    }
</style>
""", unsafe_allow_html=True)


# ---------- LOAD DATA ----------
@st.cache_data
def load_data():
    path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "customers-100.csv"
    )
    data = pd.read_csv(path)
    data.columns = data.columns.str.strip()
    data["Subscription Date"] = pd.to_datetime(
        data["Subscription Date"], errors="coerce"
    )
    return data

try:
    df = load_data()
except Exception as e:
    st.error(f"Could not load the dataset: {e}")
    st.stop()

# ---------- DESIGN ----------
st.markdown("""
<style>
.block-container {padding-top: 2rem; padding-bottom: 2rem;}
[data-testid="stMetric"] {
    background: var(--secondary-background-color);
    padding: 18px;
    border-radius: 12px;
    border: 1px solid rgba(128,128,128,0.2);
}
</style>
""", unsafe_allow_html=True)

st.title("📊 Customer Data Analysis")
st.caption("Customer data • Business insights • AI-powered analysis")

# ---------- SIDEBAR FILTERS ----------
st.sidebar.title("🔎 Dashboard Filters")

countries = sorted(df["Country"].dropna().unique())
selected_countries = st.sidebar.multiselect(
    "Select countries",
    countries,
    default=countries
)

search = st.sidebar.text_input("Search customer or company")

filtered = df[df["Country"].isin(selected_countries)].copy()

if search:
    mask = (
        filtered["First Name"].fillna("").astype(str)
        + " "
        + filtered["Last Name"].fillna("").astype(str)
        + " "
        + filtered["Company"].fillna("").astype(str)
        + " "
        + filtered["Email"].fillna("").astype(str)
    ).str.contains(search, case=False, na=False)

    filtered = filtered[mask]


# ---------- PROFESSIONAL BUSINESS OVERVIEW ----------
st.subheader("📌 Business Overview")

total_customers = len(filtered)
total_countries = filtered["Country"].nunique()
total_companies = filtered["Company"].nunique()
total_cities = filtered["City"].nunique()

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.metric(
        label="👥 Total Customers",
        value=f"{total_customers:,}"
    )

with k2:
    st.metric(
        label="🌍 Countries",
        value=f"{total_countries:,}"
    )

with k3:
    st.metric(
        label="🏢 Companies",
        value=f"{total_companies:,}"
    )

with k4:
    st.metric(
        label="🏙️ Cities",
        value=f"{total_cities:,}"
    )

st.caption("Metrics update automatically when you change the sidebar filters.")
st.divider()

# ---------- CHARTS ----------
left, right = st.columns(2)

with left:
    st.subheader("🌍 Customers by Country")
    country_counts = filtered["Country"].value_counts().head(10)

    if not country_counts.empty:
        fig, ax = plt.subplots(figsize=(8, 5))
        country_counts.sort_values().plot(
            kind="barh", ax=ax
        )
        ax.set_xlabel("Number of Customers")
        ax.set_ylabel("")
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.info("No country data for this filter.")

with right:
    st.subheader("📅 Subscription Trend")

    dates = filtered.dropna(subset=["Subscription Date"])

    if not dates.empty:
        monthly = (
            dates.set_index("Subscription Date")
            .resample("MS")
            .size()
        )

        fig, ax = plt.subplots(figsize=(8, 5))
        monthly.plot(kind="bar", ax=ax)
        ax.set_xlabel("Subscription Month")
        ax.set_ylabel("New Subscriptions")
        ax.tick_params(axis="x", labelrotation=60)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.info("No valid subscription dates.")

st.divider()

# ---------- AI INSIGHTS ----------
st.subheader("🤖 Customer Insights Assistant")
st.write(
    "Generate data-based insights or ask AI to analyze your customers."
)

if st.button("✨ Generate Quick Insights"):
    if filtered.empty:
        st.warning("No customer records match your filters.")
    else:
        top_country = filtered["Country"].value_counts()

        st.markdown("**Key findings**")
        st.write(f"- Analyzed {len(filtered)} customer records.")
        st.write(
            f"- Found {filtered['Country'].nunique()} countries "
            "in the filtered data."
        )
        st.write(
            f"- Found {filtered['Company'].nunique()} distinct companies."
        )

        if not top_country.empty:
            st.write(
                f"- Most represented country: **{top_country.index[0]}** "
                f"({top_country.iloc[0]} customers)."
            )

        st.caption(
            "These are rule-based insights generated by Python, "
            "not responses from a generative AI model."
        )

# ---------- CUSTOMER TABLE ----------
st.divider()
st.subheader("👥 Customer Records")


st.dataframe(
    df,
    width="stretch",
    hide_index=True
)


st.download_button(
    "⬇️ Download Filtered CSV",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="filtered_customers.csv",
    mime="text/csv"
)



# Automatic Customer Insights
st.subheader("📊 Customer Insights")

total_customers = len(df)
total_countries = df["Country"].nunique()

st.write(f"👥 Total customers: {total_customers}")
st.write(f"🌍 Total countries: {total_countries}")

# Country with maximum customers
country_counts = df["Country"].value_counts()

if not country_counts.empty:
    top_country = country_counts.index[0]
    top_count = country_counts.iloc[0]

    st.success(
        f"Most customers are from {top_country} "
        f"({top_count} customers)."
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



# ---------- PROFESSIONAL INTERACTIVE CHARTS ----------
st.header("📊 Professional Data Visualization")

left, right = st.columns(2)

with left:
    st.subheader("🌍 Top 10 Countries by Customers")

    country_data = (
        filtered["Country"]
        .value_counts()
        .head(10)
        .sort_values()
    )

    if not country_data.empty:
        fig, ax = plt.subplots(figsize=(8, 5))
        country_data.plot(kind="barh", ax=ax)
        ax.set_xlabel("Number of Customers")
        ax.set_ylabel("")
        ax.set_title("Customer Distribution by Country")
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.info("No country data available.")

with right:
    st.subheader("📈 Monthly Subscription Trend")

    subscription_dates = filtered["Subscription Date"].dropna()

    if not subscription_dates.empty:
        monthly_data = (
            subscription_dates
            .dt.to_period("M")
            .value_counts()
            .sort_index()
        )

        monthly_data.index = monthly_data.index.astype(str)
        st.line_chart(monthly_data)
    else:
        st.info("No valid subscription dates found.")

# ----------------------------------
# Customer Data Chat Assistant
# ----------------------------------

st.header("💬 Customer Data Chat Assistant")

st.caption(
    "Ask questions about your customer dataset. "
    "This assistant works without API credits."
)

question = st.chat_input(
    "Ask: Which country has the most customers?"
)

if question:
    st.chat_message("user").write(question)

    q = question.lower().strip()

    with st.chat_message("assistant"):
        if "total customer" in q or "how many customer" in q:
            st.write(f"Your dataset contains {len(df)} customers.")

        elif "country" in q and ("most" in q or "highest" in q or "top" in q):
            counts = df["Country"].value_counts()

            if not counts.empty:
                st.write(
                    f"The country with the most customers is "
                    f"{counts.index[0]}, with {counts.iloc[0]} customers."
                )
            else:
                st.write("No country data is available.")

        elif "countr" in q or "countries" in q:
            countries = sorted(df["Country"].dropna().unique())
            st.write("Countries in your dataset:")
            st.write(", ".join(countries))

        elif "subscription" in q or "trend" in q or "month" in q:
            dates = pd.to_datetime(
                df["Subscription Date"], errors="coerce"
            ).dropna()

            if dates.empty:
                st.write("No valid subscription dates were found.")
            else:
                monthly = dates.dt.to_period("M").value_counts().sort_index()
                st.write(f"Total valid subscription dates: {len(dates)}")
                st.write(f"Month with the most subscriptions: {monthly.idxmax()}")
                st.write(f"Subscriptions in that month: {monthly.max()}")

        else:
            st.write(
                "I can answer questions about total customers, "
                "countries, top country, and subscription trends. "
                "Try asking one of these questions."
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


# ---------- DASHBOARD HEADER ----------
st.title("📊 Customer Data Analysis Dashboard")
st.caption(
    "Explore customer records, country distribution, "
    "subscription trends and business insights."
)

st.divider()

# ---------- BUSINESS OVERVIEW ----------
st.subheader("📌 Business Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Customers", f"{len(filtered):,}")
c2.metric("Countries", filtered["Country"].nunique())
c3.metric("Companies", filtered["Company"].nunique())
c4.metric("Cities", filtered["City"].nunique())

st.caption(
    f"Showing {len(filtered):,} of {len(df):,} total customer records."
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
            st.write(f"**Busiest month:** {monthly_counts.idxmax()}")
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


st.caption("Customer Data Analysis Dashboard • Built with Python, Pandas, Matplotlib and Streamlit")
