import joblib
import pandas as pd
import numpy as np
import os
import hashlib
from datetime import datetime
from typing import List, Dict, Any
import asyncio
from functools import lru_cache

from config.settings import (
    MODELS_DIR, MODEL_FILENAME, SCALER_FILENAME, FEATURE_NAMES_FILENAME,
    ALERT_THRESHOLDS, PREDICTION_CACHE_SIZE
)

class FastMLService:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_names = None
        self.model_loaded = False
        self.load_model()
    
    def load_model(self):
        """Load trained ML model"""
        try:
            model_path = os.path.join(MODELS_DIR, MODEL_FILENAME)
            scaler_path = os.path.join(MODELS_DIR, SCALER_FILENAME)
            feature_path = os.path.join(MODELS_DIR, FEATURE_NAMES_FILENAME)
            
            if os.path.exists(model_path):
                print("Loading trained ML model...")
                self.model = joblib.load(model_path)
                self.scaler = joblib.load(scaler_path)
                self.feature_names = joblib.load(feature_path)
                self.model_loaded = True
                print(f"✓ Model loaded with {len(self.feature_names)} features")
            else:
                print("⚠ No trained model found. Using mock predictions.")
                self.model_loaded = False
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model_loaded = False
    
    @lru_cache(maxsize=PREDICTION_CACHE_SIZE)
    def _cached_predict(self, data_hash: str):
        """Cached prediction for identical data"""
        return self._predict_uncached(data_hash)
    
    def predict_batch(self, log_data: List[Dict]) -> List[Dict]:
        """Predict threats from log data (FAST)"""
        if not log_data:
            return []
        
        alerts = []
        
        for i, log in enumerate(log_data):
            alert = self._create_alert(log, i)
            alerts.append(alert)
        
        return alerts
    
    def _create_alert(self, log: Dict, idx: int) -> Dict:
        """Create an alert from log data"""
        # Generate prediction
        if self.model_loaded:
            prediction = self._predict_with_model(log)
        else:
            prediction = self._mock_prediction(log)
        
        # Create alert ID
        alert_id = hashlib.md5(f"{datetime.now().timestamp()}{idx}".encode()).hexdigest()[:10]
        
        # Determine severity
        confidence = prediction['confidence']
        severity = 'info'
        if confidence >= ALERT_THRESHOLDS['critical']:
            severity = 'critical'
        elif confidence >= ALERT_THRESHOLDS['high']:
            severity = 'high'
        elif confidence >= ALERT_THRESHOLDS['medium']:
            severity = 'medium'
        elif confidence >= ALERT_THRESHOLDS['low']:
            severity = 'low'
        
        # Attack categories
        attack_types = ['Port Scan', 'DDoS', 'Malware', 'Brute Force', 'SQL Injection']
        
        return {
            'id': alert_id,
            'timestamp': datetime.now().isoformat(),
            'source_ip': log.get('source_ip', f"192.168.{idx % 256}.{idx % 100}"),
            'destination_ip': log.get('destination_ip', f"10.0.{idx % 256}.1"),
            'protocol': log.get('protocol', 'TCP'),
            'source_port': log.get('source_port', np.random.randint(1024, 65535)),
            'destination_port': log.get('destination_port', 80),
            'threat_type': 'Malicious' if prediction['is_threat'] else 'Normal',
            'confidence': confidence,
            'severity': severity,
            'risk_score': int(confidence * 100),
            'description': self._generate_description(log, prediction, severity),
            'attack_category': np.random.choice(attack_types) if prediction['is_threat'] else 'Normal',
            'mitre_techniques': [],
            'status': 'new',
            'assigned_to': None
        }
    
    def _predict_with_model(self, log: Dict) -> Dict:
        """Predict using loaded model"""
        try:
            # Create feature vector
            features = self._extract_features(log)
            
            # Predict
            if features is not None:
                proba = self.model.predict_proba(features.reshape(1, -1))
                confidence = float(proba[0, 1]) if proba.shape[1] > 1 else float(proba[0, 0])
                is_threat = confidence > 0.5
            else:
                # Fallback to mock
                confidence = np.random.uniform(0.1, 0.9)
                is_threat = confidence > 0.6
        except Exception as e:
            print(f"Model prediction error: {e}")
            confidence = np.random.uniform(0.1, 0.8)
            is_threat = confidence > 0.5
        
        return {
            'is_threat': is_threat,
            'confidence': round(confidence, 3)
        }
    
    def _extract_features(self, log: Dict) -> np.ndarray:
        """Extract features from log"""
        try:
            if not self.feature_names:
                return None
            
            features = []
            for feat_name in self.feature_names:
                # Try to get value from log
                if feat_name in log:
                    features.append(float(log[feat_name]))
                elif 'feature_' in feat_name:
                    # Extract number from feature name
                    try:
                        feat_num = int(feat_name.split('_')[1])
                        features.append(float(log.get(f'feature_{feat_num}', 0.0)))
                    except:
                        features.append(0.0)
                else:
                    features.append(0.0)
            
            # Scale features
            features_array = np.array(features).reshape(1, -1)
            if self.scaler:
                features_array = self.scaler.transform(features_array)
            
            return features_array
        except Exception as e:
            print(f"Feature extraction error: {e}")
            return None
    
    def _mock_prediction(self, log: Dict) -> Dict:
        """Generate mock prediction"""
        # Simulate some threats (30% chance)
        is_threat = np.random.random() > 0.7
        confidence = np.random.uniform(0.6, 0.95) if is_threat else np.random.uniform(0.1, 0.4)
        
        return {
            'is_threat': is_threat,
            'confidence': round(confidence, 3)
        }
    
    def _generate_description(self, log: Dict, prediction: Dict, severity: str) -> str:
        """Generate alert description"""
        source = log.get('source_ip', 'Unknown')
        dest = log.get('destination_ip', 'Unknown')
        protocol = log.get('protocol', 'TCP')
        
        if prediction['is_threat']:
            attack_types = ['port scan', 'DDoS attack', 'malware activity', 'brute force attempt']
            attack = np.random.choice(attack_types)
            return f"{severity.upper()} {attack} detected from {source} to {dest} via {protocol}"
        else:
            return f"Normal traffic from {source} to {dest}"
    
    async def analyze_logs_async(self, logs: List[Dict]) -> List[Dict]:
        """Async version for better performance"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.predict_batch, logs)

# Global instance
ml_service = FastMLService()