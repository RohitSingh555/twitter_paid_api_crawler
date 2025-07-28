#!/usr/bin/env python3
"""
Setup and run script for tweet verification system
"""

import os
import subprocess
import sys

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'openai',
        'pandas', 
        'dotenv',
        'tqdm',
        'openpyxl'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Installing required packages...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
            print("✅ Dependencies installed successfully!")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies. Please run: pip install -r requirements.txt")
            return False
    else:
        print("✅ All dependencies are installed!")
    
    return True

def check_env_file():
    """Check if .env file exists with OpenAI API key"""
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("Creating .env file template...")
        
        with open('.env', 'w') as f:
            f.write("# OpenAI API Configuration\n")
            f.write("OPENAI_API_KEY=your_openai_api_key_here\n")
            f.write("\n# Add your OpenAI API key above\n")
        
        print("✅ Created .env file template")
        print("⚠️  Please edit .env file and add your OpenAI API key")
        return False
    
    # Check if API key is set
    from dotenv import load_dotenv
    load_dotenv()
    
    if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") == "your_openai_api_key_here":
        print("❌ OpenAI API key not set in .env file!")
        print("Please edit .env file and add your actual OpenAI API key")
        return False
    
    print("✅ OpenAI API key configured!")
    return True

def run_workflow():
    """Run the complete workflow"""
    print("\n🚀 Starting tweet verification workflow...")
    
    # Step 1: Check if we have cleaned tweets
    cleaned_files = [f for f in os.listdir('.') if 'cleaned' in f and f.endswith('.json')]
    
    if not cleaned_files:
        print("❌ No cleaned tweets found!")
        print("Please run one of the cleaning scripts first:")
        print("  python clean_tweets.py")
        print("  python tweet_analyzer.py")
        return
    
    # Use the most recent cleaned file
    latest_file = max(cleaned_files, key=os.path.getctime)
    print(f"📂 Using cleaned file: {latest_file}")
    
    # Step 2: Run verification
    print("\n🔍 Running tweet verification...")
    try:
        subprocess.run([sys.executable, 'verify_tweets.py', latest_file], check=True)
        print("✅ Verification completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Verification failed: {e}")
        return
    
    # Step 3: Show results
    output_dir = "output"
    if os.path.exists(output_dir):
        output_files = os.listdir(output_dir)
        excel_files = [f for f in output_files if f.endswith('.xlsx')]
        json_files = [f for f in output_files if f.endswith('.json') and 'verified' in f]
        
        if excel_files:
            latest_excel = max(excel_files, key=lambda x: os.path.getctime(os.path.join(output_dir, x)))
            print(f"\n📊 Results saved to: output/{latest_excel}")
        
        if json_files:
            latest_json = max(json_files, key=lambda x: os.path.getctime(os.path.join(output_dir, x)))
            print(f"📄 JSON results: output/{latest_json}")

def main():
    """Main setup function"""
    print("🔥 Tweet Verification System Setup")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Check environment
    if not check_env_file():
        return
    
    # Run workflow
    run_workflow()

if __name__ == "__main__":
    main() 