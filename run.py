#!/usr/bin/env python3
import subprocess
import sys
import os
import webbrowser
import time
import threading

def check_dependencies():
    """Check and install dependencies"""
    print("🔍 Checking dependencies...")
    
    try:
        import fastapi
        import uvicorn
        import sklearn
        import pandas
        import openai
        print("✓ All dependencies are installed")
    except ImportError as e:
        print(f"⚠ Missing dependency: {e}")
        print("Installing requirements...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])

def check_configuration():
    """Check project configuration"""
    print("\n⚙️  Checking configuration...")
    
    from config.settings import (
        OPENAI_API_KEY, TRAINING_DATA_PATH, TESTING_DATA_PATH,
        MODELS_DIR, MODEL_FILENAME, BASE_DIR
    )
    
    # Check API key
    if OPENAI_API_KEY and not OPENAI_API_KEY.startswith('sk-your'):
        print("✓ OpenAI API Key: Configured")
    else:
        print("⚠ OpenAI API Key: Not configured (using mock LLM)")
    
    # Check data files
    if os.path.exists(TRAINING_DATA_PATH):
        print(f"✓ Training data: {TRAINING_DATA_PATH}")
    else:
        print(f"⚠ Training data not found at: {TRAINING_DATA_PATH}")
        print(f"   Current working directory: {os.getcwd()}")
        print(f"   BASE_DIR: {BASE_DIR}")
        print(f"   DATA_DIR: {os.path.dirname(TRAINING_DATA_PATH)}")
        print("   Will use synthetic data for training")
    
    if os.path.exists(TESTING_DATA_PATH):
        print(f"✓ Testing data: {TESTING_DATA_PATH}")
    else:
        print(f"⚠ Testing data not found at: {TESTING_DATA_PATH}")
        print("   Will generate synthetic logs")
    
    # Check model
    model_path = os.path.join(MODELS_DIR, MODEL_FILENAME)
    if os.path.exists(model_path):
        print("✓ ML Model: Found")
    else:
        print("⚠ ML Model: Not found (will train or use mock)")
    
    # Check frontend
    frontend_dir = os.path.join(BASE_DIR, "frontend")
    if os.path.exists(frontend_dir):
        print(f"✓ Frontend: Found at {frontend_dir}")
    else:
        print(f"✗ Frontend not found at {frontend_dir}")
    
    return True

def train_model_if_needed():
    """Train ML model if needed"""
    from config.settings import MODELS_DIR, MODEL_FILENAME, TRAINING_DATA_PATH
    
    model_path = os.path.join(MODELS_DIR, MODEL_FILENAME)
    
    if not os.path.exists(model_path):
        print("\n🤖 Training ML model...")
        try:
            # Create models directory if it doesn't exist
            os.makedirs(MODELS_DIR, exist_ok=True)
            
            # Check if training data exists
            if os.path.exists(TRAINING_DATA_PATH):
                from ml.training.train_ensemble import train_fast_model
                train_fast_model()
                print("✓ Model trained successfully")
            else:
                print("⚠ No training data found. Creating synthetic model...")
                create_synthetic_model()
        except Exception as e:
            print(f"⚠ Model training failed: {e}")
            print("Will use mock predictions")
    else:
        print("\n✓ Using existing trained model")

def create_synthetic_model():
    """Create a synthetic model for demonstration"""
    import joblib
    import numpy as np
    from sklearn.ensemble import RandomForestClassifier
    from config.settings import MODELS_DIR, MODEL_FILENAME, SCALER_FILENAME, FEATURE_NAMES_FILENAME
    
    print("Creating synthetic model for demonstration...")
    
    # Create a simple model
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    
    # Create synthetic training data
    X = np.random.randn(100, 15)
    y = np.random.choice([0, 1], 100, p=[0.8, 0.2])
    model.fit(X, y)
    
    # Save model
    model_path = os.path.join(MODELS_DIR, MODEL_FILENAME)
    joblib.dump(model, model_path)
    
    # Save scaler
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    scaler.fit(X)
    scaler_path = os.path.join(MODELS_DIR, SCALER_FILENAME)
    joblib.dump(scaler, scaler_path)
    
    # Save feature names
    feature_names = [f'feature_{i}' for i in range(15)]
    feature_path = os.path.join(MODELS_DIR, FEATURE_NAMES_FILENAME)
    joblib.dump(feature_names, feature_path)
    
    print("✓ Synthetic model created")

def open_browser():
    """Open browser after delay"""
    time.sleep(3)
    webbrowser.open('http://localhost:8000/')

def start_server():
    """Start the FastAPI server"""
    print("\n" + "="*60)
    print("🚀 NETWORK SECURITY INTELLIGENCE DASHBOARD")
    print("="*60)
    print("\nStarting server...")
    print(f"📊 Dashboard: http://localhost:8000/")
    print(f"📊 Dashboard (direct): http://localhost:8000/dashboard.html")
    print(f"🚨 Alerts Page: http://localhost:8000/alerts.html")
    print(f"📚 API Docs: http://localhost:8000/docs")
    print(f"🔗 API Test: http://localhost:8000/api/test")
    print(f"❤️  Health Check: http://localhost:8000/api/health")
    print("\nPress Ctrl+C to stop the server")
    print("-"*60)
    
    # Open browser in background
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Start server
    from backend.main import app
    import uvicorn
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )

def main():
    """Main entry point"""
    print("🔐 Initializing Security Dashboard...")
    
    # Check dependencies
    check_dependencies()
    
    # Check configuration
    check_configuration()
    
    # Train model if needed
    train_model_if_needed()
    
    # Start server
    start_server()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)