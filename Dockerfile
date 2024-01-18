FROM node:current-alpine
WORKDIR /app

RUN apk add --update --no-cache \
    python3 \
    python3-dev \
    musl-dev \
    fluidsynth \ 
    portaudio-dev \ 
    py3-pip \
    curl \
    gcc \
    libressl-dev \ 
    libffi-dev
RUN pip3 install --no-cache --upgrade --break-system-packages pip setuptools && \
    pip3 install --no-cache-dir --break-system-packages poetry
COPY . .
RUN cd src && cd api && cd front && \ 
    npm install && npm run build && cd /app
RUN poetry install
CMD poetry run uvicorn src.api.main:app --host 0.0.0.0
EXPOSE 8000
