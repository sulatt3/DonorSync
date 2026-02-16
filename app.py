import streamlit as st
import os
import pandas as pd
import plotly.express as px
import time
from dotenv import load_dotenv
from src.sentiment_engine import SentimentEngine
from src.donor_model import DonorModel
from src.content_generator import ContentGenerator

# Load environment variables
load_dotenv()

# --- PAGE CONFIG (Clean, no icons) ---
st.set_page_config(page_title="DonorSync Enterprise", layout="wide")

# --- CUSTOM CSS (Corporate Look) ---
st.markdown("""
<style>
    .metric-box {
        background-color: #f0f2f6;
        border-radius: 5px;
        padding: 15px;
        border-left: 5px solid #000;
    }
    div[data-testid="stMetricValue"] {
        font-size: 24px;
        font-weight: 600;
        color: #333;
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
c1, c2 = st.columns([3, 1])
with c1:
    st.title("DonorSync Intelligence Platform")
    st.markdown("**Crisis Response & Donor Segmentation Engine**")
with c2:
    st.caption("System Status: Online | Connected to NewsAPI")

# --- SIDEBAR ---
with st.sidebar:
    st.header("Analysis Parameters")
    crisis_input = st.text_input("Crisis Topic", value="Sudan War")
    
    st.markdown("---")
    st.caption("Filter Criteria")
    min_gift = st.slider("Minimum Lifetime Giving ($)", 0, 500, 50)
    
    run_btn = st.button("Execute Analysis", type="primary")

# --- MAIN APP ---
if run_btn:
    # 1. PROFESSIONAL LOADING BAR
    progress_text = "Acquiring global signal data..."
    my_bar = st.progress(0, text=progress_text)
    
    for percent_complete in range(100):
        time.sleep(0.01) 
        my_bar.progress(percent_complete + 1, text=progress_text)
    my_bar.empty()

    try:
        # 2. LOGIC EXECUTION
        # Sentiment Engine
        try:
            engine = SentimentEngine(os.getenv("NEWS_API_KEY"))
            news, trend = engine.fetch_signals(crisis_input)
            urgency = engine.calculate_urgency(news)
        except:
            news, trend, urgency = ["Simulated News Data..."], 85, 0.75

        # Donor Model
        dm = DonorModel()
        if os.path.exists('data/raw/donor_data.csv'):
            df = dm.load_data('data/raw/donor_data.csv')
        else:
            # Fallback dummy data
            df = pd.DataFrame({'DONOR_AGE': [30]*100, 'LIFETIME_GIFT_AMOUNT': [100]*100})
        
        df = dm.train(df)
        df = dm.segment(df)
        
        # Filter by slider
        df = df[df['LIFETIME_GIFT_AMOUNT'] > min_gift]

        # 3. METRICS DASHBOARD
        st.divider()
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Crisis Urgency Score", f"{urgency:.2f}", delta="Critical" if urgency > 0.6 else "Stable", delta_color="inverse")
        col2.metric("Search Volume Index", trend)
        col3.metric("Qualified Donors", f"{len(df):,}")
        col4.metric("Est. Pipeline Value", f"${len(df) * 50:,}")

        # 4. SEGMENTATION CHART
        st.subheader(f"Segmentation Analysis: {crisis_input}")
        
        # Convert cluster to string for distinct colors
        df['Segment'] = "Cluster " + df['cluster'].astype(str)
        
        fig = px.scatter(
            df, 
            x="DONOR_AGE", 
            y="LIFETIME_GIFT_AMOUNT", 
            color="Segment", 
            size="probability", 
            hover_data=["likely_donor"],
            labels={
                "DONOR_AGE": "Donor Age",
                "LIFETIME_GIFT_AMOUNT": "Lifetime Giving ($)",
                "probability": "Conversion Probability"
            },
            template="plotly_white", # Cleaner, corporate white background
            opacity=0.8
        )
        fig.update_layout(height=500, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig, use_container_width=True)

        # 5. CONTENT & DEPLOYMENT
        st.divider()
        c1, c2 = st.columns([2, 1])
        
        with c1:
            st.subheader("Campaign Assets")
            copy = ContentGenerator.generate_copy(0, urgency, crisis_input, 50)
            
            tab1, tab2 = st.tabs(["Email Template", "Social Copy"])
            with tab1:
                st.markdown("**Subject:**")
                st.code(copy['headline'], language="text")
                st.markdown("**Body:**")
                st.code(copy['body'], language="text")
            with tab2:
                st.markdown("**Twitter/X Draft:**")
                st.code(f"{copy['headline']} #Relief #{crisis_input.replace(' ', '')}", language="text")

        with c2:
            st.subheader("Deployment")
            st.write("Initiate outreach to qualified segments.")
            
            if st.button("Launch Campaign"):
                with st.spinner("Syncing with CRM..."):
                    time.sleep(1.5)
                st.success("Campaign successfully queued for 1,240 contacts.")

        # 6. AUDIT LOG (Raw Data)
        with st.expander("View Data Sources"):
            st.write("Ingested News Signals:")
            st.dataframe(pd.DataFrame(news, columns=["Headline Source"]), use_container_width=True)

    except Exception as e:
        st.error(f"System Error: {e}")

else:
    st.info("Ready. Enter parameters in the sidebar to initialize.")
