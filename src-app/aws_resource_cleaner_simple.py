#!/usr/bin/env python3
"""
AWS Resource Cleaner - Uma alternativa ao AWS Nuke (Versão Simplificada)
Este script usa o AWS CLI para listar e excluir recursos em uma conta AWS
"""

import boto3
import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description='AWS Resource Cleaner - Uma alternativa ao AWS Nuke')
    parser.add_argument('--access-key', required=True, help='AWS Access Key ID')
    parser.add_argument('--secret-key', required=True, help='AWS Secret Access Key')
    parser.add_argument('--region', required=True, help='AWS Region')
    parser.add_argument('--no-dry-run', action='store_true', help='Execute a exclusão real (sem isso, apenas simula)')
    
    args = parser.parse_args()
    
    dry_run = not args.no_dry_run
    
    # Configurar sessão AWS
    session = boto3.Session(
        aws_access_key_id=args.access_key,
        aws_secret_access_key=args.secret_key,
        region_name=args.region
    )
    
    # Obter ID da conta
    try:
        sts = session.client('sts')
        account_id = sts.get_caller_identity()["Account"]
    except Exception as e:
        print(f"❌ Erro ao obter ID da conta: {e}")
        sys.exit(1)
    
    print("=" * 60)
    print(f"{'🔍 DRY RUN MODE' if dry_run else '🚨 EXECUTION MODE'}")
    print(f"Account ID: {account_id}")
    print(f"Region: {args.region}")
    print("=" * 60)
    
    total_resources = 0
    
    # EC2 Resources
    print(f"\n🔍 Checking EC2 Resources...")
    try:
        ec2 = session.resource('ec2')
        
        # Instâncias EC2
        instances = list(ec2.instances.all())
        if instances:
            print(f"  📦 Found {len(instances)} EC2 instances")
            total_resources += len(instances)
            for instance in instances:
                state = instance.state['Name']
                print(f"    {'🔍 Would terminate' if dry_run else '🗑️  Terminating'} EC2 instance: {instance.id} (state: {state})")
                if not dry_run and state not in ['terminated', 'terminating']:
                    instance.terminate()
        
        # Volumes EBS
        volumes = [v for v in ec2.volumes.all() if v.state == 'available']
        if volumes:
            print(f"  💾 Found {len(volumes)} available EBS volumes")
            total_resources += len(volumes)
            for volume in volumes:
                print(f"    {'🔍 Would delete' if dry_run else '🗑️  Deleting'} EBS volume: {volume.id}")
                if not dry_run:
                    volume.delete()
        
        # Security Groups
        security_groups = [sg for sg in ec2.security_groups.all() if sg.group_name != 'default']
        if security_groups:
            print(f"  🔒 Found {len(security_groups)} security groups")
            total_resources += len(security_groups)
            for sg in security_groups:
                print(f"    {'🔍 Would delete' if dry_run else '🗑️  Deleting'} security group: {sg.id} ({sg.group_name})")
                if not dry_run:
                    try:
                        sg.delete()
                    except Exception as e:
                        print(f"    ⚠️  Cannot delete security group {sg.id}: {str(e)}")
                        
    except Exception as e:
        print(f"  ❌ Error checking EC2 resources: {e}")
    
    # S3 Buckets
    print(f"\n🔍 Checking S3 Buckets...")
    try:
        s3 = session.resource('s3')
        buckets = list(s3.buckets.all())
        
        if buckets:
            print(f"  🪣 Found {len(buckets)} S3 buckets")
            total_resources += len(buckets)
            for bucket in buckets:
                print(f"    {'🔍 Would delete' if dry_run else '🗑️  Deleting'} S3 bucket: {bucket.name}")
                if not dry_run:
                    try:
                        # Primeiro exclui todos os objetos
                        bucket.objects.all().delete()
                        # Depois exclui o bucket
                        bucket.delete()
                    except Exception as e:
                        print(f"    ❌ Error deleting bucket {bucket.name}: {e}")
    except Exception as e:
        print(f"  ❌ Error checking S3 buckets: {e}")
    
    # RDS Instances
    print(f"\n🔍 Checking RDS Instances...")
    try:
        rds = session.client('rds')
        response = rds.describe_db_instances()
        instances = response.get('DBInstances', [])
        
        if instances:
            print(f"  🗄️  Found {len(instances)} RDS instances")
            total_resources += len(instances)
            for instance in instances:
                instance_id = instance['DBInstanceIdentifier']
                status = instance['DBInstanceStatus']
                print(f"    {'🔍 Would delete' if dry_run else '🗑️  Deleting'} RDS instance: {instance_id} (status: {status})")
                if not dry_run:
                    try:
                        rds.delete_db_instance(
                            DBInstanceIdentifier=instance_id,
                            SkipFinalSnapshot=True,
                            DeleteAutomatedBackups=True
                        )
                    except Exception as e:
                        print(f"    ❌ Error deleting RDS instance {instance_id}: {e}")
    except Exception as e:
        print(f"  ❌ Error checking RDS instances: {e}")
    
    # Lambda Functions
    print(f"\n🔍 Checking Lambda Functions...")
    try:
        lambda_client = session.client('lambda')
        response = lambda_client.list_functions()
        functions = response.get('Functions', [])
        
        if functions:
            print(f"  ⚡ Found {len(functions)} Lambda functions")
            total_resources += len(functions)
            for function in functions:
                function_name = function['FunctionName']
                print(f"    {'🔍 Would delete' if dry_run else '🗑️  Deleting'} Lambda function: {function_name}")
                if not dry_run:
                    try:
                        lambda_client.delete_function(FunctionName=function_name)
                    except Exception as e:
                        print(f"    ❌ Error deleting Lambda function {function_name}: {e}")
    except Exception as e:
        print(f"  ❌ Error checking Lambda functions: {e}")
    
    # DynamoDB Tables
    print(f"\n🔍 Checking DynamoDB Tables...")
    try:
        dynamodb = session.client('dynamodb')
        response = dynamodb.list_tables()
        tables = response.get('TableNames', [])
        
        if tables:
            print(f"  🗃️  Found {len(tables)} DynamoDB tables")
            total_resources += len(tables)
            for table_name in tables:
                print(f"    {'🔍 Would delete' if dry_run else '🗑️  Deleting'} DynamoDB table: {table_name}")
                if not dry_run:
                    try:
                        dynamodb.delete_table(TableName=table_name)
                    except Exception as e:
                        print(f"    ❌ Error deleting DynamoDB table {table_name}: {e}")
    except Exception as e:
        print(f"  ❌ Error checking DynamoDB tables: {e}")
    
    # CloudFormation Stacks
    print(f"\n🔍 Checking CloudFormation Stacks...")
    try:
        cf = session.client('cloudformation')
        response = cf.list_stacks(
            StackStatusFilter=[
                'CREATE_COMPLETE', 'UPDATE_COMPLETE', 'ROLLBACK_COMPLETE',
                'UPDATE_ROLLBACK_COMPLETE'
            ]
        )
        stacks = response.get('StackSummaries', [])
        
        if stacks:
            print(f"  📚 Found {len(stacks)} CloudFormation stacks")
            total_resources += len(stacks)
            for stack in stacks:
                stack_name = stack['StackName']
                print(f"    {'🔍 Would delete' if dry_run else '🗑️  Deleting'} CloudFormation stack: {stack_name}")
                if not dry_run:
                    try:
                        cf.delete_stack(StackName=stack_name)
                    except Exception as e:
                        print(f"    ❌ Error deleting CloudFormation stack {stack_name}: {e}")
    except Exception as e:
        print(f"  ❌ Error checking CloudFormation stacks: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 SUMMARY:")
    print(f"Total resources found: {total_resources}")
    if dry_run:
        print("🔍 This was a DRY RUN - no resources were actually deleted")
        print("💡 Use --no-dry-run flag to actually delete resources")
    else:
        print("🚨 Resources have been deleted!")
    print("=" * 60)

if __name__ == '__main__':
    main()
