import streamlit as st
st.set_page_config(layout="wide")

import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# -----------------------
# Data Loading and Caching
# -----------------------
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("/Users/hassaanulhaq/Library/Mobile Documents/com~apple~CloudDocs/spring_2025/transit_hackaton/divvyviz.github.io/data_files/202004-divvy-tripdata.csv")
        df['started_at'] = pd.to_datetime(df['started_at'])
        df['ended_at'] = pd.to_datetime(df['ended_at'])
        df['ride_duration'] = (df['ended_at'] - df['started_at']).dt.total_seconds() / 60
        df['start_hour'] = df['started_at'].dt.hour
        df['day_of_week'] = df['started_at'].dt.day_name()
        df['is_daytime'] = df['start_hour'].between(6, 18)
        # Create a route column early
        df['route'] = df['start_station_name'] + " → " + df['end_station_name']
        return df
    except Exception as e:
        st.error("Error loading data: " + str(e))
        return pd.DataFrame()

df = load_data()

# -----------------------
# Chart Functions with Caching and Error Reporting
# -----------------------
@st.cache_data
def get_fig_donut_total(filtered_df):
    try:
        trip_counts = filtered_df['member_casual'].value_counts().rename_axis('member_casual')\
                                          .reset_index(name='count')
        fig = px.pie(trip_counts, values='count', names='member_casual', hole=0.5,
                     title="Trip Distribution by User Type")
        return fig
    except Exception as e:
        st.error("Error in get_fig_donut_total: " + str(e))
        return None

@st.cache_data
def get_fig_donut_avg(filtered_df):
    try:
        avg_duration = filtered_df.groupby('member_casual')['ride_duration'].mean().reset_index()
        fig = px.pie(avg_duration, values='ride_duration', names='member_casual', hole=0.5,
                     title="Average Trip Duration by User Type")
        return fig
    except Exception as e:
        st.error("Error in get_fig_donut_avg: " + str(e))
        return None

@st.cache_data
def get_fig_day_night(filtered_df):
    try:
        day_night = filtered_df.groupby(['member_casual', 'is_daytime']).size()\
                               .reset_index(name='count')
        # Filter out groups with too few observations
        day_night = day_night[day_night['count'] > 10]
        fig = px.sunburst(day_night,
                          path=['member_casual', 'is_daytime'],
                          values='count',
                          title="Day vs Night Trips by User Type",
                          maxdepth=2)
        return fig
    except Exception as e:
        st.error("Error in get_fig_day_night: " + str(e))
        return None

# -----------------------
# Title and Global Filters
# -----------------------
st.title("🚲 Divvy Bike Trip Dashboard - April 2020")

col1, col2 = st.columns(2)
with col1:
    members = st.multiselect("Select User Types", df['member_casual'].unique(),
                               default=df['member_casual'].unique())
with col2:
    date_range = st.date_input("Select Date Range", [df['started_at'].min().date(),
                                                     df['started_at'].max().date()])

filtered_df = df[
    (df['member_casual'].isin(members)) &
    (df['started_at'].dt.date >= date_range[0]) &
    (df['started_at'].dt.date <= date_range[1])
]

# -----------------------
# Tabs Setup
# -----------------------
tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Patterns", "Durations", "Map"])

# Initialize session state flags for donut plots
if "donuts_loaded" not in st.session_state:
    st.session_state.donuts_loaded = False
if "donut_plots" not in st.session_state:
    st.session_state.donut_plots = {}

