#!/usr/bin/env bash
DIR="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")" && pwd)"
cd "$DIR"

# Priorizar el entorno virtual local autónomo
if [ -x "$DIR/.venv/bin/python" ]; then
    PYTHON="$DIR/.venv/bin/python"
elif [ -x "/home/cachy/Descargas/MCP/.venv/bin/python" ]; then
    PYTHON="/home/cachy/Descargas/MCP/.venv/bin/python"
else
    PYTHON="python3"
fi

export PYTHONPATH="$DIR:$PYTHONPATH"
exec "$PYTHON" "$DIR/server.py" "$@"
