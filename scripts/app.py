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
        df = pd.read_csv("data_files/202004-divvy-tripdata.csv")
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
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Overview", "Patterns", "Durations", "Map", "Demand Prediction"])

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
    # Use a small sample to reduce computation time if necessary
    sample_df = filtered_df if len(filtered_df) < 1000 else filtered_df.sample(1000)
    
    # Directly compute the donut plots
    total_fig = get_fig_donut_total(sample_df)
    avg_fig = get_fig_donut_avg(sample_df)
    day_night_fig = get_fig_day_night(sample_df)
    
    col1, col2, col3 = st.columns(3)
    if total_fig:
        col1.plotly_chart(total_fig, use_container_width=True)
    if avg_fig:
        col2.plotly_chart(avg_fig, use_container_width=True)
    if day_night_fig:
        col3.plotly_chart(day_night_fig, use_container_width=True)

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
    st.title("Trip Durations and Routes")
    
    # Use a smaller subset for heavy computations if necessary
    dur_df = filtered_df if len(filtered_df) < 5000 else filtered_df.sample(5000)
    
    # -------- Row 1: Two Columns (Histogram | Average Duration) --------
    row1_col1, row1_col2 = st.columns(2)
    
    with row1_col1:
        st.subheader("Trip Duration Distribution (Histogram)")
        try:
            df_hist = dur_df[dur_df['ride_duration'] <= 120].copy()
            df_hist['trip_duration_min'] = df_hist['ride_duration']
            fig_hist = px.histogram(
                df_hist,
                x='trip_duration_min',
                color='member_casual',
                nbins=30,
                opacity=0.7,
                barmode='overlay',
                title='Trip Duration Distribution: Members vs. Casual Riders',
                labels={'trip_duration_min': 'Trip Duration (minutes)', 'count': 'Number of Trips'},
                color_discrete_map={'member': '#1F77B4', 'casual': '#FF7F0E'}
            )
            fig_hist.update_layout(
                plot_bgcolor='white',
                legend_title='User Type',
                xaxis_title='Trip Duration (minutes)',
                yaxis_title='Number of Trips',
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
                height=300,
                margin=dict(l=20, r=20, t=50, b=20)
            )
            st.plotly_chart(fig_hist, use_container_width=True)
        except Exception as e:
            st.error("Error in Trip Duration Histogram: " + str(e))
    
    with row1_col2:
        st.subheader("Average Trip Duration: Day vs. Night")
        try:
            # Recalculate necessary columns on the full df
            df['trip_duration_min'] = (df['ended_at'] - df['started_at']).dt.total_seconds() / 60
            df['hour'] = df['started_at'].dt.hour
            df['time_of_day'] = df['hour'].apply(
                lambda x: 'Day (6am-6pm)' if 6 <= x < 18 else 'Night (6pm-6am)'
            )
            temp_df = df[df['trip_duration_min'] <= 180]  # Remove extreme outliers
            avg_duration = temp_df.groupby(['time_of_day', 'member_casual'])['trip_duration_min'].agg(
                ['mean', 'median', 'count', 'std']
            ).reset_index()
            avg_duration['mean'] = avg_duration['mean'].round(1)
            avg_duration['median'] = avg_duration['median'].round(1)
            
            fig_avg = px.bar(
                avg_duration,
                x='time_of_day',
                y='mean',
                color='member_casual',
                barmode='group',
                title='Average Trip Duration: Day vs. Night',
                labels={
                    'mean': 'Average Duration (minutes)', 
                    'time_of_day': 'Time of Day', 
                    'member_casual': 'User Type'
                },
                color_discrete_map={'member': '#1F77B4', 'casual': '#FF7F0E'},
                text='mean'
            )
            fig_avg.update_traces(textposition='outside')
            fig_avg.update_layout(
                plot_bgcolor='white',
                legend_title='User Type',
                xaxis_title='Time of Day',
                yaxis_title='Average Trip Duration (minutes)',
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
                height=300,
                margin=dict(l=20, r=20, t=50, b=20)
            )
            st.plotly_chart(fig_avg, use_container_width=True)
        except Exception as e:
            st.error("Error in Average Trip Duration: " + str(e))
    
    # -------- Row 2: Two Columns (Top Routes | Day/Night Rides Distribution) --------
    row2_col1, row2_col2 = st.columns(2)
    
    with row2_col1:
        st.subheader("Top 15 Routes (Bar Chart)")
        try:
            route_counts = dur_df.groupby(['start_station_name', 'end_station_name']).size().reset_index(name='count')
            top_routes = route_counts.sort_values('count', ascending=False).head(15)
            top_routes['route'] = top_routes['start_station_name'] + " → " + top_routes['end_station_name']
            fig_route = px.bar(
                top_routes,
                y='route',
                x='count',
                orientation='h',
                title='Top 15 Most Popular Divvy Routes',
                labels={'count': 'Number of Trips', 'route': 'Route'},
                color='count',
                color_continuous_scale='Blues'
            )
            fig_route.update_layout(
                plot_bgcolor='white',
                yaxis={'categoryorder': 'total ascending'},
                height=300,
                yaxis_title='',
                xaxis_title='Number of Trips',
                margin=dict(l=20, r=20, t=50, b=20)
            )
            st.plotly_chart(fig_route, use_container_width=True)
        except Exception as e:
            st.error("Error in Top 15 Routes (Bar Chart): " + str(e))
    
    with row2_col2:
        st.subheader("Day vs. Night Rides Distribution")
        try:
            temp_df = dur_df.copy()
            temp_df['hour'] = temp_df['started_at'].dt.hour
            temp_df['time_of_day'] = temp_df['hour'].apply(lambda x: 'Day' if 6 <= x < 18 else 'Night')
            
            day_night_counts = temp_df.groupby(['time_of_day', 'member_casual']).size().reset_index(name='rides')
            total_rides = day_night_counts.groupby('member_casual')['rides'].sum().reset_index()
            day_night_counts = day_night_counts.merge(total_rides, on='member_casual', suffixes=('', '_total'))
            day_night_counts['percentage'] = (day_night_counts['rides'] / day_night_counts['rides_total'] * 100).round(1)
            
            fig_dn = px.bar(
                day_night_counts, 
                x='time_of_day', 
                y='rides', 
                color='member_casual',
                barmode='group',
                title='Day vs. Night Rides: Members vs. Casual Riders',
                labels={'rides': 'Number of Rides', 'time_of_day': 'Time of Day', 'member_casual': 'User Type'},
                color_discrete_map={'member': '#1F77B4', 'casual': '#FF7F0E'},
                text='percentage',
                custom_data=['percentage']
            )
            fig_dn.update_traces(
                texttemplate='%{customdata[0]}%', 
                textposition='outside'
            )
            fig_dn.update_layout(
                plot_bgcolor='white',
                legend_title='User Type',
                xaxis_title='Time of Day',
                yaxis_title='Number of Rides',
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
                height=300,
                margin=dict(l=20, r=20, t=50, b=20)
            )
            st.plotly_chart(fig_dn, use_container_width=True)
        except Exception as e:
            st.error("Error in Day vs. Night Rides: " + str(e))
    
    # -------- Full-Width Row: Boxplot --------
    st.subheader("Trip Duration Distribution (Boxplot): Day vs. Night")
    try:
        temp_df = dur_df.copy()
        temp_df['trip_duration_min'] = (temp_df['ended_at'] - temp_df['started_at']).dt.total_seconds() / 60
        temp_df['hour'] = temp_df['started_at'].dt.hour
        temp_df['time_of_day'] = temp_df['hour'].apply(
            lambda x: 'Day (6am-6pm)' if 6 <= x < 18 else 'Night (6pm-6am)'
        )
        temp_df = temp_df[temp_df['trip_duration_min'] <= 180]
        
        fig_box = px.box(
            temp_df,
            x='time_of_day',
            y='trip_duration_min',
            color='member_casual',
            title='Trip Duration Distribution: Day vs. Night',
            points="outliers",
            labels={
                'trip_duration_min': 'Trip Duration (minutes)', 
                'time_of_day': 'Time of Day', 
                'member_casual': 'User Type'
            },
            color_discrete_map={'member': '#1F77B4', 'casual': '#FF7F0E'}
        )
        
        fig_box.update_layout(
            plot_bgcolor='white',
            legend_title='User Type',
            xaxis_title='Time of Day',
            yaxis_title='Trip Duration (minutes)',
            boxmode='group',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            height=300,
            margin=dict(l=20, r=20, t=50, b=20)
        )
        
        st.plotly_chart(fig_box, use_container_width=True)
    except Exception as e:
        st.error("Error in Trip Duration Boxplot: " + str(e))
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

# -----------------------
# Tab5: Demand Prediction
# -----------------------
with tab5:
    from PIL import Image
    st.title("Demand Prediction")
    image_a = Image.open("/Users/hassaanulhaq/Library/Mobile Documents/com~apple~CloudDocs/spring_2025/transit_hackaton/divvyviz.github.io/scripts/a.png")
    st.image(image_a, caption="Demand Prediction Model")
    image_b = Image.open("/Users/hassaanulhaq/Library/Mobile Documents/com~apple~CloudDocs/spring_2025/transit_hackaton/divvyviz.github.io/scripts/b.jpeg")
    st.image(image_b, caption="Future Prediction")