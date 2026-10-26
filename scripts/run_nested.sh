#!/usr/bin/env bash
# Runs emulator with a startup script and a custom VFS.
python -m src.main \
    --vfs vfs/default.xml \
    --script scripts/startup.sh \
    --debug
