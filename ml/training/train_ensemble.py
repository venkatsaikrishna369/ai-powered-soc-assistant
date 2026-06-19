import pandas as pd
import numpy as np
import joblib
import os
import time
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import warnings
warnings.filterwarnings('ignore')

from config.settings import TRAINING_DATA_PATH, MODELS_DIR, MODEL_FILENAME, SCALER_FILENAME, FEATURE_NAMES_FILENAME
from ml.preprocessing.network_features import FastFeatureEngineer

def train_fast_model():
    """Train a lightweight model for real-time predictions"""
    print("🚀 Training fast security model...")
    
    # Load your training data
    try:
        df = pd.read_csv(TRAINING_DATA_PATH)
        print(f"✓ Loaded {len(df)} records from {TRAINING_DATA_PATH}")
    except Exception as e:
        print(f"❌ Error loading training data: {e}")
        print("Using synthetic data for demonstration...")
        # Create synthetic data
        np.random.seed(42)
        n_samples = 1000
        n_features = 15
        X = np.random.randn(n_samples, n_features)
        y = np.random.choice([0, 1], n_samples, p=[0.85, 0.15])
        df = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(n_features)])
        df['label'] = y
    
    # Prepare features
    feature_engineer = FastFeatureEngineer()
    
    # Find label column
    label_col = None
    for col in ['label', 'Label', 'class', 'Class', 'attack', 'Attack', 'result']:
        if col in df.columns:
            label_col = col
            break
    
    if label_col is None:
        # Create binary label
        print("No label column found, creating synthetic labels")
        df['label'] = np.random.choice([0, 1], len(df), p=[0.85, 0.15])
        label_col = 'label'
    
    # Separate features and labels
    X = df.drop(columns=[label_col])
    y = df[label_col]
    
    # Convert labels to binary if needed
    if y.dtype == 'object':
        y = pd.factorize(y)[0]
    
    # Prepare features
    X_processed = feature_engineer.prepare_features(X, is_training=True)
    
    print(f"✓ Prepared {X_processed.shape[1]} features")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X_processed, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"✓ Training samples: {X_train.shape[0]}, Test samples: {X_test.shape[0]}")
    
    # Train fast model
    print("Training model...")
    start_time = time.time()
    
    # Use Random Forest for better performance
    model = RandomForestClassifier(
        n_estimators=50,      # Few trees for speed
        max_depth=10,         # Limit depth
        min_samples_split=5,
        n_jobs=-1,           # Use all cores
        random_state=42,
        verbose=0
    )
    
    model.fit(X_train, y_train)
    training_time = time.time() - start_time
    
    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"✓ Model trained in {training_time:.2f} seconds")
    print(f"✓ Accuracy: {accuracy:.4f}")
    
    # Save everything
    os.makedirs(MODELS_DIR, exist_ok=True)
    
    # Save model
    model_path = os.path.join(MODELS_DIR, MODEL_FILENAME)
    joblib.dump(model, model_path)
    
    # Save scaler
    scaler_path = os.path.join(MODELS_DIR, SCALER_FILENAME)
    joblib.dump(feature_engineer.scaler, scaler_path)
    
    # Save feature names
    feature_names_path = os.path.join(MODELS_DIR, FEATURE_NAMES_FILENAME)
    joblib.dump(list(X_processed.columns), feature_names_path)
    
    print(f"✓ Model saved: {model_path}")
    print(f"✓ Scaler saved: {scaler_path}")
    print(f"✓ Feature names saved: {feature_names_path}")
    
    return model

if __name__ == "__main__":
    train_fast_model()