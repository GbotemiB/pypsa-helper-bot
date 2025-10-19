#!/usr/bin/env python3
"""
Quick test script to verify local setup before deployment
"""
import os
import sys
from pathlib import Path

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def print_warning(text):
    print(f"⚠️  {text}")

def test_python_version():
    print_header("Testing Python Version")
    version = sys.version_info
    if version >= (3, 11):
        print_success(f"Python {version.major}.{version.minor}.{version.micro} (Required: 3.11+)")
        return True
    else:
        print_error(f"Python {version.major}.{version.minor}.{version.micro} (Required: 3.11+)")
        return False

def test_imports():
    print_header("Testing Dependencies")
    required_packages = [
        ("discord", "discord.py"),
        ("langchain", "langchain"),
        ("langchain_google_genai", "langchain-google-genai"),
        ("google.generativeai", "google-generativeai"),
        ("faiss", "faiss-cpu"),
        ("dotenv", "python-dotenv"),
        ("git", "gitpython"),
        ("requests", "requests"),
    ]
    
    all_passed = True
    for module_name, package_name in required_packages:
        try:
            __import__(module_name)
            print_success(f"{package_name} installed")
        except ImportError:
            print_error(f"{package_name} NOT installed (pip install {package_name})")
            all_passed = False
    
    return all_passed

def test_environment_variables():
    print_header("Testing Environment Variables")
    
    # Try to load .env file
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print_success(".env file loaded")
    except Exception as e:
        print_error(f"Error loading .env file: {e}")
        return False
    
    required_vars = [
        "DISCORD_BOT_TOKEN",
        "GOOGLE_API_KEY",
    ]
    
    optional_vars = [
        "GITHUB_ACCESS_TOKEN",
        "GITHUB_REPO_OWNER",
        "GITHUB_REPO_NAME",
    ]
    
    all_passed = True
    for var in required_vars:
        value = os.getenv(var)
        if value and len(value) > 10:
            print_success(f"{var} is set ({value[:10]}...)")
        else:
            print_error(f"{var} is NOT set or invalid")
            all_passed = False
    
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print_success(f"{var} is set (optional)")
        else:
            print_warning(f"{var} is not set (optional)")
    
    return all_passed

def test_faiss_index():
    print_header("Testing FAISS Index")
    
    index_path = Path("pypsa_ecosystem_faiss_index")
    
    if not index_path.exists():
        print_error("FAISS index directory not found")
        print_warning("Run: cd src && python ingest.py")
        return False
    
    index_file = index_path / "index.faiss"
    pkl_file = index_path / "index.pkl"
    
    if not index_file.exists():
        print_error("index.faiss file not found")
        return False
    
    if not pkl_file.exists():
        print_error("index.pkl file not found")
        return False
    
    # Check file sizes
    index_size_mb = index_file.stat().st_size / 1024 / 1024
    pkl_size_mb = pkl_file.stat().st_size / 1024 / 1024
    
    print_success(f"index.faiss found ({index_size_mb:.1f} MB)")
    print_success(f"index.pkl found ({pkl_size_mb:.1f} MB)")
    
    # Check if files are recent
    import time
    age_hours = (time.time() - index_file.stat().st_mtime) / 3600
    if age_hours < 24:
        print_success(f"Index is recent ({age_hours:.1f} hours old)")
    elif age_hours < 168:  # 7 days
        print_warning(f"Index is {age_hours:.1f} hours old (consider regenerating)")
    else:
        print_warning(f"Index is {age_hours/24:.1f} days old (recommend regenerating)")
    
    return True

def test_storage_module():
    print_header("Testing Storage Module")
    
    try:
        # Add src to path if not already there
        src_path = Path(__file__).parent / "src"
        if src_path.exists() and str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
        
        from storage import IndexStorage, ensure_index_available
        print_success("storage.py module imports successfully")
        
        storage = IndexStorage()
        info = storage.get_index_info()
        
        if info.get('exists'):
            print_success(f"Index info retrieved: {info}")
        else:
            print_warning("Index exists but info incomplete")
        
        return True
    except Exception as e:
        print_error(f"Error testing storage module: {e}")
        return False

def test_discord_connection():
    print_header("Testing Discord Bot Token")
    
    try:
        import discord
        from dotenv import load_dotenv
        load_dotenv()
        
        token = os.getenv('DISCORD_BOT_TOKEN')
        if not token:
            print_error("DISCORD_BOT_TOKEN not set")
            return False
        
        # Try to create client (doesn't actually connect)
        intents = discord.Intents.default()
        intents.message_content = True
        client = discord.Client(intents=intents)
        
        print_success("Discord client created successfully")
        print_warning("Note: Not actually connecting to Discord in this test")
        print_warning("Run 'python src/bot.py' to test actual connection")
        
        return True
    except Exception as e:
        print_error(f"Error testing Discord setup: {e}")
        return False

def test_google_api():
    print_header("Testing Google API Connection")
    
    try:
        import google.generativeai as genai
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            print_error("GOOGLE_API_KEY not set")
            return False
        
        genai.configure(api_key=api_key)
        
        # Try to list models (lightweight API call)
        models = genai.list_models()
        model_names = [m.name for m in models if 'gemini' in m.name.lower()]
        
        if model_names:
            print_success(f"Connected to Google API successfully")
            print_success(f"Available Gemini models: {len(model_names)}")
        else:
            print_warning("Connected but no Gemini models found")
        
        return True
    except Exception as e:
        print_error(f"Error testing Google API: {e}")
        print_warning("Check your GOOGLE_API_KEY is valid")
        return False

def main():
    print("\n" + "🧪 PyPSA Helper Bot - Local Test Suite".center(60))
    print("=" * 60)
    
    results = []
    
    # Run all tests
    results.append(("Python Version", test_python_version()))
    results.append(("Dependencies", test_imports()))
    results.append(("Environment Variables", test_environment_variables()))
    results.append(("FAISS Index", test_faiss_index()))
    results.append(("Storage Module", test_storage_module()))
    results.append(("Discord Setup", test_discord_connection()))
    results.append(("Google API", test_google_api()))
    
    # Summary
    print_header("Test Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("\n" + "="*60)
    print(f"  Results: {passed}/{total} tests passed")
    print("="*60)
    
    if passed == total:
        print("\n🎉 All tests passed! You're ready to run the bot locally.")
        print("\nNext steps:")
        print("  1. Run: cd src && python bot.py")
        print("  2. Test in Discord by mentioning the bot")
        print("  3. Follow docs/DEPLOYMENT.md to deploy to Fly.io")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  - Install dependencies: pip install -r requirements.txt")
        print("  - Create .env file: cp .env.sample .env")
        print("  - Generate index: cd src && python ingest.py")
        return 1

if __name__ == "__main__":
    sys.exit(main())
