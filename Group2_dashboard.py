import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
df = pd.read_csv("merged_output.csv")

# Preprocess
df['Start Year'] = pd.to_numeric(df['Start Year'], errors='coerce')
df['Total Deaths'] = pd.to_numeric(df['Total Deaths'], errors='coerce').fillna(0)
df['Location'] = df['Location'].fillna("Unknown")
df['Disaster Subgroup'] = df['Disaster Subgroup'].fillna("Unknown")
df['Disaster Subtype'] = df['Disaster Subtype'].fillna("Unknown")

if "Total Damage ('000 US$)" in df.columns:
    df["Total Damage ('000 US$)"] = pd.to_numeric(df["Total Damage ('000 US$)"], errors='coerce').fillna(0)

# Setup Streamlit page
st.set_page_config(page_title="Saudi Disasters Dashboard", layout="wide")
st.title("Saudi Disasters Dashboard")

# Sidebar filters
st.sidebar.header("Filters")

min_year, max_year = int(df['Start Year'].min()), int(df['Start Year'].max())

year_range = st.sidebar.slider(
    "Select Year Range",
    min_year,
    max_year,
    (min_year, max_year)
)

disaster_types = st.sidebar.multiselect(
    "Select Disaster Types",
    options=sorted(df['Disaster Type'].dropna().unique()),
    default=sorted(df['Disaster Type'].dropna().unique())
)

cities = st.sidebar.multiselect(
    "Select Cities (Location)",
    options=sorted(df['Location'].dropna().unique()),
    default=sorted(df['Location'].dropna().unique())
)

# Filter data
filtered_df = df[
    (df['Start Year'] >= year_range[0]) &
    (df['Start Year'] <= year_range[1]) &
    (df['Disaster Type'].isin(disaster_types)) &
    (df['Location'].isin(cities))
]

st.markdown(f"### Data from {year_range[0]} to {year_range[1]} | {len(filtered_df)} events")

