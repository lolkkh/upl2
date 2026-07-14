FROM python:3.12-alpine3.20

WORKDIR /app

COPY . .

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
    unzip

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

RUN pip3 install --no-cache-dir --upgrade pip setuptools && \
    pip3 install --no-cache-dir -r sainibots.txt && \
    python3 -m pip install --no-cache-dir -U yt-dlp

RUN chmod +x start.sh

ENV PYTHONUNBUFFERED=1

CMD ["sh", "start.sh"]
