from flask import Flask, request, jsonify, render_template
import subprocess
import os
import tempfile
import yaml
import re
import sys
from pathlib import Path

app = Flask(__name__, static_folder='static', template_folder='templates')

# Configurações
BASE_DIR = Path(__file__).parent.parent
AWS_NUKE_PATH = str(BASE_DIR / 'src-nuke' / 'aws-nuke-v2.25.0-linux-amd64')
AWS_CLEANER_PATH = str(BASE_DIR / 'src-app' / 'aws_resource_cleaner_simple.py')

def validate_inputs(data):
    """Valida os dados de entrada"""
    required_fields = ['account_id', 'aws_access_key', 'aws_secret_key', 'region']
    
    for field in required_fields:
        if not data.get(field):
            return False, f'Campo obrigatório: {field}'
    
    # Valida formato do Account ID
    if not re.match(r'^\d{12}$', data['account_id']):
        return False, 'Account ID deve ter 12 dígitos'
    
    # Valida formato básico da Access Key
    if not re.match(r'^AKIA[0-9A-Z]{16}$', data['aws_access_key']):
        return False, 'AWS Access Key deve começar com AKIA e ter 20 caracteres'
    
    # Valida tamanho da Secret Key
    if len(data['aws_secret_key']) != 40:
        return False, 'AWS Secret Key deve ter 40 caracteres'
    
    return True, ''

def create_config_file(data):
    """Cria arquivo de configuração sem exigir alias da conta"""
    config = {
        'account-blocklist': ["999999999999"],  # Conta protegida
        'accounts': {
            data['account_id']: {}  # Sem filtros para permitir deletar TUDO
        },
        'regions': ['global', data['region']],  # Adicionado 'global' para recursos globais
        'feature-flags': {
            'disable-deletion-protection': {
                'EC2Instance': True,
                'RDSInstance': True,
                'CloudformationStack': True
            }
        }
    }
    
    fd, path = tempfile.mkstemp(suffix='.yml')
    with os.fdopen(fd, 'w') as tmp:
        yaml.dump(config, tmp, sort_keys=False, default_flow_style=False, width=float("inf"))
    
    return path

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/dry-run', methods=['POST'])
def dry_run():
    try:
        data = request.json
        
        # Validação
        is_valid, error_msg = validate_inputs(data)
        if not is_valid:
            return jsonify({'success': False, 'error': error_msg}), 400
        
        # Configura ambiente AWS
        env = os.environ.copy()
        env.update({
            'AWS_ACCESS_KEY_ID': data['aws_access_key'],
            'AWS_SECRET_ACCESS_KEY': data['aws_secret_key'],
            'AWS_DEFAULT_REGION': data['region']
        })
        
        # Usa o AWS Resource Cleaner em vez do AWS Nuke
        result = subprocess.run(
            [
                sys.executable, AWS_CLEANER_PATH,
                '--access-key', data['aws_access_key'],
                '--secret-key', data['aws_secret_key'],
                '--region', data['region']
            ],
            env=env,
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=300  # 5 minutos timeout
        )
        
        return jsonify({
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr,
            'return_code': result.returncode
        })
        
    except subprocess.TimeoutExpired:
        return jsonify({'success': False, 'error': 'Timeout: Operação demorou mais que 5 minutos'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': f'Erro: {str(e)}'}), 500

@app.route('/api/execute', methods=['POST'])
def execute():
    try:
        data = request.json
        
        # Validação
        if not data.get('confirmed'):
            return jsonify({
                'success': False,
                'error': 'Confirmação necessária para executar o nuke'
            }), 400

        is_valid, error_msg = validate_inputs(data)
        if not is_valid:
            return jsonify({'success': False, 'error': error_msg}), 400

        # Configura ambiente AWS
        env = os.environ.copy()
        env.update({
            'AWS_ACCESS_KEY_ID': data['aws_access_key'],
            'AWS_SECRET_ACCESS_KEY': data['aws_secret_key'],
            'AWS_DEFAULT_REGION': data['region']
        })
        
        # Usa o AWS Resource Cleaner em vez do AWS Nuke
        result = subprocess.run(
            [
                sys.executable, AWS_CLEANER_PATH,
                '--access-key', data['aws_access_key'],
                '--secret-key', data['aws_secret_key'],
                '--region', data['region'],
                '--no-dry-run'
            ],
            env=env,
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=1800  # 30 minutos timeout
        )
        
        return jsonify({
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr,
            'return_code': result.returncode
        })
        
    except subprocess.TimeoutExpired:
        return jsonify({'success': False, 'error': 'Timeout: Operação demorou mais que 30 minutos'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': f'Erro: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Verifica se tudo está funcionando"""
    try:
        cleaner_exists = os.path.exists(AWS_CLEANER_PATH)
        
        if not cleaner_exists:
            return jsonify({
                'status': 'error',
                'message': 'AWS Resource Cleaner não encontrado'
            }), 500
            
        return jsonify({
            'status': 'ok',
            'aws_cleaner_path': AWS_CLEANER_PATH,
            'version': 'v1.0.0'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
