#!/bin/bash

# AWS Resource Cleaner - Organized Git Commits
# Execute this script to make clean, organized commits

set -e

echo "🚀 AWS Resource Cleaner - Git Commit Script"
echo "==========================================="

# Check if we're in a git repository
if [ ! -d .git ]; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

# Function to ask for confirmation
confirm() {
    read -p "$1 (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        return 0
    else
        return 1
    fi
}

# Check for sensitive data before committing
echo "🔍 Checking for sensitive data..."
if grep -r "AKIA[A-Z0-9]\{16\}" . --exclude-dir=.git | grep -v "AKIATEST\|AKIAEXAMPLE"; then
    echo "❌ ERROR: Real AWS credentials found in files!"
    echo "Please remove real credentials before committing."
    exit 1
else
    echo "✅ No real credentials found"
fi

echo ""
echo "📋 This script will create 7 organized commits:"
echo "1. Update documentation to English"
echo "2. Add project configuration files"
echo "3. Add main Flask application"
echo "4. Add AWS resource cleaner scripts"
echo "5. Add AWS Nuke binaries and configuration"
echo "6. Add test suite"
echo "7. Add usage examples and final cleanup"
echo ""

if ! confirm "Do you want to proceed with all commits?"; then
    echo "Aborted."
    exit 0
fi

echo ""
echo "🔄 Starting commits..."

# Commit 1: Documentation
echo "📝 Commit 1/8: Update documentation..."
git add README.md docs/INSTALLATION.md docs/SECURITY.md
git commit -m "docs: update documentation to English and simplify

- Convert all documentation from Portuguese to English
- Simplify documentation structure and content
- Emphasize security and no credential storage policy
- Update README with clear security guarantees
- Streamline installation and security guides"

# Commit 2: Configuration
echo "⚙️  Commit 2/8: Add configuration files..."
git add .gitignore
git commit -m "config: add comprehensive .gitignore

- Add .gitignore to protect sensitive files
- Exclude AWS credentials, keys, and certificates
- Exclude Python cache and temporary files
- Exclude logs and backup files
- Ensure no sensitive data is committed"

# Commit 3: Main application
echo "🌐 Commit 3/8: Add Flask application..."
git add src-app/app.py src-app/requirements.txt src-app/templates/ src-app/static/
git commit -m "feat: add main Flask web application

- Add Flask web interface for AWS resource cleaning
- Add REST API endpoints for dry-run and execution
- Add modern web interface with dark/light mode
- Add input validation for AWS credentials
- Add health check endpoint
- Include CSS styling and HTML templates"

# Commit 4: Resource cleaner scripts
echo "🧹 Commit 4/8: Add resource cleaner scripts..."
git add src-app/aws_resource_cleaner_simple.py src-app/aws_resource_cleaner.py
git commit -m "feat: add AWS resource cleaning scripts

- Add optimized resource cleaner with clear output
- Add support for EC2, S3, RDS, Lambda, DynamoDB, CloudFormation
- Add dry-run mode with detailed resource listing
- Add security protections for critical resources
- Ensure no credential storage or persistence"

# Commit 5: AWS Nuke binaries
echo "🔧 Commit 5/8: Add AWS Nuke binaries..."
git add src-nuke/
git commit -m "feat: add AWS Nuke binaries and configuration

- Add AWS Nuke v2.25.0 binary as backup option
- Add wrapper scripts for AWS Nuke integration
- Add example configuration files
- Provide fallback option for advanced users"

# Commit 6: Tests
echo "🧪 Commit 6/8: Add test suite..."
git add tests/
git commit -m "test: add comprehensive test suite

- Add automated tests for application functionality
- Add health check, validation, and dry-run tests
- Add security verification tests
- Add credential safety checks
- Ensure application reliability"

# Commit 7: Examples and final cleanup
echo "🏁 Commit 7/7: Add examples and final cleanup..."
git add examples/ COMMIT_PLAN.md commit.sh
git commit -m "docs: add usage examples and finalize project structure

- Add API usage examples with fake credentials
- Add configuration examples for different scenarios
- Add security best practices examples
- Add structured commit plan for clean git history
- Add automated commit script
- Complete documentation and examples
- Ready for production use"

echo ""
echo "✅ All commits completed successfully!"
echo ""

if confirm "Do you want to create a release tag v1.0.0?"; then
    git tag -a v1.0.0 -m "Release v1.0.0: AWS Resource Cleaner

- Complete web interface for AWS resource cleaning
- No credential storage guarantee
- Comprehensive documentation in English
- Full test suite and examples
- Production ready"
    echo "🏷️  Tag v1.0.0 created"
fi

echo ""
echo "🎉 Git repository is now organized with clean commit history!"
echo ""
echo "📋 Next steps:"
echo "- Review commits: git log --oneline"
echo "- Push to remote: git push origin main"
echo "- Push tags: git push origin --tags"
echo ""
echo "🔒 Security verified: No credentials stored in repository"
