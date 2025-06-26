#!/usr/bin/env python3
"""
Setup script for EZ Task Document Processor
"""

import os
import subprocess
import sys

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully!")
    except subprocess.CalledProcessError:
        print("❌ Failed to install requirements")
        return False
    return True

def check_env_file():
    """Check if .env file exists"""
    if not os.path.exists(".env"):
        print("⚠️  .env file not found!")
        print("📋 Please copy .env.example to .env and add your API keys:")
        print("   - GOOGLE_API_KEY")
        print("   - PINECONE_API_KEY")
        return False
    else:
        print("✅ .env file found!")
        return True

def main():
    print("🚀 Setting up EZ Task Document Processor...")
    print("=" * 50)
    
    # Install requirements
    if not install_requirements():
        sys.exit(1)
    
    # Check environment file
    env_exists = check_env_file()
    
    print("\n" + "=" * 50)
    if env_exists:
        print("✅ Setup complete! You can now run the application with:")
        print("   streamlit run app.py")
    else:
        print("⚠️  Setup incomplete. Please configure your .env file first.")
        print("📋 Steps to complete setup:")
        print("   1. Copy .env.example to .env")
        print("   2. Add your Google AI API key")
        print("   3. Add your Pinecone API key")
        print("   4. Run: streamlit run app.py")

if __name__ == "__main__":
    main()
