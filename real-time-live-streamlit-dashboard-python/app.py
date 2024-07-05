import streamlit as st
import numpy as np
import pandas as pd
import time
import plotly.express as px
from azure.eventhub import EventHubConsumerClient
import json
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# Event Hub Connection String
connection_str = os.getenv("EVENT_HUB_CONNECTION_STR")
consumer_group = os.getenv("STREAMLIT_CONS_GROUP")
eventhub_name = os.getenv("METRIC_EVENT_HUB_NAME")

real_time_data = []

st.set_page_config(page_title="Real-Time Glucose Monitoring Dashboard", layout="wide")

# Placeholder for Streamlit components
placeholder = st.empty()

# Define a function for consistent header styling
def create_styled_header(text, color):
    return f"""
    <h2 style='text-align: center; color: {color}; padding: 10px; 
               background-color: #f0f0f0; border-radius: 5px; margin: 20px 0;'>
        {text}
    </h2>
    """

def on_event(partition_context, event):
    """
    Callback function that is called whenever an event is received from the Event Hub
    Args:
        partition_context (PartitionContext): Context of the partition
        event (EventData): Event data received from the Event Hub
    Returns:
        None
    """
    event_data = json.loads(event.body_as_str())
    real_time_data.append(event_data)
    df = pd.DataFrame(real_time_data)

    # Converting 'timestamp' to datetime and sort the DataFrame
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values(by="timestamp")

    # Metric Calculations That Will Be Displayed on the Dashboard
    avg_glucose = df["glucose_reading"].mean()
    unique_users = df["user_id"].nunique()
    unique_devices = df["device_id"].nunique()
    high_critical_readings_count = df[df["glucose_reading"] > 200].shape[0]
    low_critical_readings_count = df[df["glucose_reading"] < 55].shape[0]

    with placeholder.container():
        # Displaying the Important Metrics
        st.markdown(create_styled_header("📊 Glucose Monitoring Overview 📊", "#1E90FF"), unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Average Glucose Reading", f"{avg_glucose:.2f} mg/dL")
            st.metric("Unique Users", unique_users)
        with col2:
            st.metric("Unique Devices", unique_devices)
            st.metric("Critical Readings High", high_critical_readings_count, "Above 200 mg/dL")
        with col3:
            st.metric("Critical Readings Low", low_critical_readings_count, "Below 55 mg/dL")

        # Time Series Plot
        st.markdown(create_styled_header("📈 Glucose Readings Over Time 📈", "#32CD32"), unsafe_allow_html=True)
        fig1 = px.line(df, x="timestamp", y="glucose_reading")
        st.plotly_chart(fig1, use_container_width=True)

        # Assigning color based on glucose reading
        # Red: Above 200, Orange: Below 55, Blue: Normal
        df["color"] = df.apply(
            lambda x: "red"
            if x["glucose_reading"] > 200
            else ("orange" if x["glucose_reading"] < 55 else "blue"),
            axis=1,
        )

        # Description of the color being displayed on the map
        color_scale = {
            "red": "Users With Glucose Level Too High",
            "orange": "Users With Glucose Level Too Low",
            "blue": "Users In Normal Range"
        }

        # Geographical Map
        st.markdown(create_styled_header("🗺️ User Locations by Glucose Level Status 🗺️", "#FF69B4"), unsafe_allow_html=True)

        fig2 = px.scatter_geo(
            df,
            lat="latitude",
            lon="longitude",
            color="color",
            color_discrete_map={"red": "red", "orange": "orange", "blue": "blue"},
            labels={"color": "Glucose Level Status"}
        )

        fig2.update_layout(
            legend_title_text='Glucose Level Status',
            legend=dict(
                orientation="h",  
                yanchor="bottom",
                y=1.02, 
                xanchor="center",
                x=0.5  
            ),
            # Center the map
            geo=dict(
                center=dict(
                    lat=df['latitude'].mean(),
                    lon=df['longitude'].mean()
                ),
                projection_scale=4  # Adjust this value to zoom in/out
            )
        )

        # To ensure the markers are visible
        fig2.update_traces(marker=dict(size=10))

        # Mapping the color to category
        fig2.for_each_trace(lambda t: t.update(name=color_scale[t.name]))

        st.plotly_chart(fig2, use_container_width=True)

        # Glucose Reading Distribution
        st.markdown(create_styled_header("📊 Distribution of Glucose Readings 📊", "#FFA500"), unsafe_allow_html=True)
        fig3 = px.histogram(df, x="glucose_reading")
        st.plotly_chart(fig3, use_container_width=True)

        # A Display DataFrames for critical readings
        st.markdown(create_styled_header("⚠️ Critical Readings ⚠️", "#DC143C"), unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<h3 style='text-align: center; color: #FF4500;'>Users with Readings Above 200 mg/dL</h3>", unsafe_allow_html=True)
            st.markdown(
                df[df["glucose_reading"] > 200].to_html(index=False),
                unsafe_allow_html=True
            )
        with col2:
            st.markdown("<h3 style='text-align: center; color: #FF4500;'>Users with Readings Below 55 mg/dL</h3>", unsafe_allow_html=True)
            st.markdown(
                df[df["glucose_reading"] < 55].to_html(index=False),
                unsafe_allow_html=True
            )

        # Raw Data and Statistical Analysis
        st.markdown(create_styled_header("📊 Raw Data and Statistical Analysis 📊", "#4B0082"), unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Statistical Summary")
            st.write(df[["glucose_reading"]].describe())
        
        with col2:
            st.subheader("Raw Data")
            st.dataframe(df)

       
        
# Setup for Streamlit Dashboard
st.markdown("""
    <h1 style='text-align: center; color: #FF4B4B; padding: 20px; 
               background-color: #f0f0f0; border-radius: 10px; margin-bottom: 30px;'>
        🩸 Real-Time Glucose Monitoring Dashboard 🩸
    </h1>
    """, unsafe_allow_html=True)

# Event Hub Connection
client = EventHubConsumerClient.from_connection_string(
    conn_str=connection_str, consumer_group=consumer_group, eventhub_name=eventhub_name
)

# Starting the Event Hub client
with client:
    print("Starting Event Hub Client")
    client.receive(on_event=on_event, starting_position="-1")