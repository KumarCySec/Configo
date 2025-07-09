#!/bin/bash

# Resolve real script location even if symlinked
SOURCE="${BASH_SOURCE[0]}"
while [ -L "$SOURCE" ]; do
  DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"
  SOURCE="$(readlink "$SOURCE")"
  [[ "$SOURCE" != /* ]] && SOURCE="$DIR/$SOURCE"
done
DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"

# Detect Python version
if command -v python3 &>/dev/null; then
    PYTHON=python3
elif command -v python &>/dev/null; then
    PYTHON=python
elif command -v py &>/dev/null; then
    PYTHON=py
else
    echo "Python is not installed. Please install Python 3.x"
    exit 1
fi

# Run main.py from real project directory
$PYTHON "$DIR/main.py" "$@"
