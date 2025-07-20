import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Saudi Disasters Dashboard", layout="wide")
st.title("Saudi Disasters Dashboard")

# Load datasets
df = pd.read_csv("merged_output.csv")
df_severity = pd.read_csv("disaster_predictions_with_severity.csv")
df_deadly = pd.read_csv("disaster_predictions_logreg.csv")

# Normalize columns to avoid KeyError
df_severity.columns = df_severity.columns.str.strip().str.lower()
df_deadly.columns = df_deadly.columns.str.strip().str.lower()

severity_col = [col for col in df_severity.columns if 'severity' in col][0]
deadly_col = [col for col in df_deadly.columns if 'deadly' in col][0]

df['Predicted_Severity'] = df_severity[severity_col]
df['Predicted_Deadly'] = df_deadly[deadly_col].map({1: "Yes", 0: "No"})

df['Start Year'] = pd.to_numeric(df['Start Year'], errors='coerce')
df['Total Deaths'] = pd.to_numeric(df['Total Deaths'], errors='coerce').fillna(0)

# Sidebar filters
st.sidebar.header("Filters")
min_year, max_year = int(df['Start Year'].min()), int(df['Start Year'].max())
year_range = st.sidebar.slider("Start Year", min_year, max_year, (min_year, max_year))

disaster_types = st.sidebar.multiselect(
    "Disaster Type", sorted(df['Disaster Type'].dropna().unique()), sorted(df['Disaster Type'].dropna().unique())
)

cities_all = pd.Series(sum([loc.split(", ") for loc in df['Location'].dropna()], [])).unique()
cities = st.sidebar.multiselect("Cities", sorted(cities_all), None)

filtered_df = df[
    (df['Start Year'] >= year_range[0]) &
    (df['Start Year'] <= year_range[1]) &
    (df['Disaster Type'].isin(disaster_types))
]

if cities:
    filtered_df = filtered_df[filtered_df['Location'].str.contains('|'.join(cities), na=False)]

if filtered_df.empty:
    st.warning("No data available for selected filters.")
    st.stop()

st.header("Key Metrics and Insights")
col1, col2, col3, col4 = st.columns(4)
col5, col6, col7, col8 = st.columns(4)

total_deaths = int(filtered_df['Total Deaths'].sum())
avg_deaths = round(filtered_df['Total Deaths'].mean(), 2)
most_common_type = filtered_df['Disaster Type'].mode()[0]
deadliest_event = filtered_df.loc[filtered_df['Total Deaths'].idxmax()]
unique_subgroups = filtered_df['Disaster Subgroup'].nunique()
most_frequent_city = filtered_df['Location'].mode()[0]
earliest_year = int(filtered_df['Start Year'].min())
latest_year = int(filtered_df['Start Year'].max())
most_freq_subgroup = filtered_df['Disaster Subgroup'].mode()[0]

col1.metric("Total Deaths", total_deaths)
col2.metric("Avg Deaths/Event", avg_deaths)
col3.metric("Most Common Disaster", most_common_type)
col4.metric("Deadliest Event", f"{deadliest_event['Disaster Type']} ({int(deadliest_event['Total Deaths'])})")
col5.metric("Unique Subgroups", unique_subgroups)
col6.metric("Most Frequent City", most_frequent_city)
col7.metric("Earliest Year", earliest_year)
col8.metric("Latest Year", latest_year)

st.metric("Most Frequent Subgroup", most_freq_subgroup)

st.header("Exploratory Data Analysis")

# Deaths per year
deaths_year = filtered_df.groupby('Start Year')['Total Deaths'].sum().reset_index()
st.plotly_chart(px.line(deaths_year, x='Start Year', y='Total Deaths', title="Deaths Over Time"), use_container_width=True)

# Disasters count per year
disasters_year = filtered_df.groupby('Start Year').size().reset_index(name='Count')
st.plotly_chart(px.area(disasters_year, x='Start Year', y='Count', title="Disasters Over Time"), use_container_width=True)

# Cumulative deaths
deaths_year['Cumulative'] = deaths_year['Total Deaths'].cumsum()
st.plotly_chart(px.line(deaths_year, x='Start Year', y='Cumulative', title="Cumulative Deaths"), use_container_width=True)

# Disaster type pie
type_counts = filtered_df['Disaster Type'].value_counts().reset_index()
type_counts.columns = ['Disaster Type', 'Count']
st.plotly_chart(px.pie(type_counts, names='Disaster Type', values='Count', title="Disaster Type Distribution"), use_container_width=True)

# Animated bar
type_year = filtered_df.groupby(['Start Year', 'Disaster Type']).size().reset_index(name='Count')
st.plotly_chart(px.bar(type_year, x='Start Year', y='Count', color='Disaster Type', animation_frame='Start Year',
                       range_y=[0, type_year['Count'].max()], title="Disaster Types Over Years (Animated)"), use_container_width=True)

