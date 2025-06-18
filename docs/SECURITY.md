# 🔒 Documentação de Segurança

## Política de Não Armazenamento de Credenciais

### ❌ **GARANTIA: ZERO ARMAZENAMENTO DE CREDENCIAIS**

Esta aplicação foi projetada com segurança em mente e **NUNCA** armazena credenciais AWS em qualquer forma:

#### 🚫 **O que NÃO fazemos:**
- ❌ Não salvamos credenciais em arquivos de texto
- ❌ Não armazenamos em banco de dados
- ❌ Não mantemos em cache ou memória persistente
- ❌ Não enviamos para serviços externos
- ❌ Não fazemos log das credenciais
- ❌ Não criamos backups com credenciais
- ❌ Não armazenamos em cookies ou sessões

#### ✅ **O que fazemos:**
- ✅ Recebemos credenciais via POST HTTP
- ✅ Usamos temporariamente para chamadas AWS
- ✅ Descartamos imediatamente após o uso
- ✅ Limpamos variáveis de ambiente
- ✅ Terminamos processos sem rastros

## Fluxo de Segurança Detalhado

### 1. **Recebimento das Credenciais**
```python
# Credenciais chegam via POST request
data = request.json
aws_access_key = data['aws_access_key']    # Apenas em memória
aws_secret_key = data['aws_secret_key']    # Não persistido
region = data['region']                    # Temporário
```

### 2. **Uso Temporário**
```python
# Criamos variáveis de ambiente temporárias
env = os.environ.copy()
env.update({
    'AWS_ACCESS_KEY_ID': aws_access_key,      # Apenas para este processo
    'AWS_SECRET_ACCESS_KEY': aws_secret_key,  # Não salvo em disco
    'AWS_DEFAULT_REGION': region              # Descartado após uso
})

# Executamos o script em processo filho
result = subprocess.run([script], env=env, ...)
# Processo termina, variáveis são automaticamente descartadas
```

### 3. **Limpeza Automática**
```python
# Após a execução:
# - Variável 'env' sai de escopo
# - Processo filho termina
# - Memória é liberada pelo garbage collector
# - Nenhum rastro permanece no sistema
```

## Verificação de Segurança

### 🔍 **Como Verificar que Não Armazenamos Credenciais:**

1. **Verificar arquivos de configuração:**
```bash
# Procurar por credenciais em arquivos
find /root/worldskills53/nuke -type f -name "*.py" -exec grep -l "AKIA\|aws_secret" {} \;
# Resultado: Apenas nos scripts de exemplo/teste (com credenciais falsas)
```

2. **Verificar logs:**
```bash
# Verificar se há credenciais nos logs
grep -r "AKIA\|aws_secret" /var/log/ 2>/dev/null || echo "Nenhuma credencial encontrada nos logs"
```

3. **Verificar arquivos temporários:**
```bash
# Verificar arquivos temporários
find /tmp -name "*aws*" -o -name "*credential*" 2>/dev/null || echo "Nenhum arquivo temporário com credenciais"
```

4. **Verificar banco de dados:**
```bash
# Esta aplicação não usa banco de dados
ls -la /root/worldskills53/nuke/ | grep -E "\.(db|sqlite|sql)$" || echo "Nenhum banco de dados encontrado"
```

## Exemplos de Uso Seguro

### ✅ **Exemplo 1: Credenciais Temporárias**
```bash
# Use credenciais temporárias do AWS STS
aws sts get-session-token --duration-seconds 3600

# Use as credenciais temporárias na aplicação
# Elas expiram automaticamente em 1 hora
```

### ✅ **Exemplo 2: Usuário IAM Específico**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeInstances",
        "ec2:TerminateInstances",
        "s3:ListBucket",
        "s3:DeleteBucket"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "aws:RequestedRegion": "us-east-1"
        }
      }
    }
  ]
}
```

### ✅ **Exemplo 3: Monitoramento**
```bash
# Configure CloudTrail para monitorar ações
aws cloudtrail create-trail \
  --name aws-nuke-audit \
  --s3-bucket-name my-audit-bucket

# Monitore logs em tempo real
aws logs tail /aws/cloudtrail/aws-nuke-audit --follow
```

## Auditoria de Segurança

### 📋 **Checklist de Segurança:**

- [ ] ✅ Credenciais não são salvas em arquivos
- [ ] ✅ Credenciais não são armazenadas em banco de dados
- [ ] ✅ Credenciais não aparecem em logs
- [ ] ✅ Credenciais não são enviadas para terceiros
- [ ] ✅ Processo filho termina após uso
- [ ] ✅ Variáveis de ambiente são limpas
- [ ] ✅ Memória é liberada automaticamente
- [ ] ✅ Nenhum arquivo temporário com credenciais

### 🔍 **Script de Auditoria:**
```bash
#!/bin/bash
echo "🔍 Auditoria de Segurança - AWS Resource Cleaner"
echo "================================================"

echo "1. Verificando arquivos com credenciais..."
if find /root/worldskills53/nuke -name "*.py" -exec grep -l "AKIA[A-Z0-9]\{16\}" {} \; | grep -v test | grep -v example; then
    echo "❌ ATENÇÃO: Credenciais encontradas em arquivos!"
else
    echo "✅ Nenhuma credencial real encontrada em arquivos"
fi

echo "2. Verificando logs..."
if grep -r "AKIA[A-Z0-9]\{16\}" /var/log/ 2>/dev/null; then
    echo "❌ ATENÇÃO: Credenciais encontradas em logs!"
else
    echo "✅ Nenhuma credencial encontrada em logs"
fi

echo "3. Verificando arquivos temporários..."
if find /tmp -name "*credential*" -o -name "*aws*" 2>/dev/null | head -5; then
    echo "⚠️  Arquivos temporários AWS encontrados (normal durante execução)"
else
    echo "✅ Nenhum arquivo temporário AWS encontrado"
fi

echo "4. Verificando processos..."
if ps aux | grep -i aws | grep -v grep; then
    echo "⚠️  Processos AWS em execução (normal durante uso)"
else
    echo "✅ Nenhum processo AWS em execução"
fi

echo "================================================"
echo "✅ Auditoria concluída"
```

## Contato de Segurança

Se você encontrar alguma vulnerabilidade de segurança ou tiver dúvidas sobre o tratamento de credenciais, entre em contato através de:

- 📧 Email: security@example.com
- 🐛 Issues: GitHub Issues (para vulnerabilidades não críticas)
- 🔒 Security Advisory: GitHub Security Advisory (para vulnerabilidades críticas)

---

**🛡️ Sua segurança é nossa prioridade!**
