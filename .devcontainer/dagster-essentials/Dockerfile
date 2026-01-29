FROM mcr.microsoft.com/devcontainers/python:3.12-bookworm
ENV PYTHONUNBUFFERED 1

COPY --from=ghcr.io/astral-sh/uv:0.6.10 /uv /bin/uv

COPY dagster_university/dagster_essentials /workspace
WORKDIR /workspace

RUN uv pip install -r pyproject.toml --system

# Install Just command runner and related bash completions
RUN <<EOT
    curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --tag 1.42.2 --to /bin
    echo 'eval "$(just --completions bash)"' >> ~/.bash_aliases
EOT