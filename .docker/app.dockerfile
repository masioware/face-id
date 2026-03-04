FROM nvidia/cuda:12.6.2-cudnn-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    INSIGHTFACE_HOME=/app/.insightface

WORKDIR /app

# OS deps (opencv runtime + build toolchain for insightface)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl bash \
    software-properties-common \
    build-essential pkg-config cmake \
    libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Python 3.13
RUN add-apt-repository ppa:deadsnakes/ppa -y \
    && apt-get update && apt-get install -y --no-install-recommends \
    python3.13 python3.13-dev python3.13-venv \
    && rm -rf /var/lib/apt/lists/*

# pip (+ symlinks for convenience)
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.13 \
    && ln -sf /usr/bin/python3.13 /usr/local/bin/python \
    && ln -sf /usr/local/bin/pip3 /usr/local/bin/pip \
    && python -m pip install --no-cache-dir -U pip setuptools wheel

# deps first (cache)
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir \
    --prefer-binary \
    --no-compile \
    --retries 10 --timeout 120 --progress-bar off \
    -r requirements.txt

# app code
COPY app ./app
COPY run.sh ./run.sh
RUN chmod +x ./run.sh

EXPOSE 8081

CMD ["/app/run.sh"]