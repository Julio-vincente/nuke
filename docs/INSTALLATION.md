# 📦 Installation Guide

## Requirements

- 🐍 Python 3.8+
- 📦 pip (Python package manager)
- 🌐 Modern web browser

## Quick Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd nuke
```

### 2. Install Dependencies
```bash
cd src-app
pip install -r requirements.txt
```

### 3. Run Application
```bash
python app.py
```

### 4. Access Interface
Open browser: http://localhost:5000

## Detailed Installation

### Step 1: Check Python
```bash
# Check Python version
python3 --version
# Should show Python 3.8 or higher

# Install Python if needed:
# Ubuntu/Debian:
sudo apt update && sudo apt install python3.8 python3-pip

# macOS (with Homebrew):
brew install python@3.8
```

### Step 2: Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
cd src-app
pip install -r requirements.txt

# Verify installation
pip list
```

## Configuration

### Custom Port
```python
# Edit src-app/app.py
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)  # Change port here
```

### HTTPS (Production)
```python
# Use SSL certificate
if __name__ == '__main__':
    app.run(
        host='0.0.0.0', 
        port=443, 
        ssl_context=('cert.pem', 'key.pem')
    )
```

## Testing Installation

### Health Check
```bash
# Test health endpoint
curl http://localhost:5000/api/health

# Expected response:
{
  "status": "ok",
  "version": "v1.0.0"
}
```

### Run Tests
```bash
cd tests
python test_app.py
```

## Troubleshooting

### "ModuleNotFoundError"
```bash
# Install missing dependencies
pip install flask boto3 pyyaml

# Or reinstall everything
pip install -r requirements.txt --force-reinstall
```

### "Permission denied"
```bash
# Give execution permissions
chmod +x src-app/aws_resource_cleaner_simple.py
```

### "Port already in use"
```bash
# Find process using port
sudo netstat -tulpn | grep :5000

# Kill process
sudo kill -9 <PID>

# Or use different port
python app.py --port 8080
```

## Uninstallation

```bash
# Stop application
pkill -f "python.*app.py"

# Remove directory
rm -rf /path/to/nuke

# Remove virtual environment
rm -rf venv
```

---

**🚀 Installation complete!**
