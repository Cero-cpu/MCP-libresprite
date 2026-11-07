#!/usr/bin/env bash
DIR="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")" && pwd)"
cd "$DIR"

# Asegurar acceso a las librerías instaladas en el sistema (mcp, PIL, etc.)
export PYTHONPATH="/usr/lib/python3.14/site-packages:$DIR:$PYTHONPATH"

# Usar el Python del venv de MCP (que tiene mcp instalado) o python3 del sistema
if [ -x "/home/cachy/Descargas/MCP/.venv/bin/python" ]; then
    PYTHON="/home/cachy/Descargas/MCP/.venv/bin/python"
else
    PYTHON="python3"
fi

exec "$PYTHON" "$DIR/server.py" "$@"
