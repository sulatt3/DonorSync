import streamlit as st
import os
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
from src.sentiment_engine import SentimentEngine
from src.donor_model import DonorModel
from src.content_generator import ContentGenerator

# Load environment variables
load_dotenv()

st.set_page_config(page_title="DonorSync", layout="wide")
st.title("DonorSync: Crisis Command Center")

# --- SIDEBAR ---
with st.sidebar:
    st.header("Crisis Simulation")
    crisis_input = st.text_input("Crisis Topic", "Myanmar earthquake")
    run_btn = st.button("Run Analysis", type="primary")

# --- MAIN APP ---
if run_btn:
    with st.spinner(f"Analyzing Global Signals for '{crisis_input}'..."):
        
        # 1. SENTIMENT ENGINE
        try:
            # Initialize engine (API key is optional for demo simulation)
            engine = SentimentEngine(os.getenv("NEWS_API_KEY"))
            news, trend = engine.fetch_signals(crisis_input)
            urgency = engine.calculate_urgency(news)
        except Exception as e:
            st.warning(f"API Limit or Error. Using simulation mode. ({e})")
            news = [f"Breaking: {crisis_input} causes major damage...", f"Urgent relief needed for {crisis_input} victims."]
            trend = 85
            urgency = 0.88
        
        # 2. METRICS ROW
        col1, col2 = st.columns(2)
        col1.metric("Urgency Score", f"{urgency:.2f}", delta="High Risk" if urgency > 0.6 else "Normal", delta_color="inverse")
        col2.metric("Search Interest", trend, "+15% vs yesterday")
        
        # 3. DONOR MODEL
        try:
            dm = DonorModel()
            # Check if CSV exists
            if os.path.exists('data/raw/donor_data.csv'):
                df = dm.load_data('data/raw/donor_data.csv')
            else:
                st.warning("'donor_data.csv' not found in data/raw/. Generating dummy data.")
                # Create dummy data for demo
                df = pd.DataFrame({
                    'DONOR_AGE': [25, 40, 60, 30, 50] * 20,
                    'LIFETIME_GIFT_AMOUNT': [100, 5000, 200, 50, 1000] * 20,
                    'RECENT_AVG_GIFT_AMT': [10, 50, 20, 5, 10] * 20,
                    'MONTHS_SINCE_LAST_GIFT': [1, 12, 24, 2, 6] * 20,
                    'RECENT_RESPONSE_PROP': [0.1, 0.5, 0.2, 0.1, 0.4] * 20,
                    'MEDIAN_HOUSEHOLD_INCOME': [50000] * 100
                })

            # Train and Segment
            df = dm.train(df)
            df = dm.segment(df)
            
            # 4. VISUALIZATION
            st.divider()
            st.subheader("Donor Segmentation Map")
            fig = px.scatter(
                df, 
                x="DONOR_AGE", 
                y="LIFETIME_GIFT_AMOUNT", 
                color="cluster", 
                size="probability", 
                hover_data=["likely_donor"],
                title="Identifying High-Value 'Crisis Responder' Clusters"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # 5. CONTENT GENERATION
            st.divider()
            st.subheader("AI Campaign Generator")
            
            # Generate copy for the best cluster (Cluster 0 as example)
            copy = ContentGenerator.generate_copy(0, urgency, crisis_input, 50)
            
            c1, c2 = st.columns(2)
            with c1:
                st.info(f"**HEADLINE:** {copy['headline']}")
                st.write(copy['body'])
            with c2:
                st.success(f"**SUGGESTED ASK:** {copy['ask']}")
                st.button("Deploy to Social Media")

        except Exception as e:
            st.error(f"Error in data model: {e}")

else:
    st.info("👈 Enter a crisis topic in the sidebar and click 'Run Analysis' to start.")
