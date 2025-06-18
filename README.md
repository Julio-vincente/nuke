# AWS Resource Cleaner

A modern web interface to clean all AWS resources from an account without requiring account alias. Uses only Account ID and temporary AWS credentials.

## **SECURITY: NO CREDENTIALS STORED**

### **THIS APPLICATION NEVER STORES CREDENTIALS**

### 🔍 **How Credentials Are Handled:**

```python
# ✅ SAFE: Credentials used only temporarily
env = os.environ.copy()
env.update({
    'AWS_ACCESS_KEY_ID': data['aws_access_key'],      # Used only during execution
    'AWS_SECRET_ACCESS_KEY': data['aws_secret_key'],  # Not saved anywhere
    'AWS_DEFAULT_REGION': data['region']              # Discarded after use
})

# Child process uses credentials and terminates
result = subprocess.run([script], env=env, ...)

# Variables are automatically discarded
# No persistence of sensitive data
```

## **Quick Start**

### 1. Install Dependencies
```bash
cd src-app
pip install -r requirements.txt
```

### 2. Run Application
```bash
python app.py
```

### 3. Access Interface
Open http://localhost:5000 and fill in:
- Account ID (12 digits)
- AWS Access Key (AKIA...)
- AWS Secret Key (40 characters)
- Region

### 4. Test First
Click "🔍 Execute Dry-Run" to see what would be deleted

### 5. Execute
Click "Execute Nuke" only if you're sure

## **Project Structure**

```
nuke/
├── README.md                       # This file
├── src-app/                        # Main Flask application
│   ├── app.py                      # Web application
│   ├── aws_resource_cleaner_simple.py  # Cleanup script
│   ├── requirements.txt            # Python dependencies
│   ├── templates/index.html        # Web interface
│   └── static/style.css           # Styles
├── tests/                          # Test scripts
├── examples/                       # Usage examples
└── docs/                          # Additional documentation
```

## **Supported Resources**

| Service | Resources | Status |
|---------|-----------|--------|
| **EC2** | Instances, EBS Volumes, Security Groups | ✅ |
| **S3** | Buckets and Objects | ✅ |
| **RDS** | DB Instances | ✅ |
| **Lambda** | Functions | ✅ |
| **DynamoDB** | Tables | ✅ |
| **CloudFormation** | Stacks | ✅ |

## **Security Warnings**

- ✅ **Always run dry-run first**
- ✅ **Keep important backups**
- ✅ **Use in test/development accounts**
- ❌ **Never use in production without extreme care**

## **Testing**

```bash
cd tests
python test_app.py
```

## 📄 **License**

MIT License - see [LICENSE](LICENSE) file for details.
