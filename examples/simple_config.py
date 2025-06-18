#!/usr/bin/env python3
"""
Simple configuration example for AWS Resource Cleaner
This shows how to configure the application without filters
"""

# Example configuration without filters - DELETES EVERYTHING!
SIMPLE_CONFIG = {
    'account-blocklist': ["999999999999"],  # Protected account
    'accounts': {
        '123456789012': {}  # No filters = DELETE EVERYTHING
    },
    'regions': ['global', 'us-east-1'],
    'feature-flags': {
        'disable-deletion-protection': {
            'EC2Instance': True,
            'RDSInstance': True,
            'CloudformationStack': True
        }
    }
}

# Example with some basic filters
FILTERED_CONFIG = {
    'account-blocklist': ["999999999999"],
    'accounts': {
        '123456789012': {
            'filters': {
                'EC2Instance': [
                    {
                        'property': 'tag:Environment',
                        'value': 'Production'
                    }
                ],
                'S3Bucket': [
                    {
                        'property': 'Name',
                        'value': 'important-*'
                    }
                ]
            }
        }
    },
    'regions': ['us-east-1'],
}

def save_config(config, filename):
    """Save configuration to YAML file"""
    import yaml
    
    with open(filename, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    
    print(f"Configuration saved to {filename}")

if __name__ == '__main__':
    print("🔧 AWS Resource Cleaner Configuration Examples")
    print("=" * 50)
    
    print("\n1. Simple config (NO FILTERS - DELETES EVERYTHING):")
    print("   - Use for test accounts only")
    print("   - No protection for any resources")
    
    print("\n2. Filtered config (WITH PROTECTION):")
    print("   - Protects Production tagged resources")
    print("   - Protects buckets starting with 'important-'")
    
    choice = input("\nSave which config? (1=simple, 2=filtered, n=none): ")
    
    if choice == '1':
        save_config(SIMPLE_CONFIG, 'simple-config.yml')
        print("⚠️  WARNING: This config has NO FILTERS!")
    elif choice == '2':
        save_config(FILTERED_CONFIG, 'filtered-config.yml')
        print("✅ This config has basic protections")
    else:
        print("No config saved")
    
    print("\n💡 To use config with AWS Nuke:")
    print("   aws-nuke -c config.yml --dry-run")
    print("   aws-nuke -c config.yml --no-dry-run --force")
