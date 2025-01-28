FROM mcr.microsoft.com/devcontainers/miniconda:1-3

# Instalar SQLite explícitamente
RUN apt-get update && apt-get install -y sqlite3 libsqlite3-dev

# Copiar el archivo environment.yml para configurar el entorno Conda
COPY environment.yml* /tmp/conda-tmp/

# Actualizar el entorno base de Conda si environment.yml está presente
RUN if [ -f "/tmp/conda-tmp/environment.yml" ]; then \
        umask 0002 && /opt/conda/bin/conda env update -n base -f /tmp/conda-tmp/environment.yml; \
    fi && rm -rf /tmp/conda-tmp

# Configurar Python como predeterminado (opcional, en caso de problemas con la versión)
ENV PYTHONUNBUFFERED=1
