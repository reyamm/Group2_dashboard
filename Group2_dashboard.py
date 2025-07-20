import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
df = pd.read_csv("merged_output.csv")
df_deadly = pd.read_csv("disaster_predictions_logreg.csv")
df_severity = pd.read_csv("disaster_predictions_with_severity.csv")

df['Predicted_Deadly'] = df_deadly['Predicted_Is_Deadly']
df['Predicted_Severity'] = df_severity['Predicted_Severity_Level']

df['Start Year'] = pd.to_numeric(df['Start Year'], errors='coerce')
df['Total Deaths'] = pd.to_numeric(df['Total Deaths'], errors='coerce').fillna(0)
df['Location'] = df['Location'].fillna("Unknown")
df['Disaster Subgroup'] = df['Disaster Subgroup'].fillna("Unknown")
df['Disaster Subtype'] = df['Disaster Subtype'].fillna("Unknown")
if "Total Damage ('000 US$)" in df.columns:
    df["Total Damage ('000 US$)"] = pd.to_numeric(df["Total Damage ('000 US$)"], errors='coerce').fillna(0)

st.set_page_config(page_title="Saudi Disasters Dashboard", layout="wide")
st.title("Saudi Disasters Dashboard")

# Filters
st.sidebar.header("Filters")
min_year, max_year = int(df['Start Year'].min()), int(df['Start Year'].max())
year_range = st.sidebar.slider("Year Range", min_year, max_year, (min_year, max_year))
disaster_types = st.sidebar.multiselect("Disaster Types", sorted(df['Disaster Type'].unique()), sorted(df['Disaster Type'].unique()))
cities = st.sidebar.multiselect("Cities", sorted(df['Location'].unique()), sorted(df['Location'].unique()))

filtered_df = df[
    (df['Start Year'] >= year_range[0]) &
    (df['Start Year'] <= year_range[1]) &
    (df['Disaster Type'].isin(disaster_types)) &
    (df['Location'].isin(cities))
]

if filtered_df.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

# Clean & aligned Key Metrics
st.subheader("Key Metrics and Insights")

total_deaths = int(filtered_df['Total Deaths'].sum())
avg_deaths = round(filtered_df['Total Deaths'].mean(), 2)
most_common_disaster = filtered_df['Disaster Type'].mode()[0]
deadliest_event = filtered_df.loc[filtered_df['Total Deaths'].idxmax()]
most_frequent_city = filtered_df['Location'].mode()[0]
earliest_year = int(filtered_df['Start Year'].min())
latest_year = int(filtered_df['Start Year'].max())
unique_subgroups = filtered_df['Disaster Subgroup'].nunique()
most_frequent_subgroup = filtered_df['Disaster Subgroup'].mode()[0]

# Organize nicely in 2 rows
col1, col2, col3, col4 = st.columns(4)
col5, col6, col7, col8 = st.columns(4)

col1.metric("Total Deaths", total_deaths)
col2.metric("Average Deaths/Event", avg_deaths)
col3.metric("Most Common Disaster", most_common_disaster)
col4.metric("Deadliest Event", f"{deadliest_event['Disaster Type']} ({int(deadliest_event['Total Deaths'])})")

col5.metric("Most Frequent City", most_frequent_city)
col6.metric("Earliest Event Year", earliest_year)
col7.metric("Latest Event Year", latest_year)
col8.metric("Most Frequent Subgroup", most_frequent_subgroup)

st.markdown("---")

# 📊 EDA Visualizations (16, excluding region)

# Temporal
st.subheader("Exploratory Data Analysis")

deaths_year = filtered_df.groupby('Start Year')['Total Deaths'].sum().reset_index()
st.plotly_chart(px.line(deaths_year, x='Start Year', y='Total Deaths', title='Deaths Over Time'), use_container_width=True)

disasters_year = filtered_df.groupby('Start Year').size().reset_index(name='Count')
st.plotly_chart(px.area(disasters_year, x='Start Year', y='Count', title='Disasters Over Time'), use_container_width=True)

deaths_year['Cumulative'] = deaths_year['Total Deaths'].cumsum()
st.plotly_chart(px.line(deaths_year, x='Start Year', y='Cumulative', title='Cumulative Deaths Over Time'), use_container_width=True)

