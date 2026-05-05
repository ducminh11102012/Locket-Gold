#!/bin/bash
cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

./venv/bin/pip install --upgrade pip >/dev/null
./venv/bin/pip install aiohttp requests >/dev/null

echo "🚀 Starting Locket Gold Local Activator..."
./venv/bin/python3 main.py
