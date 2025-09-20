import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page Setup ---
st.set_page_config(page_title="Tourism Analysis Dashboard", layout="wide")
st.title("🏨 Tourism Infrastructure Dashboard")

# --- Load Dataset ---
df = pd.read_csv(r"C:\Users\user\Downloads\551015b5649368dd2612f795c2a9c2d8_20240902_115953.csv")

# Clean Data
df = df.drop(columns=["Observation URI", "references", "publisher", "dataset"], errors="ignore")
df["refArea"] = df["refArea"].apply(lambda x: x.split("/")[-1] if isinstance(x, str) else x)

# --- Show Raw Data Checkbox ---
if st.checkbox("Show raw data"):
    st.subheader("📄 Raw data preview")
    st.dataframe(df)

st.divider()

# --- Chart 1: Top 10 Towns by Hotels ---
st.subheader("🏙️ Top 10 Towns by Number of Hotels")
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

# --- Chart 2: Tourism Index per Town ---
st.subheader("🌍 Tourism Index per Town")
min_index, max_index = int(df["Tourism Index"].min()), int(df["Tourism Index"].max())
selected_range = st.slider(
    "Select Tourism Index Range for Scatter Plot",
    min_value=min_index,
    max_value=max_index,
    value=(min_index, max_index)
)
filtered_df_scatter = df[df["Tourism Index"].between(selected_range[0], selected_range[1])]

fig_tourism = px.scatter(
    filtered_df_scatter,
    x="Town",
    y="Tourism Index",
    title=f"Tourism Index per Town (Range: {selected_range[0]}–{selected_range[1]})",
    labels={"Town": "Town", "Tourism Index": "Index Value"}
)
fig_tourism.update_xaxes(tickangle=45, showticklabels=False)
st.plotly_chart(fig_tourism, use_container_width=True)

st.markdown("""
**Insight:**  
This scatter plot is filtered by the Tourism Index range you select above.
Use it to focus on low-index or high-index towns.
""")

st.divider()

# --- Chart 3: Restaurant Availability Pie Chart ---
st.subheader("🍽️ Restaurant Availability Distribution")
restaurant_filter = st.radio(
    "Choose data to display:",
    ["All Towns", "Only Towns with Hotels"]
)

# Filter dataset based on selection
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

available_regions = sorted(chart_df["refArea"].apply(lambda x: x.split("/")[-1]).unique())
selected_regions = st.multiselect("Select Regions for Bubble Chart", available_regions, default=available_regions)

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




#------------------------
# --- Filters (Sidebar) ---
st.sidebar.header("🔧 Filters")
all_towns = sorted(df["Town"].unique())
selected_towns = st.sidebar.multiselect(
    "Select Towns to Display",
    options=all_towns,
    default=all_towns
)

min_index, max_index = int(df["Tourism Index"].min()), int(df["Tourism Index"].max())
selected_range = st.sidebar.slider(
    "Select Tourism Index Range",
    min_value=min_index,
    max_value=max_index,
    value=(min_index, max_index)
)

# --- Apply Filters ---
filtered_df = df[
    (df["Town"].isin(selected_towns)) &
    (df["Tourism Index"].between(selected_range[0], selected_range[1]))
]

# --- Top KPI Metrics ---
st.subheader("Key Metrics for Current Selection")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Towns Selected", len(filtered_df["Town"].unique()))

with col2:
    avg_index = filtered_df["Tourism Index"].mean()
    st.metric("Avg Tourism Index", f"{avg_index:.2f}")

with col3:
    total_hotels = filtered_df["Total number of hotels"].sum()
    st.metric("Total Hotels", total_hotels)

with col4:
    total_restaurants = filtered_df["Total number of restaurants"].sum()
    st.metric("Total Restaurants", total_restaurants)




# Extract region name
df["Region"] = df["refArea"].apply(lambda x: x.split("/")[-1] if isinstance(x, str) else x)

# Approximate lat/lon mapping (add more if you have more regions)
region_coords = {
    "Mount_Lebanon_Governorate": (33.833, 35.583),
    "North_Governorate": (34.4, 35.9),
    "South_Governorate": (33.3, 35.4),
    "Akkar_Governorate": (34.55, 36.2),
    "Beirut": (33.9, 35.5),
    "Bekaa_Governorate": (33.85, 36.15),
    "Nabatieh_Governorate": (33.38, 35.48)
}

# Create new columns for lat/lon
df["lat"] = df["Region"].map(lambda r: region_coords.get(r, (None, None))[0])
df["lon"] = df["Region"].map(lambda r: region_coords.get(r, (None, None))[1])

# Drop missing coords
map_df = df.dropna(subset=["lat", "lon"])

# Create interactive map
fig_map = px.scatter_mapbox(
    map_df,
    lat="lat",
    lon="lon",
    size="Total number of hotels",  # bubble size = hotels
    color="Tourism Index",  # color by tourism index
    hover_name="Town",
    color_continuous_scale="YlOrRd",
    zoom=7,
    mapbox_style="carto-positron",
    title="Tourism Index per Town (Bubble Map)"
)




st.subheader("🌳 Tourism Infrastructure Breakdown (Treemap)")
region_agg = df.groupby("refArea")[["Total number of hotels", "Total number of restaurants"]].sum().reset_index()

fig_treemap = px.treemap(
    region_agg,
    path=["refArea"],
    values="Total number of hotels",
    color="Total number of restaurants",
    color_continuous_scale="Blues",
    title="Treemap of Hotels (Color = Restaurants)"
)
st.plotly_chart(fig_treemap, use_container_width=True)

st.markdown("""
**Insight:**  
This treemap shows how hotels are distributed among regions, with color indicating number of restaurants.  
You can quickly spot which regions dominate and which are underrepresented.
""")

