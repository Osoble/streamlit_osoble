import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page Setup ---
st.set_page_config(page_title="Tourism Analysis Dashboard", layout="wide")
st.title("Tourism Infrastructure Dashboard")

# --- Load Dataset ---
df = pd.read_csv("551015b5649368dd2612f795c2a9c2d8_20240902_115953.csv")


# Clean Data
df = df.drop(columns=["Observation URI", "references", "publisher", "dataset"], errors="ignore")
df["refArea"] = df["refArea"].apply(lambda x: x.split("/")[-1] if isinstance(x, str) else x)

# --- Show Raw Data Checkbox ---
if st.checkbox("Show raw data"):
    st.subheader("Raw data preview")
    st.dataframe(df)

st.divider()

# --- Chart 1: Top 10 Towns by Hotels ---
st.subheader("Top 10 Towns by Number of Hotels")
selected_n = st.slider("Select number of towns to display", 5, 20, 10)
hotels = (
    df.groupby("Town")["Total number of hotels"]
    .sum()
    .sort_values(ascending=False)
    .head(selected_n)
)

fig_hotels = px.bar(
    hotels,
    x=hotels.index,
    y=hotels.values,
    title=f"Top {selected_n} Towns by Number of Hotels",
    labels={"x": "Town", "y": "Number of Hotels"}
)
st.plotly_chart(fig_hotels, use_container_width=True)

st.markdown(f"""
**Insight:**  
Showing top **{selected_n} towns** ranked by total hotels.
Adjust the slider above to explore more or fewer towns.
""")

st.divider()

# --- Chart 3: Restaurant Availability Pie Chart ---
st.subheader("Restaurant Availability Distribution")

# Use a single column layout to control width
col = st.columns([0.3, 0.7])[0]  # first column takes 30% width, second is empty

with col:
    restaurant_filter = st.selectbox(
        "Choose data to display:",
        ["All Towns", "Only Towns with Hotels"],
        index=0,
    )

if restaurant_filter == "Only Towns with Hotels":
    df_rest = df[df["Total number of hotels"] > 0]
else:
    df_rest = df


restaurants = df_rest["Existence of restaurants - exists"].value_counts()

fig_restaurants = px.pie(
    values=restaurants.values,
    names=["No Restaurants", "Has Restaurants"] if len(restaurants) == 2 else restaurants.index.astype(str),
    title="Distribution of Restaurants (Exists vs Not)",
    hole=0.4
)
st.plotly_chart(fig_restaurants, use_container_width=True)

st.markdown(f"""
**Insight:**  
You selected **{restaurant_filter.lower()}**.  
This shows the share of towns that have restaurants vs. those that don't.
""")

#-----------------------------
# Bubble Chart: Tourism Index vs Hotels
chart_df = df[(df["Total number of hotels"] > 0) | (df["Total number of restaurants"] > 0)]

st.subheader("Select Regions for Bubble Chart")

available_regions = sorted(chart_df["refArea"].apply(lambda x: x.split("/")[-1]).unique())

# Use session state to remember which regions are selected
if "selected_regions" not in st.session_state:
    st.session_state.selected_regions = available_regions.copy()  # Default: select all

# --- Quick Action Buttons ---
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("Select All Regions"):
        st.session_state.selected_regions = available_regions.copy()
with col2:
    if st.button("Clear All Regions"):
        st.session_state.selected_regions = []

# --- Checkbox Grid ---
selected_regions = []
cols = st.columns(3)
for i, region in enumerate(available_regions):
    col = cols[i % 3]
    checked = region in st.session_state.selected_regions
    if col.checkbox(region, value=checked, key=f"region_{region}"):
        selected_regions.append(region)

# Update session state with new selections
st.session_state.selected_regions = selected_regions

# Filter dataset based on selected regions
chart_df = chart_df[chart_df["refArea"].apply(lambda x: x.split("/")[-1]).isin(selected_regions)]

size_scale = st.slider("Adjust bubble size scale", 10, 100, 30)

fig_bubble = px.scatter(
    chart_df,
    x="Tourism Index",
    y="Total number of hotels",
    size="Total number of restaurants",
    color=chart_df["refArea"].apply(lambda x: x.split("/")[-1]),
    hover_name="Town",
    title="Tourism Index vs Hotels (Bubble Size = Number of Restaurants)",
    size_max=size_scale
)
st.plotly_chart(fig_bubble, use_container_width=True)

# --- Dynamic Insight for Bubble Chart ---
if not chart_df.empty:
    avg_tourism = chart_df["Tourism Index"].mean()
    avg_hotels = chart_df["Total number of hotels"].mean()
    town_max_hotels = chart_df.loc[chart_df["Total number of hotels"].idxmax(), "Town"]
    max_hotels_value = chart_df["Total number of hotels"].max()

    st.markdown(f"""
    **Insight:**  
    - Currently selected towns have an **average Tourism Index of {avg_tourism:.2f}**  
    - Average number of hotels per town: **{avg_hotels:.1f}**  
    - Town with the most hotels in this view: **{town_max_hotels} ({max_hotels_value} hotels)**  
    - Bubble size reflects restaurants — large bubbles indicate towns with more food infrastructure.
    """)
else:
    st.info("No towns match the current selection — adjust filters above to see results.")
