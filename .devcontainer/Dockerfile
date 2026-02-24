FROM mcr.microsoft.com/devcontainers/miniconda:1-3

# Install git (needed to clone repo)
RUN apt-get update && apt-get install -y git \
    && rm -rf /var/lib/apt/lists/*

# Copy conda environment
COPY ../environment.yml /tmp/environment.yml

# Update conda and install environment
RUN conda update -n base -c defaults conda -y \
    && conda env update -n base -f /tmp/environment.yml \
    && conda clean -afy

# Install Playwright browsers (ARM compatible)
RUN python -m playwright install --with-deps chromium

# Clone indicators_setup
RUN git clone https://github.com/lauracagigal/indicators_setup.git /opt/ind_setup

# Add to PYTHONPATH safely
ENV PYTHONPATH="/opt/ind_setup:${PYTHONPATH}"