type_counts = filtered_df['Disaster Type'].value_counts().reset_index()
type_counts.columns = ['Disaster Type', 'Count']
st.plotly_chart(px.pie(type_counts, names='Disaster Type', values='Count', title='Disaster Type Distribution'), use_container_width=True)

type_year = filtered_df.groupby(['Start Year', 'Disaster Type']).size().reset_index(name='Count')
st.plotly_chart(px.bar(type_year, x='Start Year', y='Count', color='Disaster Type', animation_frame='Start Year',
                       range_y=[0, type_year['Count'].max()], title='Disaster Types Over Years (Animated)'), use_container_width=True)

subtype_counts = filtered_df['Disaster Subtype'].value_counts().reset_index()
subtype_counts.columns = ['Disaster Subtype', 'Count']
st.plotly_chart(px.bar(subtype_counts, x='Disaster Subtype', y='Count', title='Disaster Subtype Counts'), use_container_width=True)

st.plotly_chart(px.treemap(filtered_df, path=['Disaster Subgroup', 'Disaster Type'], title='Disaster Subgroup vs Type (Treemap)'), use_container_width=True)

city_counts = filtered_df.groupby('Location').size().reset_index(name='Count').sort_values(by='Count', ascending=False)
st.plotly_chart(px.bar(city_counts, x='Count', y='Location', orientation='h', title='Disasters per City'), use_container_width=True)

heatmap_data = filtered_df.groupby(['Location', 'Disaster Type']).size().reset_index(name='Count')
heatmap_pivot = heatmap_data.pivot(index='Location', columns='Disaster Type', values='Count').fillna(0)
st.plotly_chart(px.imshow(heatmap_pivot, title='Heatmap: City vs Disaster Type'), use_container_width=True)

if 'Latitude' in filtered_df.columns and 'Longitude' in filtered_df.columns:
    fig_map = px.scatter_map(filtered_df, lat='Latitude', lon='Longitude', color='Disaster Type',
                             size='Total Deaths', hover_name='Location',
                             title='Interactive Disaster Locations Map', zoom=4)
    fig_map.update_layout(map_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig_map, use_container_width=True)

deaths_type = filtered_df.groupby(['Disaster Type'])['Total Deaths'].sum().reset_index()
st.plotly_chart(px.bar(deaths_type, x='Disaster Type', y='Total Deaths', title='Deaths per Disaster Type'), use_container_width=True)

if "Total Damage ('000 US$)" in filtered_df.columns:
    st.plotly_chart(px.histogram(filtered_df, x="Total Damage ('000 US$)", nbins=30, title='Damage Distribution'), use_container_width=True)

if 'Magnitude' in filtered_df.columns:
    st.plotly_chart(px.scatter(filtered_df, x='Magnitude', y='Total Deaths',
                               size="Total Damage ('000 US$)", color='Disaster Type',
                               title='Magnitude vs Deaths (Bubble)'), use_container_width=True)

st.plotly_chart(px.box(filtered_df, x='Disaster Type', y='Total Deaths', points='all', title='Deaths by Disaster Type (Boxplot)'), use_container_width=True)

st.plotly_chart(px.scatter(filtered_df, x='Start Year', y='Total Deaths', size="Total Damage ('000 US$)", color='Disaster Type',
                           animation_frame='Start Year', title='Animated Bubble: Deaths over Time'), use_container_width=True)

st.markdown("---")

# Predictions
st.subheader("Predictions")

deadly_counts = filtered_df['Predicted_Deadly'].value_counts().reset_index()
deadly_counts.columns = ['Deadly', 'Count']
st.plotly_chart(px.pie(deadly_counts, names='Deadly', values='Count', title='Predicted Deadly vs Non-Deadly'), use_container_width=True)

severity_type = filtered_df.groupby(['Disaster Type', 'Predicted_Severity']).size().reset_index(name='Count')
st.plotly_chart(px.bar(severity_type, x='Disaster Type', y='Count', color='Predicted_Severity',
                       barmode='stack', title='Severity Levels by Disaster Type'), use_container_width=True)

# Data Table
st.subheader("Filtered Data Table")
st.dataframe(filtered_df)

csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    "Download Filtered Data as CSV",
    data=csv,
    file_name='filtered_disasters_with_predictions.csv',
    mime='text/csv'
)
