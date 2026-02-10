import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

class DonorModel:
    def __init__(self):
        self.model = None
        self.kmeans = None

    def load_data(self, filepath):
        """Loads and cleans the donor data."""
        try:
            df = pd.read_csv(filepath)
            # Basic cleaning
            df['DONOR_AGE'] = df['DONOR_AGE'].fillna(df['DONOR_AGE'].median())
            df['likely_donor'] = ((df['RECENT_AVG_GIFT_AMT'] > 10) & 
                                  (df['MONTHS_SINCE_LAST_GIFT'] < 18)).astype(int)
            return df
        except FileNotFoundError:
            raise FileNotFoundError("❌ Data file not found. Check path.")

    def train(self, df):
        """Trains the Random Forest model."""
        features = ['DONOR_AGE', 'LIFETIME_GIFT_AMOUNT', 'RECENT_RESPONSE_PROP', 
                    'MONTHS_SINCE_LAST_GIFT', 'MEDIAN_HOUSEHOLD_INCOME']
        
        X = df[features].fillna(0)
        y = df['likely_donor']
        
        # Train Model
        self.model = RandomForestClassifier(n_estimators=50, random_state=42)
        self.model.fit(X, y)
        
        # Add predictions to dataframe
        df['probability'] = self.model.predict_proba(X)[:, 1]
        return df

    def segment(self, df):
        """Clusters donors into 7 personas."""
        features = ['DONOR_AGE', 'LIFETIME_GIFT_AMOUNT', 'probability']
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(df[features].fillna(0))
        
        self.kmeans = KMeans(n_clusters=7, random_state=42)
        df['cluster'] = self.kmeans.fit_predict(X_scaled)
        return df
