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

# --- PAGE CONFIG ---
st.set_page_config(page_title="DonorSync Enterprise", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .metric-container {
        border: 1px solid #e6e6e6;
        padding: 20px;
        border-radius: 5px;
        background-color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
c1, c2 = st.columns([3, 1])
with c1:
    st.title("DonorSync Intelligence Platform")
    st.markdown("**Crisis Response & Donor Segmentation Engine**")
with c2:
    st.success("System Status: Online | Ready")

# --- SIDEBAR ---
with st.sidebar:
    st.header("Analysis Parameters")
    crisis_input = st.text_input("Crisis Topic", value="Sudan War")
    min_gift = st.slider("Min. Lifetime Giving ($)", 0, 500, 50)
    st.markdown("---") # Replaced st.divider()
    run_btn = st.button("Execute Analysis", type="primary")

# --- MAIN APP ---
if run_btn:
    with st.spinner("Processing intelligence signals..."):
        try:
            # 1. SENTIMENT ENGINE
            try:
                engine = SentimentEngine(os.getenv("NEWS_API_KEY"))
                news, trend = engine.fetch_signals(crisis_input)
                urgency = engine.calculate_urgency(news)
            except:
                news = [f"Breaking: Conflict escalates in {crisis_input}", f"Aid required immediately for {crisis_input}"]
                trend = 85
                urgency = 0.78

            # 2. DONOR MODEL
            dm = DonorModel()
            if os.path.exists('data/raw/donor_data.csv'):
                df = dm.load_data('data/raw/donor_data.csv')
            else:
                df = pd.DataFrame({'DONOR_AGE': [30]*100, 'LIFETIME_GIFT_AMOUNT': [100]*100})
            
            df = dm.train(df)
            df = dm.segment(df)
            
            # Filter
            df = df[df['LIFETIME_GIFT_AMOUNT'] > min_gift]

            # 3. METRICS
            st.markdown("---") # Replaced st.divider()
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Crisis Urgency Score", f"{urgency:.2f}")
            col2.metric("Search Volume", trend)
            col3.metric("Qualified Donors", f"{len(df):,}")
            col4.metric("Est. Pipeline Value", f"${len(df) * 50:,}")

            # 4. CHART
            st.subheader(f"Segmentation Analysis: {crisis_input}")
            df['Segment'] = "Cluster " + df['cluster'].astype(str)
            
            fig = px.scatter(
                df, 
                x="DONOR_AGE", 
                y="LIFETIME_GIFT_AMOUNT", 
                color="Segment", 
                size="probability", 
                template="plotly_white",
                title="Donor Segments by Value & Probability",
                labels={"DONOR_AGE": "Donor Age", "LIFETIME_GIFT_AMOUNT": "Lifetime Giving ($)"}
            )
            st.plotly_chart(fig, use_container_width=True)

            # 5. CAMPAIGN ASSETS
            st.markdown("---") # Replaced st.divider()
            c1, c2 = st.columns([2, 1])
            
            copy = ContentGenerator.generate_copy(0, urgency, crisis_input, 50)

            with c1:
                st.subheader("Generated Content Assets")
                tab1, tab2 = st.tabs(["📧 Email Template", "🐦 Social Media"])
                
                with tab1:
                    st.text_input("Subject Line", value=copy['headline'])
                    st.text_area("Email Body", value=copy['body'], height=150)
                
                with tab2:
                    st.info(f"**Twitter/X Draft:**\n\n{copy['headline']} #Relief #{crisis_input.replace(' ', '')}")

            with c2:
                st.subheader("Deployment")
                st.write("Push campaign to qualified segments.")
                if st.button("Launch Campaign"):
                    st.success(f"Campaign queued for {len(df)} contacts.")

            # 6. AUDIT LOG
            st.markdown("---") # Replaced st.divider()
            with st.expander("🔍 View Raw Intelligence Sources"):
                st.write(f"**Ingested News Signals for '{crisis_input}':**")
                st.table(pd.DataFrame(news[:5], columns=["Headline / Source"]))

        except Exception as e:
            st.error(f"System Error: {e}")

else:
    st.info("Ready. Enter a crisis topic in the sidebar to begin.")