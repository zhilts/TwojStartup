#!/usr/bin/env sh

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
$SCRIPT_DIR/init.sh
. ${SCRIPT_DIR}/venv/bin/activate
python $SCRIPT_DIR/build_report.py "$@"