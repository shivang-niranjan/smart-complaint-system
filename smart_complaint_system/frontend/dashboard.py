import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime

BACKEND_URL = "http://localhost:5000" 

st.set_page_config(layout="wide", page_title="Smart Complaint Dashboard")

st.title("🚨 Smart Complaint Prioritization Dashboard")

st.header("Submit a New Complaint")
with st.form("complaint_form"):
    description = st.text_area("Complaint Description", help="Describe the civic issue (e.g., 'No water supply in my area since morning.')")
    location = st.text_input("Location (Optional)", help="e.g., 'Ward 12, Pune' or 'Sector 21, Delhi'")
    submit_button = st.form_submit_button("Submit Complaint")

    if submit_button:
        if description:
            try:
                response = requests.post(f"{BACKEND_URL}/submit_complaint", json={
                    "description": description,
                    "location": location
                })
                if response.status_code == 201:
                    st.success("Complaint submitted successfully!")
                    st.json(response.json().get("complaint_details"))
                else:
                    st.error(f"Error submitting complaint: {response.status_code} - {response.text}")
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the backend API. Make sure it's running.")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
        else:
            st.warning("Please provide a complaint description.")

st.markdown("---")

st.header("Live Complaint Overview")

@st.cache_data(ttl=5) 
def get_all_complaints():
    try:
        response = requests.get(f"{BACKEND_URL}/get_complaints")
        if response.status_code == 200:
            return pd.DataFrame(response.json())
        else:
            st.error(f"Error fetching complaints: {response.status_code} - {response.text}")
            return pd.DataFrame()
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the backend API. Make sure it's running.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return pd.DataFrame()

complaints_df = get_all_complaints()

if not complaints_df.empty:
    complaints_df['date'] = pd.to_datetime(complaints_df['date'])

    st.subheader("Top 5 Most Urgent Complaints")
    critical_complaints = complaints_df.head(5)
    st.dataframe(critical_complaints[['complaint_id', 'description', 'category', 'severity', 'location', 'urgency_score', 'date', 'resolution_status']])

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Complaints", len(complaints_df))
    with col2:
        pending_complaints = complaints_df[complaints_df['resolution_status'] == 'Pending']
        st.metric("Pending Complaints", len(pending_complaints))
    with col3:
        avg_urgency = complaints_df['urgency_score'].mean()
        st.metric("Average Urgency Score", f"{avg_urgency:.1f}")

    st.markdown("---")

    st.subheader("Complaint Analytics")

    st.write("#### Complaints by Category")
    category_counts = complaints_df['category'].value_counts().reset_index()
    category_counts.columns = ['Category', 'Count']
    fig_category = px.bar(category_counts, x='Category', y='Count', title='Number of Complaints per Category')
    st.plotly_chart(fig_category, use_container_width=True)

    st.write("#### Complaints by Urgency Level")
    severity_order = ["Critical", "High", "Medium", "Low"]
    severity_counts = complaints_df['severity'].value_counts().reindex(severity_order).fillna(0).reset_index()
    severity_counts.columns = ['Severity', 'Count']
    fig_severity = px.bar(severity_counts, x='Severity', y='Count', title='Number of Complaints by Severity Level',
                            color='Severity', color_discrete_map={"Critical": "red", "High": "orange", "Medium": "yellow", "Low": "green"})
    st.plotly_chart(fig_severity, use_container_width=True)

    st.write("#### Complaints Over Time")
    complaints_df['date_only'] = complaints_df['date'].dt.date
    daily_counts = complaints_df['date_only'].value_counts().sort_index().reset_index()
    daily_counts.columns = ['Date', 'Count']
    fig_time = px.line(daily_counts, x='Date', y='Count', title='Daily Complaint Volume')
    st.plotly_chart(fig_time, use_container_width=True)

    st.write("#### Complaint Hotspots (Map Placeholder)")
    st.info("Full GIS integration would display complaints on a map. This is a placeholder.")

    st.subheader("All Complaints Data")
    st.dataframe(complaints_df.sort_values(by='urgency_score', ascending=False))

else:
    st.info("No complaints to display yet. Submit a complaint using the form above.")