# Subtype bar
subtype_counts = filtered_df['Disaster Subtype'].value_counts().reset_index()
subtype_counts.columns = ['Disaster Subtype', 'Count']
st.plotly_chart(px.bar(subtype_counts, x='Disaster Subtype', y='Count', title="Disaster Subtype Counts"), use_container_width=True)

# Treemap
st.plotly_chart(px.treemap(filtered_df, path=['Disaster Subgroup', 'Disaster Type'],
                           title="Disaster Subgroup vs Type (Treemap)"), use_container_width=True)

# Top cities bar
city_exp = filtered_df.copy()
city_exp = city_exp.assign(Location=city_exp['Location'].str.split(', ')).explode('Location')
top_cities = city_exp['Location'].value_counts().head(10).reset_index()
top_cities.columns = ['City', 'Count']
st.plotly_chart(px.bar(top_cities, x='City', y='Count', title="Top 10 Cities with Most Disasters"), use_container_width=True)

# Deaths by type
deaths_type = filtered_df.groupby('Disaster Type')['Total Deaths'].sum().reset_index()
st.plotly_chart(px.bar(deaths_type, x='Disaster Type', y='Total Deaths', title="Deaths per Disaster Type"), use_container_width=True)

# Damage histogram
if "Total Damage ('000 US$)" in filtered_df.columns:
    st.plotly_chart(px.histogram(filtered_df, x="Total Damage ('000 US$)", nbins=30, title="Damage Distribution"), use_container_width=True)

# Scatter: magnitude vs deaths
if 'Magnitude' in filtered_df.columns:
    st.plotly_chart(px.scatter(filtered_df, x='Magnitude', y='Total Deaths',
                               size="Total Damage ('000 US$)", color='Disaster Type',
                               title="Magnitude vs Deaths"), use_container_width=True)

# Boxplot: deaths by type
st.plotly_chart(px.box(filtered_df, x='Disaster Type', y='Total Deaths', points='all',
                       title="Deaths by Disaster Type (Boxplot)"), use_container_width=True)

# Animated scatter
st.plotly_chart(px.scatter(filtered_df, x='Start Year', y='Total Deaths',
                           size="Total Damage ('000 US$)", color='Disaster Type',
                           animation_frame='Start Year', title="Animated Deaths Over Time"), use_container_width=True)

# Map
if 'Latitude' in filtered_df.columns and 'Longitude' in filtered_df.columns:
    map_fig = px.scatter_mapbox(filtered_df, lat='Latitude', lon='Longitude',
                                color='Disaster Type', size='Total Deaths', hover_name='Location',
                                zoom=4, title="Disaster Locations Map")
    map_fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(map_fig, use_container_width=True)
st.header("Predictions")
# Heatmap of severity
st.header("Heatmap: Average Severity Levels (Top Cities × Disaster Types)")

df_exp = filtered_df.copy()
df_exp = df_exp.assign(Location=df_exp['Location'].str.split(', ')).explode('Location')
df_exp = df_exp[df_exp['Location'].isin(top_cities['City'])]

severity_map = {'Low': 1, 'Medium': 2, 'High': 3}
df_exp['Severity_Numeric'] = df_exp['Predicted_Severity'].map(severity_map)

heatmap_data = df_exp.groupby(['Location', 'Disaster Type'])['Severity_Numeric'].mean().reset_index()
heatmap_pivot = heatmap_data.pivot(index='Location', columns='Disaster Type', values='Severity_Numeric')

fig_heatmap = px.imshow(
    heatmap_pivot,
    labels=dict(x="Disaster Type", y="City", color="Avg Severity Level"),
    x=heatmap_pivot.columns,
    y=heatmap_pivot.index,
    color_continuous_scale='RdYlBu',
    title="Heatmap of Average Predicted Severity Levels"
)
st.plotly_chart(fig_heatmap, use_container_width=True)

# Predictions: deadly


deadly_counts = df['Predicted_Deadly'].value_counts().reset_index()
deadly_counts.columns = ['Predicted_Deadly', 'Count']
fig_deadly = px.pie(deadly_counts, names='Predicted_Deadly', values='Count',
                    title="Predicted Deadly Events (Yes/No)")
st.plotly_chart(fig_deadly, use_container_width=True)

# Predictions: severity by type
severity_type = df.groupby(['Disaster Type', 'Predicted_Severity']).size().reset_index(name='Count')
fig_severity = px.bar(severity_type, x='Disaster Type', y='Count', color='Predicted_Severity',
                       barmode='stack', title="Predicted Severity by Disaster Type")
st.plotly_chart(fig_severity, use_container_width=True)

# Data Table
st.header("Filtered Data Table")
st.dataframe(filtered_df)

csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button("Download filtered data", data=csv,
                   file_name='filtered_disasters.csv', mime='text/csv')
