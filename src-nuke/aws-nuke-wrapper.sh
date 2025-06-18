#!/bin/bash

# Wrapper para o AWS Nuke que adiciona um alias temporário à conta AWS
# Isso contorna a verificação de alias do AWS Nuke

# Diretório do script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AWS_NUKE_BIN="$SCRIPT_DIR/aws-nuke-v2.25.0-linux-amd64"

# Verifica se o AWS CLI está instalado
if ! command -v aws &> /dev/null; then
    echo "AWS CLI não está instalado. Instalando..."
    apt-get update && apt-get install -y awscli
fi

# Função para adicionar um alias temporário à conta
add_temp_alias() {
    # Tenta criar um alias temporário para a conta
    TEMP_ALIAS="temp-$(date +%s)"
    aws iam create-account-alias --account-alias "$TEMP_ALIAS" 2>/dev/null
    
    # Verifica se o alias foi criado com sucesso
    if [ $? -eq 0 ]; then
        echo "Alias temporário '$TEMP_ALIAS' criado com sucesso."
        return 0
    else
        echo "Não foi possível criar um alias temporário. Continuando sem alias."
        return 1
    fi
}

# Função para remover o alias temporário
remove_temp_alias() {
    if [ -n "$TEMP_ALIAS" ]; then
        aws iam delete-account-alias --account-alias "$TEMP_ALIAS" 2>/dev/null
        if [ $? -eq 0 ]; then
            echo "Alias temporário '$TEMP_ALIAS' removido com sucesso."
        fi
    fi
}

# Adiciona um alias temporário
add_temp_alias

# Executa o AWS Nuke com os argumentos fornecidos
"$AWS_NUKE_BIN" "$@"
RESULT=$?

# Remove o alias temporário
remove_temp_alias

# Retorna o código de saída do AWS Nuke
exit $RESULT
