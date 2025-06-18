# AWS Nuke App

![Aws Nuke](/imgs/)

## Descrição

Interface web para o AWS Nuke que permite deletar todos os recursos de uma conta AWS sem precisar de alias da conta. A aplicação usa apenas o Account ID e credenciais AWS fornecidas.

## Principais Correções Implementadas

### ✅ Problema do Alias Resolvido
- Configurado preset `allow-no-alias` para não exigir alias da conta
- Agora funciona apenas com Account ID + credenciais AWS

### ✅ Configuração Corrigida
- Estrutura YAML correta para AWS Nuke v2.25.0
- Filtros no formato adequado com `property`, `type` e `value`
- Feature flags para desabilitar proteção de deleção

### ✅ Validações Adicionadas
- Validação de formato do Account ID (12 dígitos)
- Validação de formato da AWS Access Key (AKIA...)
- Validação de tamanho da Secret Key (40 caracteres)

### ✅ Melhor Tratamento de Erros
- Timeouts configurados (5min dry-run, 30min execução)
- Limpeza automática de arquivos temporários
- Mensagens de erro mais claras

## Como Usar

1. **Instalar dependências:**
   ```bash
   cd src-app
   pip install -r requirements.txt
   ```

2. **Executar a aplicação:**
   ```bash
   python app.py
   ```

3. **Acessar interface:**
   - Abra http://localhost:5000
   - Preencha os campos:
     - AWS Account ID (12 dígitos)
     - AWS Access Key ID
     - AWS Secret Access Key
     - Região AWS

4. **Testar primeiro:**
   - Clique em "Executar Dry-Run" para ver o que seria deletado
   - Analise a saída antes de executar

5. **Executar (CUIDADO!):**
   - Clique em "Executar Nuke" apenas se tiver certeza
   - Confirme na caixa de diálogo

## Configuração de Proteção

Por padrão, a aplicação protege alguns recursos críticos:

```yaml
filters:
  S3Bucket:
    - property: Name
      type: regex
      value: important-.*
  IAMRole:
    - property: RoleName
      value: OrganizationAccountAccessRole
  IAMUser:
    - property: UserName
      value: admin
```

### Para Deletar TUDO (sem proteção):
Remova a seção `filters` do arquivo `src-app/app.py` na função `create_config_file()`.

## Estrutura do Projeto

```
nuke/
├── src-app/           # Aplicação Flask
│   ├── app.py         # Aplicação principal (CORRIGIDA)
│   ├── templates/     # Templates HTML
│   ├── static/        # CSS/JS
│   └── requirements.txt
├── src-nuke/          # Binário AWS Nuke
│   ├── aws-nuke-v2.25.0-linux-amd64
│   └── nuke-config.yml (CORRIGIDA)
└── test_config.py     # Script de teste
```

## Endpoints da API

- `GET /` - Interface web
- `POST /api/dry-run` - Executa dry-run
- `POST /api/execute` - Executa nuke real
- `GET /api/health` - Verifica status da aplicação

## Segurança

⚠️ **ATENÇÃO**: Esta ferramenta pode deletar TODOS os recursos da conta AWS!

- Sempre execute dry-run primeiro
- Mantenha backups importantes
- Use em contas de teste/desenvolvimento
- Nunca use em produção sem extremo cuidado

## Teste da Configuração

Execute o script de teste para verificar se a configuração está correta:

```bash
python test_config.py
```

## Logs e Debug

Para ver logs detalhados, execute com debug:

```bash
python app.py
```

Os logs aparecerão no terminal mostrando todas as requisições e erros.