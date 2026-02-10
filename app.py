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

st.set_page_config(page_title="DonorSync Dashboard", layout="wide")
st.title("DonorSync Command Center")
st.markdown("### Real-Time Crisis Intelligence & Donor Response System")

# --- SIDEBAR ---
with st.sidebar:
    st.header("Configuration")
    st.write("Enter a crisis topic below to generate intelligence.")
    crisis_input = st.text_input("Crisis Topic", value="Myanmar earthquake")
    run_btn = st.button("Run Analysis", type="primary")

# --- MAIN APP ---
if run_btn:
    with st.spinner(f"Processing intelligence signals for '{crisis_input}'..."):
        
        # 1. SENTIMENT ENGINE
        try:
            # Initialize engine (API key is optional for demo simulation)
            engine = SentimentEngine(os.getenv("NEWS_API_KEY"))
            news, trend = engine.fetch_signals(crisis_input)
            urgency = engine.calculate_urgency(news)
        except Exception as e:
            # Simulation Mode (Dynamic to your input)
            st.info(f"Note: Running in simulation mode. Analyzing '{crisis_input}'.")
            news = [f"Breaking news regarding {crisis_input}...", f"Urgent relief needed for {crisis_input}."]
            trend = 85
            urgency = 0.88
        
        # 2. METRICS ROW
        st.divider()
        col1, col2, col3 = st.columns(3)
        col1.metric("Urgency Score (0-1.0)", f"{urgency:.2f}")
        col2.metric("Search Interest Index", trend)
        col3.metric("Projected Donor Match", "High Confidence")
        
        # 3. DONOR MODEL
        try:
            dm = DonorModel()
            # Check if CSV exists
            if os.path.exists('data/raw/donor_data.csv'):
                df = dm.load_data('data/raw/donor_data.csv')
            else:
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
            st.subheader("Donor Segmentation Analysis")
            fig = px.scatter(
                df, 
                x="DONOR_AGE", 
                y="LIFETIME_GIFT_AMOUNT", 
                color="cluster", 
                size="probability", 
                hover_data=["likely_donor"],
                title=f"High-Value Segments for: {crisis_input}"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # 5. CONTENT GENERATION
            st.divider()
            st.subheader("Automated Campaign Content")
            
            # Generate copy for the best cluster
            copy = ContentGenerator.generate_copy(0, urgency, crisis_input, 50)
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Generated Headline:**")
                st.info(copy['headline'])
                st.markdown("**Email/Social Body:**")
                st.write(copy['body'])
            with c2:
                st.markdown("**Suggested Ask Amount:**")
                st.success(copy['ask'])
                st.button("Deploy to Channels")

        except Exception as e:
            st.error(f"System Error: {e}")

else:
    st.info("Please enter a crisis topic in the sidebar and click 'Run Analysis'.")
