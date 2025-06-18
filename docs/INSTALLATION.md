# 📦 Guia de Instalação

## Pré-requisitos

### Sistema Operacional
- ✅ Linux (Ubuntu 20.04+ recomendado)
- ✅ macOS (10.15+ recomendado)
- ✅ Windows (com WSL2 recomendado)

### Software Necessário
- 🐍 Python 3.8+
- 📦 pip (gerenciador de pacotes Python)
- 🌐 Navegador web moderno

## Instalação Rápida

### 1. Clone o Repositório
```bash
git clone <repository-url>
cd nuke
```

### 2. Instale as Dependências
```bash
cd src-app
pip install -r requirements.txt
```

### 3. Execute a Aplicação
```bash
python app.py
```

### 4. Acesse a Interface
Abra seu navegador e vá para: http://localhost:5000

## Instalação Detalhada

### Passo 1: Verificar Python
```bash
# Verificar versão do Python
python3 --version
# Deve mostrar Python 3.8 ou superior

# Se não tiver Python 3.8+, instale:
# Ubuntu/Debian:
sudo apt update
sudo apt install python3.8 python3-pip

# CentOS/RHEL:
sudo yum install python38 python38-pip

# macOS (com Homebrew):
brew install python@3.8
```

### Passo 2: Criar Ambiente Virtual (Recomendado)
```bash
# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
# Linux/macOS:
source venv/bin/activate

# Windows:
venv\Scripts\activate

# Verificar se está ativo (deve mostrar (venv) no prompt)
```

### Passo 3: Instalar Dependências
```bash
cd src-app
pip install -r requirements.txt

# Verificar instalação
pip list
```

### Passo 4: Configurar Firewall (se necessário)
```bash
# Ubuntu/Debian:
sudo ufw allow 5000

# CentOS/RHEL:
sudo firewall-cmd --add-port=5000/tcp --permanent
sudo firewall-cmd --reload
```

## Configuração Avançada

### Configurar Porta Personalizada
```python
# Editar src-app/app.py
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)  # Mudar porta aqui
```

### Configurar HTTPS (Produção)
```python
# Usar certificado SSL
if __name__ == '__main__':
    app.run(
        host='0.0.0.0', 
        port=443, 
        ssl_context=('cert.pem', 'key.pem')
    )
```

### Configurar Proxy Reverso (Nginx)
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Verificação da Instalação

### Teste de Saúde
```bash
# Testar endpoint de saúde
curl http://localhost:5000/api/health

# Resposta esperada:
{
  "status": "ok",
  "aws_cleaner_path": "/path/to/aws_resource_cleaner_simple.py",
  "version": "v1.0.0"
}
```

### Teste Completo
```bash
cd tests
python test_app.py
```

## Solução de Problemas

### Erro: "ModuleNotFoundError"
```bash
# Instalar dependências em falta
pip install flask boto3 pyyaml

# Ou reinstalar tudo
pip install -r requirements.txt --force-reinstall
```

### Erro: "Permission denied"
```bash
# Dar permissões de execução
chmod +x src-app/aws_resource_cleaner_simple.py

# Verificar permissões
ls -la src-app/
```

### Erro: "Port already in use"
```bash
# Encontrar processo usando a porta
sudo netstat -tulpn | grep :5000

# Matar processo
sudo kill -9 <PID>

# Ou usar porta diferente
python app.py --port 8080
```

### Erro: "AWS credentials not found"
```bash
# Este é normal - a aplicação não usa credenciais do sistema
# Insira as credenciais na interface web
```

## Desinstalação

### Remover Aplicação
```bash
# Parar aplicação
pkill -f "python.*app.py"

# Remover diretório
rm -rf /path/to/nuke

# Desativar ambiente virtual
deactivate

# Remover ambiente virtual
rm -rf venv
```

### Limpar Dependências
```bash
# Se usou ambiente virtual, apenas remova o diretório venv
# Se instalou globalmente:
pip uninstall flask boto3 pyyaml botocore
```

## Atualizações

### Atualizar Aplicação
```bash
# Fazer backup das configurações (se houver)
cp config.ini config.ini.bak

# Atualizar código
git pull origin main

# Atualizar dependências
pip install -r requirements.txt --upgrade

# Reiniciar aplicação
python app.py
```

---

**🚀 Instalação concluída com sucesso!**
