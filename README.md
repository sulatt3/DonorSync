# DonorSync: AI-Driven Crisis Response Intelligence

**DonorSync** is a predictive intelligence engine designed to help non-profits react instantly to global crises. By bridging real-time external signals (NewsAPI, Google Trends) with internal donor data, it identifies the right segment of supporters to engage during critical windows of opportunity.

## The Problem
When a disaster strikes—such as an earthquake or humanitarian crisis—non-profits often lose valuable time deciding who to contact and how to frame the ask. Generic, "one-size-fits-all" appeals can lead to donor fatigue and missed fundraising targets during the moments that matter most.

## The Solution
DonorSync automates the decision matrix for crisis fundraising:
1.  **Monitors** global news for high-urgency keywords.
2.  **Calculates** a "Crisis Urgency Score" using sentiment analysis.
3.  **Segments** the donor database into behavioral personas using unsupervised learning.
4.  **Drafts** targeted, urgency-adjusted campaign copy automatically.

## Technical Architecture

### 1. Signal Detection (External Intelligence)
* **NewsAPI & Google Trends:** Fetches real-time articles and search volume indices.
* **Sentiment Engine:** Utilizes Hugging Face Transformers (`distilbert`) to score the severity of news clusters.

### 2. Donor Modeling (Internal Intelligence)
* **Predictive Classification:** A Random Forest model scores donors on their likelihood to give based on RFM (Recency, Frequency, Monetary) features.
* **Behavioral Clustering:** K-Means clustering groups donors into 7 distinct personas (e.g., "High-Value Crisis Responders," "Lapsed Occasional Donors").

### 3. Actionable Output
* **Dynamic Content Generation:** The system outputs tailored fundraising copy (Tweets, Emails) matched to the specific crisis intensity and donor persona.

## Installation & Usage

### Setup
1.  Clone the repository:
    ```bash
    git clone [https://github.com/sulatt3/DonorSync.git](https://github.com/sulatt3/DonorSync.git)
    ```
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Running the Dashboard
Launch the interactive command center:
```bash
streamlit run app.py
