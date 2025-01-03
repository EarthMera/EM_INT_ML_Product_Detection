# Base image with CUDA support
FROM nvidia/cuda:12.4.1-devel-ubuntu20.04

# Set working directory
WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive 

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    wget \
    ffmpeg \
    colmap \
    systemd \
    python3-pip \
    python3-dev \
    python3-venv \
    libx11-dev \
    libxi-dev \
    libxrandr-dev \
    libglew-dev \
    libgl1-mesa-dev \
    libglu1-mesa-dev \
    libxcb1-dev \
    libxinerama-dev \
    libxcursor-dev \
    nvidia-container-toolkit \
    --no-install-recommends && \
    ln -sf /usr/bin/python3 /usr/bin/python && \
    rm -rf /var/lib/apt/lists/*

# Upgrade CMake to meet Instant-NGP requirements
RUN wget https://github.com/Kitware/CMake/releases/download/v3.26.4/cmake-3.26.4-linux-x86_64.tar.gz && \
    tar -xvzf cmake-3.26.4-linux-x86_64.tar.gz && \
    mv cmake-3.26.4-linux-x86_64 /opt/cmake && \
    ln -sf /opt/cmake/bin/* /usr/local/bin/ && \
    rm cmake-3.26.4-linux-x86_64.tar.gz

# Upgrade pip and ensure it uses the PyPI index
RUN python3 -m pip install --upgrade pip setuptools wheel && \
    pip config set global.index-url https://pypi.org/simple

# Ensure pip uses PyPI during dependency installation
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --index-url https://pypi.org/simple

# Install PyTorch from its custom index
RUN pip install torch==2.4.1+cu124 torchvision==0.19.1+cu124 torchaudio==2.4.1+cu124 --index-url https://download.pytorch.org/whl/cu124

# Build Instant-NGP's pyngp module
RUN git clone --recursive https://github.com/NVlabs/instant-ngp.git /instant-ngp && \
    cd /instant-ngp && \
    cmake . -B build -DCMAKE_BUILD_TYPE=RelWithDebInfo && \
    cmake --build build --config RelWithDebInfo -j

# Set PYTHONPATH explicitly
ENV PYTHONPATH="/instant-ngp/build"

# Copy application files
COPY . .

# Expose API port
EXPOSE 8000

# Start FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
