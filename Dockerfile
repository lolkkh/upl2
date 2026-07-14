FROM python:3.12-alpine3.20

WORKDIR /app

COPY . .

# 1. Basic tools + .NET runtime dependencies for Alpine
RUN apk add --no-cache \
    gcc \
    libffi-dev \
    musl-dev \
    ffmpeg \
    aria2 \
    make \
    g++ \
    cmake \
    wget \
    unzip \
    icu-libs \
    krb5-libs \
    libgcc \
    libstdc++ \
    zlib

# 2. Install Bento4 (mp4decrypt)
RUN wget -q https://github.com/axiomatic-systems/Bento4/archive/v1.6.0-639.zip && \
    unzip v1.6.0-639.zip && \
    cd Bento4-1.6.0-639 && \
    mkdir build && \
    cd build && \
    cmake .. && \
    make -j$(nproc) && \
    cp mp4decrypt /usr/local/bin/ && \
    cd /app && \
    rm -rf Bento4-1.6.0-639 v1.6.0-639.zip

# 3. Install N_m3u8DL-RE (Stable Release Fetcher)
RUN apk add --no-cache jq && \
    LATEST_URL=$(wget -qO- "https://api.github.com/repos/nilaoda/N_m3u8DL-RE/releases/latest" | jq -r '.assets[] | select(.name | contains("linux-x64")) | .browser_download_url') && \
    echo "Downloading from: $LATEST_URL" && \
    wget -q "$LATEST_URL" -O /tmp/nre-download && \
    if file /tmp/nre-download | grep -q "Zip archive"; then \
        unzip /tmp/nre-download -d /tmp/nre-extract && \
        mv /tmp/nre-extract/N_m3u8DL-RE /usr/local/bin/; \
    else \
        mv /tmp/nre-download /usr/local/bin/N_m3u8DL-RE; \
    fi && \
    chmod +x /usr/local/bin/N_m3u8DL-RE && \
    rm -rf /tmp/nre-download /tmp/nre-extract && \
    apk del jq

# 4. Install Python Dependencies
RUN pip3 install --no-cache-dir --upgrade pip setuptools && \
    pip3 install --no-cache-dir -r sainibots.txt && \
    python3 -m pip install --no-cache-dir -U yt-dlp

# 5. Permissions and Environment Variables
RUN chmod +x start.sh

ENV PYTHONUNBUFFERED=1
# This prevents .NET globalization errors on Alpine Linux
ENV DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1 

CMD ["sh", "start.sh"]
