#!/usr/bin/env python3
"""
AWS Resource Cleaner - Uma alternativa ao AWS Nuke
Este script usa o AWS CLI para listar e excluir recursos em uma conta AWS
"""

import boto3
import botocore
import argparse
import sys
import time
import logging
from concurrent.futures import ThreadPoolExecutor
from botocore.exceptions import ClientError

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

class AWSResourceCleaner:
    def __init__(self, access_key, secret_key, region, dry_run=True):
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        self.dry_run = dry_run
        self.session = boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        self.account_id = self._get_account_id()
        
    def _get_account_id(self):
        """Obtém o ID da conta AWS"""
        try:
            sts = self.session.client('sts')
            return sts.get_caller_identity()["Account"]
        except Exception as e:
            logger.error(f"Erro ao obter ID da conta: {e}")
            sys.exit(1)
            
    def run(self):
        """Executa a limpeza de recursos"""
        print("=" * 60)
        print(f"{'🔍 DRY RUN MODE' if self.dry_run else '🚨 EXECUTION MODE'}")
        print(f"Account ID: {self.account_id}")
        print(f"Region: {self.region}")
        print("=" * 60)
        
        # Lista de serviços para limpar
        services = [
            ("EC2 Resources", self.clean_ec2),
            ("S3 Buckets", self.clean_s3),
            ("RDS Instances", self.clean_rds),
            ("Lambda Functions", self.clean_lambda),
            ("CloudFormation Stacks", self.clean_cloudformation),
            ("DynamoDB Tables", self.clean_dynamodb),
            ("Elastic Beanstalk", self.clean_elasticbeanstalk),
            ("IAM Users", self.clean_iam_users),
            ("IAM Roles", self.clean_iam_roles),
            ("IAM Policies", self.clean_iam_policies)
        ]
        
        total_resources = 0
        
        # Executa a limpeza sequencialmente para melhor output
        for service_name, service_func in services:
            print(f"\n🔍 Checking {service_name}...")
            try:
                count = service_func()
                total_resources += count if count else 0
            except Exception as e:
                print(f"❌ Error checking {service_name}: {str(e)}")
        
        print("\n" + "=" * 60)
        print(f"📊 SUMMARY:")
        print(f"Total resources found: {total_resources}")
        if self.dry_run:
            print("🔍 This was a DRY RUN - no resources were actually deleted")
            print("💡 Use --no-dry-run flag to actually delete resources")
        else:
            print("🚨 Resources have been deleted!")
        print("=" * 60)
    
    def clean_ec2(self):
        """Limpa recursos EC2"""
        total_count = 0
        try:
            ec2 = self.session.resource('ec2')
            
            # Termina instâncias EC2
            instances = list(ec2.instances.all())
            if instances:
                print(f"  📦 Found {len(instances)} EC2 instances")
                total_count += len(instances)
                for instance in instances:
                    state = instance.state['Name']
                    print(f"    {'🔍 Would terminate' if self.dry_run else '🗑️  Terminating'} EC2 instance: {instance.id} (state: {state})")
                    if not self.dry_run and state != 'terminated':
                        instance.terminate()
            
            # Exclui volumes EBS
            volumes = list(ec2.volumes.all())
            available_volumes = [v for v in volumes if v.state != 'in-use']
            if available_volumes:
                print(f"  💾 Found {len(available_volumes)} available EBS volumes")
                total_count += len(available_volumes)
                for volume in available_volumes:
                    print(f"    {'🔍 Would delete' if self.dry_run else '🗑️  Deleting'} EBS volume: {volume.id}")
                    if not self.dry_run:
                        volume.delete()
            
            # Exclui snapshots
            snapshots = list(ec2.snapshots.filter(OwnerIds=[self.account_id]))
            if snapshots:
                print(f"  📸 Found {len(snapshots)} EBS snapshots")
                total_count += len(snapshots)
                for snapshot in snapshots:
                    print(f"    {'🔍 Would delete' if self.dry_run else '🗑️  Deleting'} snapshot: {snapshot.id}")
                    if not self.dry_run:
                        snapshot.delete()
            
            # Exclui security groups (exceto o default)
            security_groups = [sg for sg in ec2.security_groups.all() if sg.group_name != 'default']
            if security_groups:
                print(f"  🔒 Found {len(security_groups)} security groups")
                total_count += len(security_groups)
                for sg in security_groups:
                    print(f"    {'🔍 Would delete' if self.dry_run else '🗑️  Deleting'} security group: {sg.id} ({sg.group_name})")
                    if not self.dry_run:
                        try:
                            sg.delete()
                        except ClientError as e:
                            if 'DependencyViolation' in str(e):
                                print(f"    ⚠️  Cannot delete security group {sg.id} due to dependencies")
                            else:
                                raise
                                
        except Exception as e:
            print(f"  ❌ Error cleaning EC2 resources: {e}")
        
        return total_count
    
    def clean_s3(self):
        """Limpa buckets S3"""
        total_count = 0
        try:
            s3 = self.session.resource('s3')
            buckets = list(s3.buckets.all())
            
            if buckets:
                print(f"  🪣 Found {len(buckets)} S3 buckets")
                total_count += len(buckets)
                for bucket in buckets:
                    print(f"    {'🔍 Would delete' if self.dry_run else '🗑️  Deleting'} S3 bucket: {bucket.name}")
                    if not self.dry_run:
                        try:
                            # Primeiro exclui todos os objetos
                            bucket.objects.all().delete()
                            # Depois exclui o bucket
                            bucket.delete()
                        except ClientError as e:
                            print(f"    ❌ Error deleting bucket {bucket.name}: {e}")
        except Exception as e:
            print(f"  ❌ Error cleaning S3 buckets: {e}")
        
        return total_count
    
    def clean_rds(self):
        """Limpa instâncias RDS"""
        total_count = 0
        try:
            rds = self.session.client('rds')
            
            # Lista instâncias RDS
            response = rds.describe_db_instances()
            instances = response.get('DBInstances', [])
            
            if instances:
                print(f"  🗄️  Found {len(instances)} RDS instances")
                total_count += len(instances)
                for instance in instances:
                    instance_id = instance['DBInstanceIdentifier']
                    status = instance['DBInstanceStatus']
                    print(f"    {'🔍 Would delete' if self.dry_run else '🗑️  Deleting'} RDS instance: {instance_id} (status: {status})")
                    if not self.dry_run:
                        try:
                            rds.delete_db_instance(
                                DBInstanceIdentifier=instance_id,
                                SkipFinalSnapshot=True,
                                DeleteAutomatedBackups=True
                            )
                        except ClientError as e:
                            print(f"    ❌ Error deleting RDS instance {instance_id}: {e}")
        except Exception as e:
            print(f"  ❌ Error cleaning RDS instances: {e}")
        
        return total_count
    
    def clean_lambda(self):
        total_count = 0
        """Limpa funções Lambda"""
        try:
            lambda_client = self.session.client('lambda')
            
            # Lista funções Lambda
            response = lambda_client.list_functions()
            functions = response.get('Functions', [])
            
            if functions:
                logger.info(f"Encontradas {len(functions)} funções Lambda")
                for function in functions:
                    function_name = function['FunctionName']
                    logger.info(f"{'Simulando exclusão' if self.dry_run else 'Excluindo'} função Lambda: {function_name}")
                    if not self.dry_run:
                        try:
                            lambda_client.delete_function(FunctionName=function_name)
                        except ClientError as e:
                            logger.error(f"Erro ao excluir função Lambda {function_name}: {e}")
        except Exception as e:
            logger.error(f"Erro ao limpar funções Lambda: {e}")
    
    def clean_cloudformation(self):
        """Limpa stacks do CloudFormation"""
        try:
            cf = self.session.client('cloudformation')
            
            # Lista stacks do CloudFormation
            response = cf.list_stacks(
                StackStatusFilter=[
                    'CREATE_COMPLETE', 'UPDATE_COMPLETE', 'ROLLBACK_COMPLETE',
                    'UPDATE_ROLLBACK_COMPLETE'
                ]
            )
            stacks = response.get('StackSummaries', [])
            
            if stacks:
                logger.info(f"Encontradas {len(stacks)} stacks do CloudFormation")
                for stack in stacks:
                    stack_name = stack['StackName']
                    logger.info(f"{'Simulando exclusão' if self.dry_run else 'Excluindo'} stack do CloudFormation: {stack_name}")
                    if not self.dry_run:
                        try:
                            cf.delete_stack(StackName=stack_name)
                        except ClientError as e:
                            logger.error(f"Erro ao excluir stack {stack_name}: {e}")
        except Exception as e:
            logger.error(f"Erro ao limpar stacks do CloudFormation: {e}")
    
    def clean_dynamodb(self):
        """Limpa tabelas do DynamoDB"""
        try:
            dynamodb = self.session.client('dynamodb')
            
            # Lista tabelas do DynamoDB
            response = dynamodb.list_tables()
            tables = response.get('TableNames', [])
            
            if tables:
                logger.info(f"Encontradas {len(tables)} tabelas do DynamoDB")
                for table_name in tables:
                    logger.info(f"{'Simulando exclusão' if self.dry_run else 'Excluindo'} tabela do DynamoDB: {table_name}")
                    if not self.dry_run:
                        try:
                            dynamodb.delete_table(TableName=table_name)
                        except ClientError as e:
                            logger.error(f"Erro ao excluir tabela {table_name}: {e}")
        except Exception as e:
            logger.error(f"Erro ao limpar tabelas do DynamoDB: {e}")
    
    def clean_elasticbeanstalk(self):
        """Limpa ambientes do Elastic Beanstalk"""
        try:
            eb = self.session.client('elasticbeanstalk')
            
            # Lista ambientes do Elastic Beanstalk
            response = eb.describe_environments()
            environments = response.get('Environments', [])
            
            if environments:
                logger.info(f"Encontrados {len(environments)} ambientes do Elastic Beanstalk")
                for env in environments:
                    env_name = env['EnvironmentName']
                    logger.info(f"{'Simulando exclusão' if self.dry_run else 'Excluindo'} ambiente do Elastic Beanstalk: {env_name}")
                    if not self.dry_run:
                        try:
                            eb.terminate_environment(EnvironmentName=env_name)
                        except ClientError as e:
                            logger.error(f"Erro ao excluir ambiente {env_name}: {e}")
        except Exception as e:
            logger.error(f"Erro ao limpar ambientes do Elastic Beanstalk: {e}")
    
    def clean_iam_users(self):
        """Limpa usuários IAM (exceto o usuário atual)"""
        try:
            iam = self.session.client('iam')
            
            # Obtém o usuário atual
            try:
                current_user = iam.get_user()['User']['UserName']
            except:
                current_user = None
            
            # Lista usuários IAM
            response = iam.list_users()
            users = response.get('Users', [])
            
            if users:
                logger.info(f"Encontrados {len(users)} usuários IAM")
                for user in users:
                    user_name = user['UserName']
                    if user_name == current_user:
                        logger.info(f"Ignorando usuário atual: {user_name}")
                        continue
                    
                    # Remove access keys
                    keys_response = iam.list_access_keys(UserName=user_name)
                    for key in keys_response.get('AccessKeyMetadata', []):
                        key_id = key['AccessKeyId']
                        logger.info(f"{'Simulando exclusão' if self.dry_run else 'Excluindo'} access key {key_id} do usuário {user_name}")
                        if not self.dry_run:
                            iam.delete_access_key(UserName=user_name, AccessKeyId=key_id)
                    
                    # Remove políticas anexadas
                    policies_response = iam.list_attached_user_policies(UserName=user_name)
                    for policy in policies_response.get('AttachedPolicies', []):
                        policy_arn = policy['PolicyArn']
                        logger.info(f"{'Simulando desanexação' if self.dry_run else 'Desanexando'} política {policy_arn} do usuário {user_name}")
                        if not self.dry_run:
                            iam.detach_user_policy(UserName=user_name, PolicyArn=policy_arn)
                    
                    # Exclui o usuário
                    logger.info(f"{'Simulando exclusão' if self.dry_run else 'Excluindo'} usuário IAM: {user_name}")
                    if not self.dry_run:
                        try:
                            iam.delete_user(UserName=user_name)
                        except ClientError as e:
                            logger.error(f"Erro ao excluir usuário {user_name}: {e}")
        except Exception as e:
            logger.error(f"Erro ao limpar usuários IAM: {e}")
    
    def clean_iam_roles(self):
        """Limpa roles IAM (exceto roles essenciais)"""
        try:
            iam = self.session.client('iam')
            
            # Lista roles IAM
            response = iam.list_roles()
            roles = response.get('Roles', [])
            
            # Roles essenciais que não devem ser excluídas
            essential_roles = ['OrganizationAccountAccessRole', 'AWSServiceRoleFor']
            
            if roles:
                logger.info(f"Encontrados {len(roles)} roles IAM")
                for role in roles:
                    role_name = role['RoleName']
                    
                    # Verifica se é uma role essencial
                    if any(essential in role_name for essential in essential_roles):
                        logger.info(f"Ignorando role essencial: {role_name}")
                        continue
                    
                    # Remove políticas anexadas
                    policies_response = iam.list_attached_role_policies(RoleName=role_name)
                    for policy in policies_response.get('AttachedPolicies', []):
                        policy_arn = policy['PolicyArn']
                        logger.info(f"{'Simulando desanexação' if self.dry_run else 'Desanexando'} política {policy_arn} da role {role_name}")
                        if not self.dry_run:
                            iam.detach_role_policy(RoleName=role_name, PolicyArn=policy_arn)
                    
                    # Exclui a role
                    logger.info(f"{'Simulando exclusão' if self.dry_run else 'Excluindo'} role IAM: {role_name}")
                    if not self.dry_run:
                        try:
                            iam.delete_role(RoleName=role_name)
                        except ClientError as e:
                            logger.error(f"Erro ao excluir role {role_name}: {e}")
        except Exception as e:
            logger.error(f"Erro ao limpar roles IAM: {e}")
    
    def clean_iam_policies(self):
        """Limpa políticas IAM personalizadas"""
        try:
            iam = self.session.client('iam')
            
            # Lista políticas IAM personalizadas
            response = iam.list_policies(Scope='Local')
            policies = response.get('Policies', [])
            
            if policies:
                logger.info(f"Encontradas {len(policies)} políticas IAM personalizadas")
                for policy in policies:
                    policy_arn = policy['Arn']
                    policy_name = policy['PolicyName']
                    
                    # Exclui a política
                    logger.info(f"{'Simulando exclusão' if self.dry_run else 'Excluindo'} política IAM: {policy_name}")
                    if not self.dry_run:
                        try:
                            # Primeiro, exclui todas as versões não padrão
                            versions_response = iam.list_policy_versions(PolicyArn=policy_arn)
                            for version in versions_response.get('Versions', []):
                                if not version['IsDefaultVersion']:
                                    iam.delete_policy_version(
                                        PolicyArn=policy_arn,
                                        VersionId=version['VersionId']
                                    )
                            
                            # Depois, exclui a política
                            iam.delete_policy(PolicyArn=policy_arn)
                        except ClientError as e:
                            logger.error(f"Erro ao excluir política {policy_name}: {e}")
        except Exception as e:
            logger.error(f"Erro ao limpar políticas IAM: {e}")

def main():
    parser = argparse.ArgumentParser(description='AWS Resource Cleaner - Uma alternativa ao AWS Nuke')
    parser.add_argument('--access-key', required=True, help='AWS Access Key ID')
    parser.add_argument('--secret-key', required=True, help='AWS Secret Access Key')
    parser.add_argument('--region', required=True, help='AWS Region')
    parser.add_argument('--no-dry-run', action='store_true', help='Execute a exclusão real (sem isso, apenas simula)')
    
    args = parser.parse_args()
    
    cleaner = AWSResourceCleaner(
        access_key=args.access_key,
        secret_key=args.secret_key,
        region=args.region,
        dry_run=not args.no_dry_run
    )
    
    cleaner.run()

if __name__ == '__main__':
    main()