# -----------------------
# Tab1: Overview with Donut Plots
# -----------------------
with tab1:
    st.subheader("Overview")
    # Use a small sample to reduce computation time
    sample_df = filtered_df if len(filtered_df) < 1000 else filtered_df.sample(1000)

    # Load the donut plots on demand
    if st.button("Load Donut Plots", key="load_donuts") or st.session_state.donuts_loaded:
        if not st.session_state.donuts_loaded:
            with st.spinner("Generating donut plots..."):
                total_fig = get_fig_donut_total(sample_df)
                avg_fig = get_fig_donut_avg(sample_df)
                day_night_fig = get_fig_day_night(sample_df)
                st.session_state.donut_plots = {
                    "total": total_fig,
                    "avg": avg_fig,
                    "day_night": day_night_fig,
                }
                st.session_state.donuts_loaded = True

        col1, col2, col3 = st.columns(3)
        if st.session_state.donut_plots.get("total"):
            col1.plotly_chart(st.session_state.donut_plots["total"], use_container_width=True)
        if st.session_state.donut_plots.get("avg"):
            col2.plotly_chart(st.session_state.donut_plots["avg"], use_container_width=True)
        if st.session_state.donut_plots.get("day_night"):
            col3.plotly_chart(st.session_state.donut_plots["day_night"], use_container_width=True)
    else:
        st.info("Click the button above to load the donut plots.")

# -----------------------
# Tab2: Patterns (Weekly and Hourly)
# -----------------------
with tab2:
    st.subheader("Weekly Ride Patterns")
    try:
        dow = filtered_df.groupby(['day_of_week', 'member_casual']).size().reset_index(name='count')
        dow['day_of_week'] = pd.Categorical(dow['day_of_week'],
                                            categories=['Monday', 'Tuesday', 'Wednesday', 'Thursday',
                                                        'Friday', 'Saturday', 'Sunday'],
                                            ordered=True)
        dow = dow.sort_values('day_of_week')
        fig_dow = px.bar(dow, x='day_of_week', y='count', color='member_casual',
                         barmode='group', title="Rides by Day of Week")
        st.plotly_chart(fig_dow, use_container_width=True)
    except Exception as e:
        st.error("Error in Weekly Ride Patterns: " + str(e))

    st.subheader("Hourly Ride Pattern by User Type")
    try:
        hourly = filtered_df.groupby(['start_hour', 'member_casual']).size()\
                            .reset_index(name='count')
        fig_hourly = px.line(hourly, x='start_hour', y='count', color='member_casual',
                             markers=True, title="Hourly Ride Trends")
        st.plotly_chart(fig_hourly, use_container_width=True)
    except Exception as e:
        st.error("Error in Hourly Ride Trends: " + str(e))

# -----------------------
# Tab3: Durations and Routes
# -----------------------
with tab3:
    st.subheader("Trip Duration Density (Under 2 Hours)")
    try:
        fig_density = px.violin(filtered_df[filtered_df['ride_duration'] < 120],
                                x='member_casual', y='ride_duration', box=True,
                                points='all', title="Trip Duration under 2 Hours")
        st.plotly_chart(fig_density, use_container_width=True)
    except Exception as e:
        st.error("Error in Trip Duration Density: " + str(e))
    
    st.subheader("Trip Duration by Day vs Night")
    try:
        day_night_avg = filtered_df.groupby(['member_casual', 'is_daytime'])['ride_duration']\
                                   .mean().reset_index()
        day_night_avg['time_of_day'] = day_night_avg['is_daytime'].replace({True: "Day", False: "Night"})
        fig_daynight_avg = px.bar(day_night_avg, x='member_casual', y='ride_duration',
                                  color='time_of_day', barmode='group',
                                  title="Avg. Trip Duration: Day vs Night")
        st.plotly_chart(fig_daynight_avg, use_container_width=True)
    except Exception as e:
        st.error("Error in Trip Duration by Day vs Night: " + str(e))
    
    st.subheader("Top 15 Most Popular Routes")
    try:
        route_counts = filtered_df['route'].value_counts().head(15).reset_index()
        route_counts.columns = ['Route', 'Count']
        st.dataframe(route_counts)
    except Exception as e:
        st.error("Error in Top 15 Routes: " + str(e))

# -----------------------
# Tab4: Map of Start Locations
# -----------------------
with tab4:
    st.subheader("Map of Start Locations")
    try:
        map_data = filtered_df[['start_lat', 'start_lng']]\
                            .dropna()\
                            .rename(columns={'start_lat': 'lat', 'start_lng': 'lon'})
        if len(map_data) > 1000:
            map_data = map_data.sample(1000)
        st.map(map_data)
    except Exception as e:
        st.error("Error in Map: " + str(e))