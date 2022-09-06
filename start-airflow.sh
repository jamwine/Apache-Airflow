#!/usr/bin/env bash

echo "Compiling requirements..."
pip-compile requirements.in

echo "Starting Docker Compose..."
docker compose up
