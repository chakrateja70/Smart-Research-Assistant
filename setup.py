#!/usr/bin/env python3
"""
Setup script for EZ Task Document Processor
"""

import os
import subprocess
import sys

def create_venv():
    """Create a virtual environment if it doesn't exist"""
    if not os.path.exists("venv"):
        print("Creating virtual environment in ./venv ...")
        subprocess.check_call([sys.executable, "-m", "venv", "venv"])
        print("Virtual environment created.")
    else:
        print("Virtual environment already exists.")

def get_venv_python():
    """Get the path to the Python executable in the venv"""
    if os.name == "nt":
        return os.path.join("venv", "Scripts", "python.exe")
    else:
        return os.path.join("venv", "bin", "python")

def install_requirements():
    """Install required packages using venv Python"""
    print("Installing required packages in virtual environment...")
    venv_python = get_venv_python()
    try:
        subprocess.check_call([venv_python, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Requirements installed successfully.")
    except subprocess.CalledProcessError:
        print("Failed to install requirements.")
        return False
    return True

def check_env_file():
    """Check if .env file exists"""
    if not os.path.exists(".env"):
        print(".env file not found.")
        print("Please copy .env.example to .env and add your API keys:")
        print("   - GOOGLE_API_KEY")
        print("   - PINECONE_API_KEY")
        return False
    else:
        print(".env file found.")
        return True

def is_venv_active():
    """Check if the script is running inside the venv"""
    return (
        hasattr(sys, 'real_prefix') or
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) or
        os.environ.get('VIRTUAL_ENV')
    )

def main():
    print("Setting up EZ Task Document Processor...")
    print("=" * 50)
    
    # Create virtual environment if needed
    create_venv()

    # Check if running inside the venv
    if not is_venv_active():
        print("\nVirtual environment is not active.")
        print("Please activate the virtual environment before continuing:")
        if os.name == "nt":
            print("   venv\\Scripts\\activate")
        else:
            print("   source venv/bin/activate")
        print("\nAfter activation, re-run this setup script to install requirements.")
        sys.exit(1)
    else:
        print("Virtual environment is active.")

    # Install requirements in venv
    if not install_requirements():
        sys.exit(1)
    
    # Check environment file
    env_exists = check_env_file()
    
    print("\n" + "=" * 50)
    if env_exists:
        print("Setup complete. To start your app:")
        print("   streamlit run app.py")
    else:
        print("Setup incomplete. Please configure your .env file first.")
        print("Steps to complete setup:")
        print("   1. Copy .env.example to .env")
        print("   2. Add your Google AI API key")
        print("   3. Add your Pinecone API key")
        print("   4. Activate your virtual environment:")
        if os.name == "nt":
            print("      venv\\Scripts\\activate")
        else:
            print("      source venv/bin/activate")
        print("   5. Run: streamlit run app.py")

if __name__ == "__main__":
    main()
