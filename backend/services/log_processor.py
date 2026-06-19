import pandas as pd
import numpy as np
from typing import List, Dict, Any
import random
from datetime import datetime

from config.settings import TESTING_DATA_PATH

class LogProcessor:
    def __init__(self):
        self.test_data = None
        self.load_test_data()
    
    def load_test_data(self):
        """Load testing data for simulations"""
        try:
            # LOAD YOUR TESTING.CSV FILE HERE
            self.test_data = pd.read_csv(TESTING_DATA_PATH)
            print(f"✓ Loaded {len(self.test_data)} test records from {TESTING_DATA_PATH}")
        except Exception as e:
            print(f"⚠ Could not load test data: {e}")
            self.test_data = None
    
    def generate_sample_logs(self, count: int = 10) -> List[Dict]:
        """Generate sample network logs"""
        if self.test_data is not None and len(self.test_data) > 0:
            # Use actual test data
            samples = self.test_data.sample(min(count, len(self.test_data)))
            logs = samples.to_dict('records')
            
            # Add network fields
            for i, log in enumerate(logs):
                log.update({
                    'source_ip': f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
                    'destination_ip': f"10.0.{random.randint(1, 255)}.1",
                    'protocol': random.choice(['TCP', 'UDP', 'HTTP', 'HTTPS']),
                    'timestamp': datetime.now().isoformat()
                })
            return logs
        
        # Generate synthetic logs
        return self._generate_synthetic_logs(count)
    
    def _generate_synthetic_logs(self, count: int) -> List[Dict]:
        """Generate synthetic network logs"""
        logs = []
        protocols = ['TCP', 'UDP', 'HTTP', 'HTTPS', 'DNS', 'SSH']
        
        for i in range(count):
            log = {
                'timestamp': datetime.now().isoformat(),
                'source_ip': f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
                'destination_ip': f"10.0.{random.randint(1, 255)}.{random.randint(1, 100)}",
                'source_port': random.randint(1024, 65535),
                'destination_port': random.choice([80, 443, 22, 53, 3389]),
                'protocol': random.choice(protocols),
                'packet_size': random.randint(64, 1500),
                'duration': round(random.uniform(0.1, 10.0), 2),
                'bytes_sent': random.randint(100, 10000),
                'bytes_received': random.randint(100, 5000),
                'packet_count': random.randint(1, 100),
                'flag_count': random.randint(1, 5),
                'ttl': random.choice([64, 128, 255]),
                'window_size': random.choice([8192, 16384, 32768, 65535])
            }
            
            # Add some feature columns for ML
            for j in range(15):
                log[f'feature_{j}'] = random.uniform(0, 1)
            
            logs.append(log)
        
        return logs
    
    def parse_raw_log(self, log_line: str) -> Dict:
        """Parse raw log line"""
        try:
            # Try JSON
            import json
            return json.loads(log_line)
        except:
            # Parse as space-separated
            parts = log_line.strip().split()
            if len(parts) >= 6:
                return {
                    'timestamp': parts[0],
                    'source_ip': parts[1],
                    'destination_ip': parts[2],
                    'protocol': parts[3],
                    'source_port': int(parts[4]) if parts[4].isdigit() else 0,
                    'destination_port': int(parts[5]) if parts[5].isdigit() else 0,
                    'action': parts[6] if len(parts) > 6 else 'UNKNOWN'
                }
        
        # Return minimal log
        return {
            'timestamp': datetime.now().isoformat(),
            'raw_log': log_line[:200]
        }

# Global instance
log_processor = LogProcessor()