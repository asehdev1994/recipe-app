FROM node:20-bookworm-slim

WORKDIR /firebase

RUN apt-get update \
    && apt-get install -y --no-install-recommends openjdk-17-jre-headless \
    && npm install -g firebase-tools \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY firebase.json firestore.rules ./
