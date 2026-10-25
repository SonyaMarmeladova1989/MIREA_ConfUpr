#!/usr/bin/env bash
# Wrapper for the emulator
set -e
python -m src.main "$@"
chmod +x run.sh
