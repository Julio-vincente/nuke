#!/usr/bin/env python3
"""
Example API usage for AWS Resource Cleaner
WARNING: This is just an example. Never put real credentials in code!
"""

import requests
import json

# ⚠️  WARNING: NEVER put real credentials in code!
# This is just an example with fake credentials for demonstration
EXAMPLE_CREDENTIALS = {
    'account_id': '123456789012',
    'aws_access_key': 'AKIAEXAMPLE123456789',  # ❌ FAKE CREDENTIAL - WON'T WORK
    'aws_secret_key': 'example1234567890123456789012345678901234567890',  # ❌ FAKE
    'region': 'us-east-1'
}

def example_health_check():
    """Example of how to check if application is running"""
    print("🔍 Checking application status...")
    
    try:
        response = requests.get('http://localhost:5000/api/health')
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Application running!")
            print(f"   Status: {data['status']}")
            print(f"   Version: {data['version']}")
            return True
        else:
            print(f"❌ Application has issues: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Application not running. Execute: python src-app/app.py")
        return False

def example_dry_run():
    """Example of how to execute a dry-run"""
    print("\n🔍 Executing example dry-run...")
    
    # ⚠️  IMPORTANT: In real use, get credentials securely:
    # - Environment variables
    # - AWS STS (temporary credentials)
    # - User input
    # - Never hardcode in code!
    
    try:
        response = requests.post(
            'http://localhost:5000/api/dry-run',
            json=EXAMPLE_CREDENTIALS,
            headers={'Content-Type': 'application/json'},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"📊 Dry-run executed!")
            print(f"   Success: {result['success']}")
            
            if result['output']:
                print("   📋 Output:")
                # Show only first lines
                lines = result['output'].split('\n')[:15]
                for line in lines:
                    if line.strip():
                        print(f"      {line}")
            
            if result['error']:
                print(f"   ⚠️  Error (expected with fake credentials): {result['error'][:100]}...")
                
        else:
            print(f"❌ Dry-run failed: {response.status_code}")
            error_data = response.json()
            print(f"   Error: {error_data.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Request error: {e}")

def example_secure_usage():
    """Example of how to use credentials securely"""
    print("\n🔒 Example of secure credential usage:")
    
    print("""
    ✅ SECURE ways to provide credentials:
    
    1. Environment variables:
       export AWS_ACCESS_KEY_ID="your_access_key"
       export AWS_SECRET_ACCESS_KEY="your_secret_key"
       
    2. Temporary credentials (STS):
       aws sts get-session-token --duration-seconds 3600
       
    3. User input:
       access_key = input("AWS Access Key: ")
       secret_key = getpass.getpass("AWS Secret Key: ")
       
    4. Configuration file (with restricted permissions):
       chmod 600 ~/.aws/credentials
    
    ❌ NEVER do:
    - Hardcode credentials in code
    - Commit credentials to Git
    - Share credentials via email/chat
    - Store credentials in plain text
    """)

def main():
    """Main example function"""
    print("🚀 AWS Resource Cleaner API Usage Example")
    print("=" * 60)
    print("⚠️  WARNING: This example uses FAKE credentials for demonstration!")
    print("   In real use, use valid credentials securely.")
    print("=" * 60)
    
    # Check if application is running
    if not example_health_check():
        print("\n💡 To start the application:")
        print("   cd src-app")
        print("   python app.py")
        return
    
    # Execute example dry-run
    example_dry_run()
    
    # Show secure usage examples
    example_secure_usage()
    
    print("\n" + "=" * 60)
    print("✅ Example completed!")
    print("📚 Check documentation for more information.")
    print("=" * 60)

if __name__ == '__main__':
    main()
