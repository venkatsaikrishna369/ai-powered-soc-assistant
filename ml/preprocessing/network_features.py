import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib
import warnings
warnings.filterwarnings('ignore')

class FastFeatureEngineer:
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.selected_features = None
        
    def prepare_features(self, df: pd.DataFrame, is_training: bool = True) -> pd.DataFrame:
        """Quick feature engineering for network security data"""
        df_processed = df.copy()
        
        # Handle missing values
        numeric_cols = df_processed.select_dtypes(include=[np.number]).columns
        df_processed[numeric_cols] = df_processed[numeric_cols].fillna(0)
        
        # Select important features for speed
        if self.selected_features is None or is_training:
            # Use variance to select features
            variances = df_processed[numeric_cols].var()
            top_features = variances.nlargest(20).index.tolist()
            self.selected_features = top_features
        
        # Use only selected features
        available_features = [f for f in self.selected_features if f in df_processed.columns]
        if len(available_features) < 10:
            available_features = numeric_cols[:15].tolist()
        
        df_processed = df_processed[available_features]
        
        # Scale features
        if is_training:
            df_scaled = self.scaler.fit_transform(df_processed)
        else:
            df_scaled = self.scaler.transform(df_processed)
        
        return pd.DataFrame(df_scaled, columns=available_features)
    
    def save(self, path: str):
        """Save preprocessor"""
        joblib.dump({
            'scaler': self.scaler,
            'selected_features': self.selected_features,
            'label_encoders': self.label_encoders
        }, path)
    
    def load(self, path: str):
        """Load preprocessor"""
        data = joblib.load(path)
        self.scaler = data['scaler']
        self.selected_features = data['selected_features']
        self.label_encoders = data.get('label_encoders', {})