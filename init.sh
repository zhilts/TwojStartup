#!/usr/bin/env sh

VENV="./venv"
if [ ! -d "$VENV" ]; then
  python3 -m venv $VENV
  echo "Installing config files in ${VENV}..."
fi

. $VENV/bin/activate
pip install -r ./requirements.txt
