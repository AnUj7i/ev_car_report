import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------------------------------------------------
# 🎨 Page Config
# ------------------------------------------------------------
st.set_page_config(page_title="EV Market Dashboard", layout="wide")

# Custom CSS for clean visuals
st.markdown("""
    <style>
    .metric-card {
        background-color: var(--background-color);
        padding: 1.2rem;
        border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        text-align: center;
        transition: transform 0.2s ease-in-out;
    }
    .metric-card:hover {
        transform: scale(1.03);
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
    }
    .metric-label {
        color: gray;
        font-size: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# 🧠 Load Data
# ------------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("new_ev_data.csv")
    df.columns = df.columns.str.strip().str.title()  # Clean column names
    return df

df = load_data()

# ------------------------------------------------------------
# 🌗 Theme Toggle
# ------------------------------------------------------------
theme = st.sidebar.radio("Choose Theme", ["🌞 Light Mode", "🌙 Dark Mode"])
if theme == "🌙 Dark Mode":
    st.markdown("<style>body { background-color: #0e1117; color: white; }</style>", unsafe_allow_html=True)

# ------------------------------------------------------------
# 🧭 Sidebar Filters
# ------------------------------------------------------------
st.sidebar.header("🔎 Filters")

years = df["Model Year"].dropna().unique()
selected_years = st.sidebar.multiselect("Select Model Year(s):", sorted(years), default=sorted(years))

brands = df["Make"].dropna().unique()
selected_brands = st.sidebar.multiselect("Select Brand(s):", sorted(brands))

filtered_df = df[
    df["Model Year"].isin(selected_years) &
    (df["Make"].isin(selected_brands) if selected_brands else True)
]

# ------------------------------------------------------------
# 🧾 Header
# ------------------------------------------------------------
st.title("⚡ Electric Vehicle Market Dashboard ")
st.markdown("Gain insights into EV trends, brands, and regional distribution 🚗🔋")

# ------------------------------------------------------------
# 📊 KPI Cards
# ------------------------------------------------------------
col1, col2, col3 = st.columns(3)

total_evs = len(filtered_df)
avg_range = None
avg_price = None

# Try to find Range/Price columns automatically
range_cols = [c for c in df.columns if "Range" in c]
price_cols = [c for c in df.columns if "Price" in c]

if range_cols:
    avg_range = round(filtered_df[range_cols[0]].mean(), 2)
if price_cols:
    avg_price = round(filtered_df[price_cols[0]].mean(), 2)

with col1:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-value'>{total_evs:,}</div>
        <div class='metric-label'>Total EVs</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-value'>{avg_range if avg_range else 'N/A'}</div>
        <div class='metric-label'>Avg Range (km)</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-value'>{avg_price if avg_price else 'N/A'}</div>
        <div class='metric-label'>Avg Price</div>
    </div>
    """, unsafe_allow_html=True)

# ------------------------------------------------------------
# 📈 Tabs
# ------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Market Trends", 
    "🏆 Brand Insights", 
    "🔋 Range & Price Analysis", 
    "🌍 Regional Distribution"
])

# ------------------------------------------------------------
# Tab 1 – Market Trends
# ------------------------------------------------------------
with tab1:
    st.subheader("📅 EV Adoption Over Time")

    yearly = (
        df.groupby("Model Year")
        .size()
        .reset_index(name="Registrations")
        .sort_values("Model Year")
    )

    fig_year = px.bar(
        yearly,
        x="Model Year",
        y="Registrations",
        color="Registrations",
        color_continuous_scale="Bluered",
        text="Registrations",
        title="EV Growth by Year"
    )

    fig_year.update_traces(texttemplate="%{text}", textposition="outside")
    fig_year.update_layout(
        xaxis_title="Model Year",
        yaxis_title="Number of EVs",
        title_x=0.5,
        font=dict(size=14),
    )
    st.plotly_chart(fig_year, use_container_width=True)

# ------------------------------------------------------------
# Tab 2 – Brand Insights
# ------------------------------------------------------------
with tab2:
    st.subheader("🏆 Top EV Brands by Popularity")

    brand_counts = (
        filtered_df["Make"]
        .value_counts()
        .reset_index()
    )

    brand_counts.columns = ["Brand", "Count"]
    brand_counts = brand_counts.loc[:, ~brand_counts.columns.duplicated()]
    brand_counts = brand_counts.head(10)

    fig_brand = px.bar(
        brand_counts,
        x="Brand",
        y="Count",
        color="Count",
        color_continuous_scale="viridis",
        text="Count",
        title="Top 10 EV Brands"
    )

    fig_brand.update_traces(texttemplate="%{text}", textposition="outside")
    fig_brand.update_layout(
        xaxis_title="Brand",
        yaxis_title="Vehicles Sold",
        title_x=0.5,
        font=dict(size=14),
    )
    st.plotly_chart(fig_brand, use_container_width=True)

# ------------------------------------------------------------
# Tab 3 – Range vs Price
# ------------------------------------------------------------
with tab3:
    st.subheader("🔋 Range vs Price Analysis")

    if range_cols and price_cols:
        range_col = range_cols[0]
        price_col = price_cols[0]

        fig_scatter = px.scatter(
            filtered_df,
            x=range_col,
            y=price_col,
            color="Make",
            hover_data=["Model"],
            title=f"{range_col} vs {price_col} by Brand",
        )
        fig_scatter.update_layout(title_x=0.5, font=dict(size=14))
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.warning("⚠️ Range or Price columns not found in dataset.")

# ------------------------------------------------------------
# Tab 4 – Regional Distribution
# ------------------------------------------------------------
with tab4:
    st.subheader("🌍 EV Distribution by Region/State")

    geo_cols = [c for c in df.columns if any(k in c.lower() for k in ["state", "city", "region", "country"])]

    if geo_cols:
        geo_col = geo_cols[0]
        geo_counts = df[geo_col].value_counts().reset_index()
        geo_counts.columns = ["Region", "Count"]

        fig_map = px.choropleth(
            geo_counts,
            locations="Region",
            color="Count",
            color_continuous_scale="Tealgrn",
            title="EV Distribution Across Regions",
        )
        fig_map.update_layout(title_x=0.5, font=dict(size=14))
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.warning("⚠️ No region/city data found in this dataset.")

# ------------------------------------------------------------
# Footer
# ------------------------------------------------------------
st.markdown("---")
st.markdown("<center>Built with ❤️ using Streamlit | EV Dashboard © 2025</center>", unsafe_allow_html=True)
