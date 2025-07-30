#!/usr/bin/env python3
"""
Startup script for the Feature Prioritization Framework Web Interface
"""

import os
import sys
import subprocess
import webbrowser
import time

def main():
    print("🚀 Feature Prioritization Framework - Web Interface")
    print("=" * 50)
    
    # Check if virtual environment exists
    venv_path = "feature_prioritization_env"
    if not os.path.exists(venv_path):
        print("❌ Virtual environment not found. Please run the setup first.")
        print("   Run: python3 -m venv feature_prioritization_env")
        print("   Then: source feature_prioritization_env/bin/activate")
        print("   And: pip install -r requirements.txt")
        return
    
    # Check if required files exist
    required_files = [
        "app.py",
        "feature_prioritization_framework.py",
        "templates/base.html",
        "templates/index.html",
        "templates/results.html"
    ]
    
    missing_files = [f for f in required_files if not os.path.exists(f)]
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return
    
    print("✅ All required files found")
    
    # Activate virtual environment and run Flask app
    try:
        print("\n🌐 Starting web interface...")
        print("   The application will be available at: http://localhost:5000")
        print("   Press Ctrl+C to stop the server")
        print("\n" + "=" * 50)
        
        # Run Flask app
        if sys.platform == "win32":
            activate_cmd = f"{venv_path}\\Scripts\\activate && python app.py"
        else:
            activate_cmd = f"source {venv_path}/bin/activate && python app.py"
        
        subprocess.run(activate_cmd, shell=True)
        
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure all dependencies are installed:")
        print("   source feature_prioritization_env/bin/activate")
        print("   pip install -r requirements.txt")
        print("2. Check if port 5000 is available")
        print("3. Try running manually: python app.py")

if __name__ == "__main__":
    main() 