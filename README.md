# AWS Resource Cleaner

![AWS Resource Cleaner](/imgs/app.png)

## Descrição

Interface web para limpar todos os recursos de uma conta AWS sem precisar de alias da conta. A aplicação usa apenas o Account ID e credenciais AWS fornecidas.

## Principais Recursos

### ✅ Limpeza Completa de Recursos
- Deleta todos os recursos da conta AWS
- Não exige alias da conta
- Funciona apenas com Account ID + credenciais AWS

### ✅ Interface Amigável
- Interface web intuitiva
- Modo escuro/claro
- Visualização em tempo real do progresso

### ✅ Validações de Segurança
- Validação de formato do Account ID (12 dígitos)
- Validação de formato da AWS Access Key (AKIA...)
- Validação de tamanho da Secret Key (40 caracteres)

### ✅ Tratamento de Erros
- Timeouts configurados (5min dry-run, 30min execução)
- Limpeza automática de arquivos temporários
- Mensagens de erro claras

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

## Recursos Protegidos

Por padrão, a aplicação protege alguns recursos críticos:

- Usuário IAM "admin"
- Role IAM "OrganizationAccountAccessRole"
- Recursos com tags específicas

## Estrutura do Projeto

```
nuke/
├── src-app/           # Aplicação Flask
│   ├── app.py         # Aplicação principal
│   ├── aws_resource_cleaner.py  # Script de limpeza de recursos
│   ├── templates/     # Templates HTML
│   ├── static/        # CSS/JS
│   └── requirements.txt
└── src-nuke/          # Binários e scripts auxiliares
```

## Endpoints da API

- `GET /` - Interface web
- `POST /api/dry-run` - Executa simulação
- `POST /api/execute` - Executa limpeza real
- `GET /api/health` - Verifica status da aplicação

## Segurança

⚠️ **ATENÇÃO**: Esta ferramenta pode deletar TODOS os recursos da conta AWS!

- Sempre execute dry-run primeiro
- Mantenha backups importantes
- Use em contas de teste/desenvolvimento
- Nunca use em produção sem extremo cuidado

## Logs e Debug

Para ver logs detalhados, execute com debug:

```bash
python app.py
```

Os logs aparecerão no terminal mostrando todas as requisições e erros.
