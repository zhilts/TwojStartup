#!/usr/bin/env sh

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
VENV="${SCRIPT_DIR}/venv"
if [ ! -d "$VENV" ]; then
  python3 -m venv $VENV
  echo "Installing config files in ${VENV}..."
fi

. ${VENV}/bin/activate
pip install -r ${SCRIPT_DIR}/requirements.txt
