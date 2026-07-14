FROM python:3.12-alpine3.20

WORKDIR /app

COPY . .

# 1. Install Build Tools + .NET 8 Runtime (Required for N_m3u8DL-RE) + System Libs
RUN apk add --no-cache \
    gcc libffi-dev musl-dev ffmpeg aria2 make g++ cmake wget unzip jq \
    icu-libs krb5-libs libgcc libstdc++ zlib \
    dotnet8-runtime

# 2. Install Bento4 (mp4decrypt) - Compile from source
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

# 3. Install N_m3u8DL-RE (Safe Download & Verify)
RUN LATEST_URL=$(wget -qO- "https://api.github.com/repos/nilaoda/N_m3u8DL-RE/releases/latest" | jq -r '.assets[] | select(.name | contains("linux-x64")) | .browser_download_url') && \
    echo "🔗 Fetching N_m3u8DL-RE from: $LATEST_URL" && \
    wget -q "$LATEST_URL" -O /tmp/nre-download && \
    if file /tmp/nre-download | grep -qi "zip"; then \
        echo " Extracting ZIP archive..." && \
        unzip -o /tmp/nre-download -d /tmp/nre-extract && \
        mv /tmp/nre-extract/N_m3u8DL-RE /usr/local/bin/; \
    else \
        echo "📥 Moving direct binary..." && \
        mv /tmp/nre-download /usr/local/bin/N_m3u8DL-RE; \
    fi && \
    chmod +x /usr/local/bin/N_m3u8DL-RE && \
    # Verify installation
    /usr/local/bin/N_m3u8DL-RE --version && \
    rm -rf /tmp/nre-download /tmp/nre-extract

# 4. Install Python Dependencies
RUN pip3 install --no-cache-dir --upgrade pip setuptools && \
    pip3 install --no-cache-dir -r sainibots.txt && \
    python3 -m pip install --no-cache-dir -U yt-dlp

# 5. Permissions and Environment Variables
RUN chmod +x start.sh

ENV PYTHONUNBUFFERED=1
# Prevents .NET globalization crashes on Alpine Linux
ENV DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1 

CMD ["sh", "start.sh"]
