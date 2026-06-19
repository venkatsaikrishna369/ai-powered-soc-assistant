import pandas as pd
import numpy as np
import os

# Create test data directory
os.makedirs("data/raw", exist_ok=True)

# Create synthetic training data
n_samples = 1000
n_features = 15

# Generate features
features = {}
for i in range(n_features):
    features[f'feature_{i}'] = np.random.randn(n_samples)

# Add labels (80% normal, 20% attack)
features['label'] = np.random.choice([0, 1], n_samples, p=[0.8, 0.2])

# Create DataFrame
df = pd.DataFrame(features)

# Save to CSV
df.to_csv("data/raw/training.csv", index=False)
print(f"Created training.csv with {len(df)} samples")

# Create testing data (smaller)
test_samples = 200
test_features = {}
for i in range(n_features):
    test_features[f'feature_{i}'] = np.random.randn(test_samples)

test_features['label'] = np.random.choice([0, 1], test_samples, p=[0.7, 0.3])

test_df = pd.DataFrame(test_features)
test_df.to_csv("data/raw/testing.csv", index=False)
print(f"Created testing.csv with {len(test_df)} samples")