if not filtered_df.empty:
    # Compute metrics
    total_deaths = int(filtered_df['Total Deaths'].sum())
    avg_deaths = round(filtered_df['Total Deaths'].mean(), 2)
    most_common_disaster = filtered_df['Disaster Type'].mode()[0]
    deadliest_event = filtered_df.loc[filtered_df['Total Deaths'].idxmax()]
    unique_disaster_subgroups = filtered_df['Disaster Subgroup'].nunique()
    most_frequent_city = filtered_df['Location'].mode()[0]
    earliest_year = int(filtered_df['Start Year'].min())
    latest_year = int(filtered_df['Start Year'].max())
    most_frequent_subgroup = filtered_df['Disaster Subgroup'].mode()[0]

    # Aligned Key Metrics
    st.subheader("Key Metrics and Insights")

    row1 = st.columns(4)
    row2 = st.columns(4)

    row1[0].metric("Total Deaths", total_deaths)
    row1[1].metric("Average Deaths/Event", avg_deaths)
    row1[2].metric("Most Common Disaster", most_common_disaster)
    row1[3].metric("Deadliest Event", f"{deadliest_event['Disaster Type']} ({int(deadliest_event['Total Deaths'])})")

    row2[0].metric("Most Frequent City", most_frequent_city)
    row2[1].metric("Earliest Event Year", earliest_year)
    row2[2].metric("Latest Event Year", latest_year)
    row2[3].metric("Most Frequent Subgroup", most_frequent_subgroup)

    st.subheader("View Deaths & Damage by Category")
    option = st.selectbox(
        "View by:",
        ['Disaster Type', 'Disaster Subtype']
    )

    grouped = filtered_df.groupby(option).agg(
        Total_Deaths=('Total Deaths', 'sum'),
        Total_Damage=('Total Damage (\'000 US$)', 'sum'),
        Event_Count=(option, 'count')
    ).reset_index()

    fig = px.bar(
        grouped,
        x=option,
        y=['Total_Deaths', 'Total_Damage'],
        barmode='group',
        title=f"Total Deaths and Damage by {option}"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Mean & Median Deaths per Disaster Type")
    agg_stats = filtered_df.groupby("Disaster Type").agg(
        Mean_Deaths=('Total Deaths', 'mean'),
        Median_Deaths=('Total Deaths', 'median')
    ).reset_index()

    fig_stats = px.bar(
        agg_stats,
        x="Disaster Type",
        y=["Mean_Deaths", "Median_Deaths"],
        barmode="group",
        title="Mean & Median Deaths by Disaster Type"
    )
    st.plotly_chart(fig_stats, use_container_width=True)

    st.subheader("Boxplot of Deaths by Disaster Type")
    fig_box = px.box(
        filtered_df,
        x='Disaster Type',
        y='Total Deaths',
        points='all',
        title="Deaths Distribution by Disaster Type"
    )
    st.plotly_chart(fig_box, use_container_width=True)

    st.subheader("Animated Scatter: Deaths & Damage Over Time")
    fig_animated = px.scatter(
        filtered_df,
        x='Start Year',
        y='Total Deaths',
        size="Total Damage ('000 US$)",
        color='Disaster Type',
        hover_name='Location',
        animation_frame='Start Year',
        title="Animated Deaths & Damage Over Time by Disaster Type",
        range_x=[min_year, max_year]
    )
    st.plotly_chart(fig_animated, use_container_width=True)

    st.subheader("Pie Chart: Disaster Subgroup Distribution")
    subgroup_counts = filtered_df['Disaster Subgroup'].value_counts().reset_index()
    subgroup_counts.columns = ['Disaster Subgroup', 'Count']
    fig_pie = px.pie(
        subgroup_counts,
        names='Disaster Subgroup',
        values='Count',
        title="Proportion of Disaster Subgroups"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

    st.subheader("Bar Chart: City-wise Disaster Summary")
    city_summary = (
        filtered_df.groupby('Location')
        .agg(
            Event_Count=('Disaster Type', 'count'),
            Total_Deaths=('Total Deaths', 'sum'),
            Most_Common_Disaster=('Disaster Type', lambda x: x.mode()[0] if not x.mode().empty else 'N/A')
        )
        .reset_index()
        .sort_values(by='Event_Count', ascending=False)
    )
    fig_bar = px.bar(
        city_summary,
        x='Location',
        y='Event_Count',
        color='Most_Common_Disaster',
        title="Number of Disasters per City",
        labels={'Event_Count': 'Number of Events', 'Location': 'City'},
        height=600
    )
    fig_bar.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_bar, use_container_width=True)

    st.subheader("Heatmap: Deaths by Year and Disaster Subgroup")
    heatmap_data = filtered_df.groupby(['Start Year', 'Disaster Subgroup'])['Total Deaths'].sum().reset_index()
    heatmap_pivot = heatmap_data.pivot(index='Disaster Subgroup', columns='Start Year', values='Total Deaths').fillna(0)
    fig_heatmap = px.imshow(
        heatmap_pivot,
        labels=dict(x="Year", y="Disaster Subgroup", color="Total Deaths"),
        title="Heatmap of Deaths by Year and Disaster Subgroup",
        aspect="auto"
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

    if 'Latitude' in filtered_df.columns and 'Longitude' in filtered_df.columns:
        st.subheader("Map: Disaster Locations")
        fig_map = px.scatter_mapbox(
            filtered_df,
            lat='Latitude',
            lon='Longitude',
            color='Disaster Type',
            size='Total Deaths',
            hover_name='Disaster Type',
            hover_data=['Start Year', 'Location', 'Total Deaths'],
            zoom=4,
            height=600
        )
        fig_map.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.info("No Latitude and Longitude columns available for map.")

    st.subheader("Filtered Data Table")
    st.dataframe(filtered_df)

    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "Download Filtered Data as CSV",
        data=csv,
        file_name='filtered_disasters.csv',
        mime='text/csv'
    )
else:
    st.warning("No data available for the selected filters. Adjust your filters and try again.")
