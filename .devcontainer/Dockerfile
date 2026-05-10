# Imagem base oficial do VS Code para Python
# Inclui git, curl, zsh e utilitários comuns
FROM mcr.microsoft.com/devcontainers/python:3.13

# Instala o uv (gerenciador de dependências do projeto)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Adiciona uv ao PATH para todos os terminais do container
ENV PATH="/root/.cargo/bin:/home/vscode/.cargo/bin:$PATH"

# (Opcional) Instala ferramentas de terminal úteis
RUN apt-get update && apt-get install -y \
    htop \
    && rm -rf /var/lib/apt/lists/*
