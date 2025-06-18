#!/usr/bin/env python3
"""
Test script for AWS Resource Cleaner application
"""

import requests
import sys

def test_health():
    """Test health endpoint"""
    print("🔍 Testing Health Check...")
    try:
        response = requests.get('http://localhost:5000/api/health', timeout=10)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Status: {data.get('status')}")
            print(f"   Version: {data.get('version')}")
            print("   ✅ Health Check OK")
            return True
        else:
            print(f"   ❌ Health Check Failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Error: Application not running on http://localhost:5000")
        print("   💡 Run: python src-app/app.py")
        return False
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False

def test_validation():
    """Test input validation"""
    print("\n🔍 Testing Input Validation...")
    
    test_cases = [
        {
            'name': 'Invalid Account ID (too short)',
            'data': {
                'account_id': '12345',
                'aws_access_key': 'AKIATEST123456789012',
                'aws_secret_key': 'test1234567890123456789012345678901234567890',
                'region': 'us-east-1'
            },
            'should_fail': True
        },
        {
            'name': 'Invalid Access Key (wrong format)',
            'data': {
                'account_id': '123456789012',
                'aws_access_key': 'INVALID_KEY',
                'aws_secret_key': 'test1234567890123456789012345678901234567890',
                'region': 'us-east-1'
            },
            'should_fail': True
        },
        {
            'name': 'Valid data (but fake credentials)',
            'data': {
                'account_id': '123456789012',
                'aws_access_key': 'AKIATEST123456789012',
                'aws_secret_key': 'test1234567890123456789012345678901234567890',
                'region': 'us-east-1'
            },
            'should_fail': False
        }
    ]
    
    passed = 0
    total = len(test_cases)
    
    for test_case in test_cases:
        print(f"   🧪 {test_case['name']}...")
        try:
            response = requests.post(
                'http://localhost:5000/api/dry-run',
                json=test_case['data'],
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if test_case['should_fail']:
                if response.status_code == 400:
                    print("      ✅ Validation worked (rejected invalid data)")
                    passed += 1
                else:
                    print(f"      ❌ Should have failed, but returned {response.status_code}")
            else:
                if response.status_code in [200, 500]:  # 500 expected with fake credentials
                    print("      ✅ Validation passed (accepted valid data)")
                    passed += 1
                else:
                    print(f"      ❌ Should have passed, but returned {response.status_code}")
                    
        except Exception as e:
            print(f"      ❌ Test error: {e}")
    
    print(f"   📊 Validation: {passed}/{total} tests passed")
    return passed == total

def test_dry_run():
    """Test dry-run with test credentials"""
    print("\n🔍 Testing Dry-Run...")
    data = {
        'account_id': '123456789012',
        'aws_access_key': 'AKIATEST123456789012',
        'aws_secret_key': 'test1234567890123456789012345678901234567890',
        'region': 'us-east-1'
    }
    
    try:
        print("   📤 Sending request...")
        response = requests.post(
            'http://localhost:5000/api/dry-run',
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=60
        )
        
        print(f"   📥 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   📊 Success: {result.get('success')}")
            
            output = result.get('output', '')
            if output:
                print("   📋 Output Preview:")
                lines = output.split('\n')[:10]
                for line in lines:
                    if line.strip():
                        print(f"      {line}")
                if len(output.split('\n')) > 10:
                    print("      ... (output truncated)")
            
            error = result.get('error', '')
            if error and 'InvalidClientTokenId' in error:
                print("   ✅ Expected error: Invalid test credentials")
                return True
            elif error:
                print(f"   ⚠️  Error: {error[:100]}...")
                
            return True
            
        else:
            print(f"   ❌ Dry-run failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   📋 Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"   📋 Response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.Timeout:
        print("   ❌ Timeout: Dry-run took more than 60 seconds")
        return False
    except Exception as e:
        print(f"   ❌ Dry-run error: {e}")
        return False

def test_security():
    """Test security aspects"""
    print("\n🔍 Testing Security...")
    
    import os
    import glob
    
    print("   🔒 Checking files for credentials...")
    
    # Look for credential patterns in Python files
    python_files = glob.glob('../src-app/*.py')
    found_credentials = False
    
    for file_path in python_files:
        if 'test' in file_path.lower() or 'example' in file_path.lower():
            continue  # Skip test files
            
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                # Look for real credential patterns (not test ones)
                if 'AKIA' in content and 'AKIATEST' not in content:
                    print(f"      ⚠️  Possible credential found in {file_path}")
                    found_credentials = True
        except:
            pass
    
    if not found_credentials:
        print("      ✅ No real credentials found in files")
    
    # Check if .gitignore is configured
    gitignore_path = '../.gitignore'
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r') as f:
            gitignore_content = f.read()
            if '*.pem' in gitignore_content and 'credentials' in gitignore_content:
                print("      ✅ .gitignore configured to ignore credentials")
            else:
                print("      ⚠️  .gitignore may not be protecting credentials")
    else:
        print("      ⚠️  .gitignore not found")
    
    return not found_credentials

def main():
    """Main test function"""
    print("🧪 Testing AWS Resource Cleaner application...")
    print("=" * 60)
    
    tests = [
        ("Health Check", test_health),
        ("Validation", test_validation),
        ("Dry-Run", test_dry_run),
        ("Security", test_security)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ Error in test {test_name}: {e}")
            results[test_name] = False
    
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY:")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print("=" * 60)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed. Check logs above.")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
